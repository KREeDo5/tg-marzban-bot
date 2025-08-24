import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Admin bot
ADMIN_BOT_TOKEN = os.getenv('ADMIN_BOT_TOKEN')
ADMIN_ID = int(os.getenv('TELEGRAM_ADMIN_ID', '0'))

# Client bot
CLIENT_BOT_TOKEN = os.getenv('CLIENT_BOT_TOKEN')

# Marzban API
MARZBAN_URL = os.getenv('MARZBAN_URL', "http://localhost:8000")
MARZBAN_USERNAME = os.getenv('MARZBAN_USERNAME', "admin")
MARZBAN_PASSWORD = os.getenv('MARZBAN_PASSWORD', "admin")

# Тексты сообщений
MESSAGES = {
    'user_not_found': "❌ Пользователь не найден в системе",
    'unknown_command': "❌ Неизвестная команда",
}