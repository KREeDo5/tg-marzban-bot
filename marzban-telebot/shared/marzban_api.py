import requests
import re
import json
from datetime import datetime, timedelta
from .config import MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD
import requests
import re
from .config import MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD

class MarzbanAPI:
    def __init__(self):
        self.base_url = MARZBAN_URL
        self.token = self._get_token()

    def _get_token(self):
        try:
            response = requests.post(
                f"{self.base_url}/api/admin/token",
                data={"username": MARZBAN_USERNAME, "password": MARZBAN_PASSWORD},
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('access_token')
        except Exception as e:
            print(f"⚠️ Ошибка получения токена: {e}")
            return None

    def get_user(self, telegram_id, telegram_name = None):
        """Поиск пользователя по Telegram ID в Note поле"""
        try:
            if not self.token:
                self.token = self._get_token()
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/users",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            users = response.json().get('users', [])
            for user in users:
                note = user.get('note', '')
                note_data = self.extract_data_from_note(note)
                if note_data.get('telegram_id') == telegram_id:
                    user.update(note_data)
                    return user
                if telegram_name and note_data.get('telegram_name') == telegram_name:
                    user.update(note_data)
                    return user
            return None
        except Exception as e:
            print(f"⚠️ Ошибка поиска пользователя: {e}")
            return None

    def get_server_status(self):
        """Получение статуса сервера"""
        try:
            if not self.token:
                self.token = self._get_token()
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/system",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            return {
                'cpu_usage': data.get('cpu_percent', 0),
                'memory_usage': data.get('memory_percent', 0),
                'network_usage': data.get('total_network', '0 GB'),
                'monthly_usage': data.get('monthly_network', '0 GB'),
                'total_users': data.get('total_users', 0),
                'active_users': data.get('active_users', 0),
                'uptime': data.get('uptime', '0 дней')
            }
        except Exception as e:
            print(f"⚠️ Ошибка получения статуса сервера: {e}")
            return {}

    def extract_data_from_note(self, note_text):
        """Извлечение данных из поля Note"""
        if not note_text:
            return {}

        data = {}

        # Ищем telegram_id:123456789
        tg_id_match = re.search(r'telegram_id:(\d+)', note_text)
        if tg_id_match:
            data['telegram_id'] = int(tg_id_match.group(1))

        # Ищем telegram_name:@username
        tg_name_match = re.search(r'telegram_name:@([a-zA-Z0-9_]+)', note_text)
        if tg_name_match:
            data['telegram_name'] = tg_name_match.group(1)

        # Ищем month_price:400
        price_match = re.search(r'month_price:(\d+)', note_text)
        if price_match:
            data['month_price'] = int(price_match.group(1))
        return data