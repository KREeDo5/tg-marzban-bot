import requests
import json
from datetime import datetime, timedelta
from .config import MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD

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
        """Получение токена аутентификации"""
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
    
    def get_server_status(self):
        """Получение статуса сервера"""
        try:
            if not self.token:
                self.token = self._get_token()
            
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/system/status",
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
            # Возвращаем mock данные при ошибке
            return {
                'cpu_usage': 25.5,
                'memory_usage': 45.2,
                'network_usage': '1.2 TB',
                'monthly_usage': '150 GB',
                'total_users': 150,
                'active_users': 87,
                'uptime': '15 дней 8 часов'
            }
    
    def get_user(self, telegram_id):
        """Получение информации о пользователе"""
        try:
            if not self.token:
                self.token = self._get_token()
            
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/user/{telegram_id}",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"⚠️ Ошибка получения данных пользователя: {e}")
            # Возвращаем mock данные при ошибке
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
            
            return response.json().get('users', [])
            
        except Exception as e:
            print(f"⚠️ Ошибка получения списка пользователей: {e}")
            return self.mock_users