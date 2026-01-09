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

KEYWORDS = [
    "elon musk",
    "musk",
    "trump",
    "donald trump"
]

def is_relevant(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in KEYWORDS)

##telegram推送
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

##企业微信推送
def send_wecom(msg):
    if not WECOM_WEBHOOK:
        return
    requests.post(WECOM_WEBHOOK, json={
        "msgtype": "text",
        "text": {"content": msg}})

##记录分析过的link
if os.path.exists("last.txt"):
    with open("last.txt") as f:
        last_link = f.read().strip()
        if last_link == link:
            print("Same tweet, skip")
            exit(0)

with open("last.txt", "w") as f:
    f.write(link)

##AI prompt
def analyze(tweet):
    prompt = f"""
System Prompt｜Fortune 新闻极速分析（中文）
你是一个商业与科技新闻分析最强大脑，负责分析 Fortune 的英文新闻内容。
请基于输入新闻正文，只做事实理解与结构化总结，不加入个人观点、不做投资建议、不使用情绪化语言。

按以下格式输出：
一句话结论
用一句话说明这条新闻最重要的事情。
关键事实
列出 3–5 条新闻中最核心、可验证的事实。
为什么重要
简要说明这件事在商业、科技或公共层面的意义，仅基于新闻内容。
事实 vs 观点
区分哪些是客观事实，哪些是被引用人物的观点。

约束：
使用简体中文
内容必须来自输入文本
不做预测、不扩展、不脑补

新闻内容：
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
    


feed = feedparser.parse(RSS_URL)
for entry in feed.entries:
    title = entry.title
    link = entry.link
    description = entry.description

    if not is_relevant(title):
        continue  # 不相关，直接跳过
content = f"{title}/n/n{description}"

analysis = analyze(content)

msg = f"""
【Fortune today】
{content}

【AI 分析】
{analysis}

原文：
{link}
"""


send(msg)
send_wecom(msg)

