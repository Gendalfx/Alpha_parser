import os
import re
import feedparser
import requests
from datetime import datetime

# Конфиги из GitHub Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_TOPIC_ID = os.getenv("TELEGRAM_TOPIC_ID")

# RSS-лента Binance Twitter (замени на свою с rss.app)
RSS_URL = "https://rss.app/feeds/BqToAxij0vGj5J4J.xml"

# Файл с последним ID новости
LAST_ID_FILE = "last_id.txt"

# Регулярка для двух шаблонов
PATTERN = re.compile(
    r"Binance Alpha (?:will|is) the first platform to feature ([^(]+) \(([A-Z0-9]+)\).*?(?:on|opening on) ([A-Za-z]+ \d{1,2}(?:st|nd|rd|th)?,? \d{4})?(?:,? at (\d{2}:\d{2}) \(UTC\))?",
    re.IGNORECASE
)

def load_last_id():
    if os.path.exists(LAST_ID_FILE):
        with open(LAST_ID_FILE, "r") as f:
            return f.read().strip()
    return None

def save_last_id(news_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(news_id)

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    # Добавляем message_thread_id только если переменная задана
    if TELEGRAM_TOPIC_ID:
        try:
            payload["message_thread_id"] = int(TELEGRAM_TOPIC_ID)
        except ValueError:
            print("Warning: TELEGRAM_TOPIC_ID не является числом, отправка в тему пропущена.")

    response = requests.post(url, json=payload)
    if not response.ok:
        print(f"Ошибка отправки сообщения: {response.text}")

def main():
    last_id = load_last_id()
    feed = feedparser.parse(RSS_URL)

    for entry in reversed(feed.entries):
        match = PATTERN.search(entry.title)
        if match:
            name, ticker, date, time = match.groups()
            news_id = entry.id

            if last_id == news_id:
                continue  # уже отправлено

            msg = (
                f"🚀 <b>Новый листинг на Binance Alpha!</b>\n"
                f"📌 Проект: <b>{name.strip()} ({ticker})</b>\n"
                f"📅 Дата запуска: <b>{date}</b>\n"
            )
            if time:
                msg += f"⏰ Время (UTC): <b>{time}</b>\n"
            msg += f"🔗 <a href='{entry.link}'>Подробнее</a>"

            send_to_telegram(msg)
            save_last_id(news_id)

if __name__ == "__main__":
    main()
