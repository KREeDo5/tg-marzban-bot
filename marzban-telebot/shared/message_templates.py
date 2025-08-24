from datetime import datetime
"""
Шаблоны сообщений для бота
"""

def get_server_status_message(status_data):
    """Шаблон сообщения со статусом сервера"""
    return (
        f"📊 <b>Статус сервера</b>\n\n"
        f"🖥️ CPU: {status_data.get('cpu_usage', 0)}%\n"
        f"💾 Память: {status_data.get('memory_usage', 0)}%\n"
        f"📶 Трафик за всё время: {status_data.get('network_usage', 'N/A')}\n"
        f"📶 Трафик за месяц: {status_data.get('monthly_usage', 'N/A')}\n"
        f"👥 Пользователей: {status_data.get('total_users', 0)}\n"
        f"⚡ Активных: {status_data.get('active_users', 0)}\n"
        f"⏰ Аптайм: {status_data.get('uptime', 'N/A')}"
    )

def get_subscription_message(user_data):
    """Шаблон сообщения с информацией о подписке"""
    created_at = user_data.get('created_at', 'N/A')
    formatted_created_date = format_date(created_at, default="Дата отсутствует")
    expire_date = user_data.get('expire', 'Не ограничено')
    formatted_expire_date = format_date(expire_date)

    used_traffic = user_data.get('used_traffic', 0)
    formatted_traffic = format_traffic(used_traffic)

    fulltime_used_traffic = user_data.get('lifetime_used_traffic', 0)
    print(f"Fulltime used traffic: {fulltime_used_traffic}")
    formatted_fulltime_traffic = format_traffic(fulltime_used_traffic)

    message = (
        f"<b>Ваша подписка</b>\n\n"
        f"🔧 Статус: {user_data.get('status', 'N/A')}\n"
        f"👤 cfg-name: {user_data.get('username', 'N/A')}\n\n"
        f"Дата подключения:\n📅 {formatted_created_date}\n\n"

        f"📊 Расход трафика:\n"
        f"- С момента сброса трафика: {formatted_traffic}\n"
        f"- Всего: {formatted_fulltime_traffic}\n\n"

        f"Подписка доступна до:\n📅 {formatted_expire_date}"
    )

    # Добавляем лимит, если он есть
    data_limit = user_data.get('data_limit')
    if data_limit and data_limit != 0:
        message += f"\n📈 Лимит: {format_traffic(data_limit)}"

    # Добавляем информацию о стоимости, если есть
    month_price = user_data.get('month_price')
    if month_price:
        message += f"\n\n💳 Стоимость: {month_price} руб./месяц"
    return message

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



# def format_traffic(traffic_in_bytes):
#     """Форматирование трафика из байтов в удобный формат (GB)"""
#     if traffic_in_bytes is None or traffic_in_bytes == '0':
#         return "0 B"

#     # Конвертируем байты в гигабайты
#     traffic_in_gb = int(traffic_in_bytes) / (1024 ** 3)
#     # Округляем до двух знаков после запятой
#     return f"{traffic_in_gb:.2f} GB"

def format_traffic(traffic_value):
    """Форматирует трафик в читаемый вид из байт или строки"""
    if not traffic_value:
        return "0 B"
    # Если это число (байты) - конвертируем в читаемый формат
    if isinstance(traffic_value, (int, float)):
        return format_traffic_bytes(traffic_value)
    # # Если это строка вроде "15.2 GB"
    # if isinstance(traffic_value, str):
    #     # Проверяем, является ли строка числом (только цифры)
    #     if traffic_value.isdigit():
    #         return format_traffic_bytes(int(traffic_value))
    #     return traffic_value  # Возвращаем как есть, если это уже форматированная строка
    return "0 B"

def format_traffic_bytes(bytes_value):
    """Форматирует байты в читаемый вид"""
    if bytes_value == 0:
        return "0 B"
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    value = float(bytes_value)

    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    # Форматируем вывод в зависимости от единицы измерения
    if unit_index == 0:  # B
        return f"{int(value)} {units[unit_index]}"
    elif unit_index == 1:  # KB
        return f"{value:.1f} {units[unit_index]}"
    else:  # MB, GB, TB
        return f"{value:.2f} {units[unit_index]}"

def format_date(date_str, default="Не ограничено"):
    """Форматирует дату из строки или timestamp в формат 'день.месяц.год'."""
    if not date_str or date_str == 'N/A':
        return default
    try:
        # Если это строка в формате ISO 8601
        if isinstance(date_str, str):
            parsed_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            return parsed_date.strftime("%d.%m.%Y")
        # Если это timestamp (число)
        elif isinstance(date_str, (int, float)):
            parsed_date = datetime.fromtimestamp(date_str)
            return parsed_date.strftime("%d.%m.%Y")
        else:
            return default
    except (ValueError, TypeError):
        return default