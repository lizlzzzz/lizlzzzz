import feedparser
import requests
import os
from openai import OpenAI

# ========= 环境变量 =========
RSS_URL = os.getenv("RSS_URL")
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")
WECOM_WEBHOOK = os.getenv("WECOM_WEBHOOK")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.deepseek.com"
)

# ========= 关键词 =========
KEYWORDS = [
    "elon musk",
    "musk",
    "trump",
    "donald trump"
]

def is_relevant(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in KEYWORDS)

# ========= Telegram =========
def send_telegram(msg: str):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg
    })

# ========= 企业微信 =========
def send_wecom(msg: str):
    if not WECOM_WEBHOOK:
        return
    requests.post(WECOM_WEBHOOK, json={
        "msgtype": "text",
        "text": {"content": msg}
    })
    
# ========= 读取link有哪些 =========
processed_links = set()

if os.path.exists("last.txt"):
    with open("last.txt") as f:
        for line in f:
            processed_links.add(line.strip())


# ========= AI 分析 =========
def analyze(content: str) -> str:
    prompt = f"""
System Prompt｜Fortune 新闻极速分析（中文）
你是一个商业与科技新闻分析最强大脑，负责分析 Fortune 的英文新闻内容。
请基于输入新闻正文，只做事实理解与结构化总结，不加入个人观点、不做投资建议、不使用情绪化语言。

按以下格式输出：
一句话结论
用一句话说明这条新闻最重要的事情。
关键事实
列出 3–5 条新闻中最核心、可验证的事实。每条关键事实不超过50字
为什么重要
简要说明这件事在商业、科技或公共层面的意义，仅基于新闻内容。该原因说明不超过100字

约束：
回答使用简体中文
内容必须来自输入文本
不做预测、不扩展、不脑补

新闻内容：
{content}
"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return resp.choices[0].message.content.strip()

# ========= 主逻辑 =========
def main():
    feed = feedparser.parse(RSS_URL)
    new_links = []

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        summary = entry.summary

        # 1. 关键词过滤
        if not is_relevant(title):
            continue

        # 2. 已处理过直接跳过
        if link in processed_links:
            continue

        # 4. 组织内容
        content = f"{title}\n\n{summary}"

        # 5. AI 分析
        analysis = analyze(content)

        msg = f"""
【Fortune Today】
{analysis}

原文：
{link}
"""

        # 6. 推送
        send_telegram(msg)
        send_wecom(msg)

        new_links.append(link)  # ✅ 关键

    if new_links:
        with open("last.txt", "a") as f:
            for l in new_links:
                f.write(l + "\n")

    if not new_links:
        print("No 'Elon Musk' or 'Donald Trump' relevant news found")

if __name__ == "__main__":
    main()

