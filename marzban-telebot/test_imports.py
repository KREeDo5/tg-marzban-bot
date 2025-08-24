import telegram
import requests
from dotenv import load_dotenv
import sys

print("✅ Все импорты работают!")
print("Python путь:", sys.executable)
print("Telegram версия:", telegram.__version__)
print("Requests версия:", requests.__version__)