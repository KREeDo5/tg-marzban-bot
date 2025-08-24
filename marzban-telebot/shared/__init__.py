"""
Пакет shared - общие модули для admin_bot и client_bot
"""

from .config import (
    ADMIN_BOT_TOKEN,
    ADMIN_ID,
    CLIENT_BOT_TOKEN,
    MARZBAN_URL,
    MARZBAN_USERNAME,
    MARZBAN_PASSWORD,
    MESSAGES
)

from .marzban_api import MarzbanAPI
from .keyboards import get_client_keyboard, get_admin_keyboard
from .message_templates import get_server_status_message, get_subscription_message, get_commands_message

# Можно указать что импортируется при from shared import *
__all__ = [
    'ADMIN_BOT_TOKEN',
    'ADMIN_ID',
    'CLIENT_BOT_TOKEN',
    'MARZBAN_URL',
    'MARZBAN_USERNAME',
    'MARZBAN_PASSWORD',
    'MESSAGES',
    'MarzbanAPI',
    'get_client_keyboard',
    'get_admin_keyboard',
    'get_server_status_message',
    'get_subscription_message',
    'get_commands_message'
]

print("✅ Пакет shared загружен")