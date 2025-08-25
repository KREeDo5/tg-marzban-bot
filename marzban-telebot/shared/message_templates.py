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
    time_until_expiry = get_time_until_expiry(expire_date)

    used_traffic = user_data.get('used_traffic', 0)
    formatted_traffic = format_traffic(used_traffic)

    fulltime_used_traffic = user_data.get('lifetime_used_traffic', 0)
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
        f"\n{time_until_expiry}"
    )

    # Добавляем лимит, если он есть
    data_limit = user_data.get('data_limit')
    if data_limit and data_limit != 0:
        message += f"\n📈 Лимит: {format_traffic(data_limit)}"

    # Добавляем информацию о стоимости, если есть
    print(f"Month price: {user_data.get('month_price')}")
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
        "▫️ /my_configs - Мои конфиги\n"
        "▫️ /my_info - Моя подписка\n"
        "▫️ /reset_traffic - Сбросить трафик\n\n"
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

def get_time_until_expiry(expire_date_str):
    """Вычисляет оставшееся время до истечения подписки"""
    if not expire_date_str or expire_date_str == 'Не ограничено':
        return "Неограниченный доступ"

    try:
        # Определяем тип данных и парсим дату истечения
        if isinstance(expire_date_str, int):  # Если это timestamp
            expire_date = datetime.fromtimestamp(expire_date_str)
        elif isinstance(expire_date_str, str):  # Если это строка
            if 'T' in expire_date_str:
                expire_date = datetime.fromisoformat(expire_date_str.replace('Z', ''))
            else:
                expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d")
        else:
            raise ValueError("Неподдерживаемый формат даты")

        current_date = datetime.now()

        print(f"❌❌❌ current_date: {current_date} ❌❌❌")

        # Если подписка уже истекла
        if expire_date < current_date:
            days_passed = (current_date - expire_date).days
            return f"❌ Истекла {days_passed} дней назад"

        # Вычисляем оставшееся время
        time_left = expire_date - current_date
        days_left = time_left.days
        hours_left = time_left.seconds // 3600

        # Форматируем вывод
        if days_left >= 30:
            months = days_left // 30
            days = days_left % 30
            if months == 1:
                return f"⏳ Истекает через: {months} месяц {days} дней"
            elif months in [2, 3, 4]:
                return f"⏳ Истекает через: {months} месяца {days} дней"
            else:
                return f"⏳ Истекает через: {months} месяцев {days} дней"
        elif days_left > 0:
            if days_left in [1, 21, 31]:
                return f"⏳ Истекает через: {days_left} день"
            elif days_left in [2, 3, 4, 22, 23, 24]:
                return f"⏳ Истекает через: {days_left} дня"
            else:
                return f"⏳ Истекает через: {days_left} дней"
        else:
            return f"⏳ Истекает сегодня ({hours_left} часов осталось)"

    except Exception as e:
        print(f"Ошибка вычисления времени: {e}")
        return "Неизвестно"