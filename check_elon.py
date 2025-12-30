import feedparser
import requests
import os
import hashlib
import openai


RSS_URL = os.getenv("RSS_URL")
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")


def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

feed = feedparser.parse(RSS_URL)
latest = feed.entries[0]

content = latest.title
link = latest.link
hash_now = hashlib.md5(content.encode()).hexdigest()

if os.path.exists("last.txt"):
    with open("last.txt") as f:
        if f.read() == hash_now:
            exit(0)

with open("last.txt", "w") as f:
    f.write(hash_now)

def analyze(tweet):
    prompt = f"""
你是专门分析 Elon Musk 推文的情报分析 AI。

请输出以下结构化内容：
- 推文类型（情绪 / 产品 / 市场 / 政治 / 玩笑）
- 是否包含潜在信号（是/否 + 理由）
- 可能影响的公司或资产
- 关注度（高 / 中 / 低）

推文内容：
{tweet}
"""

    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
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
