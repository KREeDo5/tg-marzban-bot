import requests
import json
from datetime import datetime, timedelta
from config import MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD

class MarzbanAPI:
    def __init__(self):
        self.base_url = MARZBAN_URL
        self.token = self._get_token()
        # Mock данные для тестирования
        self.mock_users = [
            {
                'username': 'user1',
                'telegram_id': 123456789,
                'created_at': '2024-01-15',
                'expire': '2024-12-31',
                'used_traffic': '15.2 GB',
                'data_limit': '100 GB',
                'status': 'active'
            },
            {
                'username': 'user2',
                'telegram_id': 987654321,
                'created_at': '2024-02-20',
                'expire': '2024-11-30',
                'used_traffic': '8.7 GB',
                'data_limit': '50 GB',
                'status': 'active'
            }
        ]

    def _get_token(self):
        """Mock метод получения токена"""
        print("⚠️ Используются mock данные для тестирования")
        return "mock_token"

    def get_user(self, telegram_id):
        """Получение информации о пользователе"""
        # Ищем пользователя в mock данных
        for user in self.mock_users:
            if user['telegram_id'] == telegram_id:
                return user

        # Если пользователь не найден, создаем mock данные
        return {
            'username': f'user_{telegram_id}',
            'telegram_id': telegram_id,
            'created_at': '2024-01-01',
            'expire': '2024-12-31',
            'used_traffic': '25.5 GB',
            'data_limit': '100 GB',
            'status': 'active'
        }

    def get_all_users(self):
        """Получение списка всех пользователей"""
        return self.mock_users

    def get_server_status(self):
        """Получение статуса сервера"""
        # Mock данные сервера
        return {
            'cpu_usage': 25.5,
            'memory_usage': 45.2,
            'network_usage': '1.2 TB',
            'total_users': 150,
            'active_users': 87,
            'uptime': '15 дней 8 часов'
        }

    def send_message_to_user(self, username, message):
        """Mock отправка сообщения"""
        print(f"📨 Сообщение для {username}: {message}")
        return True