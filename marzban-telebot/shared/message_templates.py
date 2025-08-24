"""
Шаблоны сообщений для бота
"""

def get_server_status_message(status_data):
    """Шаблон сообщения со статусом сервера"""
    return (
        f"📊 <b>Статус сервера</b>\n\n"
        f"📶 Расход трафика за всё время: {status_data.get('network_usage', 'N/A')}\n"
        f"📶 Расход трафика за этот месяц: {status_data.get('monthly_usage', 'N/A')}\n"
        f"⏰ Время работы сервера: {status_data.get('uptime', 'N/A')}\n"
        f"👥 Активных пользователей: {status_data.get('active_users', 0)}"
    )

def get_subscription_message(user_data):
    """Шаблон сообщения с информацией о подписке"""
    return (
        f"📋 <b>Ваша подписка</b>\n\n"
        f"👤 Имя: {user_data.get('username', 'N/A')}\n"
        f"📅 Создана: {user_data.get('created_at', 'N/A')}\n"
        f"📅 Истекает: {user_data.get('expire', 'Не ограничено')}\n"
        f"📊 Использовано: {user_data.get('used_traffic', '0')}\n"
        f"📈 Лимит: {user_data.get('data_limit', 'Безлимит')}\n"
        f"🔧 Статус: {user_data.get('status', 'N/A')}"
    )

def get_commands_message():
    """Шаблон сообщения с командами"""
    return (
        "ℹ️ <b>Доступные команды (аналогично кнопкам меню):</b>\n\n"
        "▫️ /start - Начать работу с ботом\n"
        "▫️ /restart - Перезапустить бот\n"
        "▫️ /status - Статус сервера\n"
        "▫️ /myinfo - Моя подписка\n\n"
        "📋 <b>Или используйте кнопки меню ниже:</b>"
    )