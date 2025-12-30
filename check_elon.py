import feedparser
import requests
import os
from openai import OpenAI


RSS_URL = os.getenv("RSS_URL")
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")
WECOM_WEBHOOK = os.getenv("WECOM_WEBHOOK")
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.deepseek.com"
)


def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

feed = feedparser.parse(RSS_URL)
latest = feed.entries[0]

content = latest.title
link = latest.link

def send_wecom(msg):
    if not WECOM_WEBHOOK:
        return
    requests.post(WECOM_WEBHOOK, json={
        "msgtype": "text",
        "text": {"content": msg}})

if os.path.exists("last.txt"):
    with open("last.txt") as f:
        last_link = f.read().strip()
        if last_link == link:
            print("Same tweet, skip")
            exit(0)

with open("last.txt", "w") as f:
    f.write(link)

def analyze(tweet):
    prompt = f"""
你是专门分析 Elon Musk 推文的情报分析 AI。

请输出：
1. 推文类型（情绪 / 产品 / 市场 / 政治 / 玩笑）
2. 是否包含潜在信号（是/否 + 理由）
3. 可能影响的公司或资产
4. 关注度（高 / 中 / 低）

要求：
1. 不要使用Markdown格式，文本输出即可

推文内容：
{tweet}
"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return resp.choices[0].message.content.strip()
    

analysis = analyze(content)

msg = f"""
【Elon Musk 新推文】
{content}

【AI 分析】
{analysis}

原文：
{link}
"""


send(msg)
send_wecom(msg)

