import feedparser
import requests
import os
import hashlib

RSS_URL = os.getenv("RSS_URL")
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

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

send(f"Elon Musk 新推文：\n{content}\n\n{link}")
