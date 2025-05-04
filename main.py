import requests
import os
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Загружаем переменные окружения из .env файла
load_dotenv()

VK_API_TOKEN = os.getenv("VK_API_TOKEN")
TG_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Ключевые слова и их веса
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
    "помогите": 6,
    "забрать": 5,
    "собака": 5,
    "кошка": 5,
}

# Фильтрация по городу и времени
CITIES = ["Москва", "Санкт-Петербург"]  # Список городов, которые хочешь отслеживать
MAX_POST_AGE_DAYS = 14  # Макс. возраст постов в днях

# Функция для поиска постов ВКонтакте
def search_vk_posts(query="помощь приют", count=50, cities=CITIES):
    url = "https://api.vk.com/method/newsfeed.search"
    posts = []

    for city in cities:
        params = {
            "q": query + " " + city,  # Добавляем город к запросу
            "count": count,
            "access_token": VK_API_TOKEN,
            "v": "5.154"
        }

        resp = requests.get(url, params=params)
        data = resp.json()

        # Логируем ответы от API
        print(f"Запрос к VK для города {city}: {resp.url}")
        print(f"Ответ от VK: {data}")

        if "response" in data:
            posts += data["response"].get("items", [])

    # Отфильтровываем посты, которые старше двух недель
    two_weeks_ago = datetime.now() - timedelta(days=MAX_POST_AGE_DAYS)
    posts = [post for post in posts if datetime.fromtimestamp(post["date"]) > two_weeks_ago]

    # Логируем оставшиеся посты после фильтрации
    print(f"После фильтрации по времени: {len(posts)} постов")

    return posts

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
        scored_posts.append((score, text, post.get("date", 0)))

    # Сортируем по баллам
    scored_posts.sort(reverse=True, key=lambda x: x[0])

    # Отбираем топ 3 поста
    top_posts = scored_posts[:3]

    # Отправляем топ 3 поста в Telegram
    for i, (score, text, date) in enumerate(top_posts, 1):
        # Форматируем сообщение с информацией о посте
        message = f"<b>Пост #{i} (баллы: {score}):</b>\n{text.strip()}\n\n" \
                  f"<i>Дата: {datetime.fromtimestamp(date).strftime('%d.%m.%Y %H:%M')}</i>"
        send_to_telegram(message)

if __name__ == "__main__":
    main()
