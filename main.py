import requests
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

VK_API_TOKEN = os.getenv("VK_API_TOKEN")
TG_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Ключевые слова для оценки постов
KEYWORDS = {
    "нужен корм": 10,
    "помощь": 7,
    "срочно": 5,
    "адрес": 3,
    "перевести": 4,
    "карта": 4,
    "реквизиты": 4,
    "месок": 3,
    "приют": 5,
    "животным": 5,
    "хвостики": 3,
    "замерзают": 4,
    "голодные": 4,
}

# Функция для поиска постов ВКонтакте
def search_vk_posts(query="помощь приют", count=50):
    url = "https://api.vk.com/method/newsfeed.search"
    params = {
        "q": query,
        "count": count,
        "access_token": VK_API_TOKEN,
        "v": "5.154"
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if "response" in data:
        return data["response"].get("items", [])
    return []

# Функция для подсчета баллов поста на основе ключевых слов
def score_post(text):
    score = 0
    text_lower = text.lower()
    for keyword, weight in KEYWORDS.items():
        if keyword in text_lower:
            score += weight
    return score

# Функция для отправки сообщений в Telegram канал
def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

# Основная функция
def main():
    posts = search_vk_posts()
    if not posts:
        print("Нет подходящих постов")
        return

    scored_posts = []
    for post in posts:
        text = post.get("text", "")
        score = score_post(text)
        scored_posts.append((score, text))

    scored_posts.sort(reverse=True, key=lambda x: x[0])
    top_posts = scored_posts[:3]

    for i, (score, text) in enumerate(top_posts, 1):
        message = f"<b>Пост #{i}:</b>\n{text.strip()}"
        send_to_telegram(message)

if __name__ == "__main__":
    main()
