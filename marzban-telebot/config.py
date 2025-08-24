import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
ADMIN_ID = int(os.getenv('TELEGRAM_ADMIN_ID', '0'))

# Marzban API (для тестов используем mock данные)
MARZBAN_URL = os.getenv('MARZBAN_URL', "http://localhost:8000")
MARZBAN_USERNAME = os.getenv('MARZBAN_USERNAME', "admin")
MARZBAN_PASSWORD = os.getenv('MARZBAN_PASSWORD', "admin")

# Тексты сообщений
MESSAGES = {
    'start': "👋 Добро пожаловать! Используйте меню для управления вашей подпиской.",
    'admin_welcome': "👑 Панель администратора",
    'user_not_found': "❌ Пользователь не найден в системе",
    'server_status': "📊 Статус сервера",
    'subscription_info': "📋 Информация о подписке",
    'broadcast_start': "📢 Рассылка сообщений пользователям",
    'message_sent': "✅ Сообщение отправлено",
}