from datetime import datetime
"""
Шаблоны сообщений для бота
"""
def get_configs_message(user_data):
    if not user_data or 'proxies' not in user_data:
        return "❌ Конфигурации не найдены"

    proxies = user_data.get('proxies', {})
    inbounds = user_data.get('inbounds', {})
    links = user_data.get('links', [])

    message = "🇫🇮 <b>Ваши конфигурации:</b>\n\n"

    # Протоколы с их emoji
    protocol_emojis = {
        'vless': '🚀',
        'vmess': '🟢',
        'shadowsocks': '🌀',
        'trojan': '🟠',
    }

    # Выводим каждый протокол
    for protocol, config in proxies.items():
        if protocol in inbounds and inbounds[protocol]:
            emoji = protocol_emojis.get(protocol, '🔹')
            message += f"{emoji} <b>{protocol.upper()}</b>\n"

            # Детали конфигурации
            if protocol == 'vless':
                message += f"   └ UUID: <code>{config.get('id')}</code>\n"
                if config.get('flow'):
                    message += f"   └ Flow: <code>{config.get('flow')}</code>\n"

            elif protocol == 'shadowsocks':
                message += f"   └ Метод: <code>{config.get('method')}</code>\n"
                message += f"   └ Пароль: <code>{config.get('password')}</code>\n"

            message += f"   └ Порт: <code>{get_port_from_links(links, protocol)}</code>\n"
            message += f"   └ Inbounds: {', '.join(inbounds[protocol])}\n\n"

    # Конфиги для копирования
    if links:
        message += "📎 <b>Конфигурации для быстрой настройки клиента:</b>\n\n"
        for i, link in enumerate(links, 1):
            # Определяем тип протокола по конфигу
            protocol_type = get_protocol_from_link(link)
            emoji = protocol_emojis.get(protocol_type, '🔗')
            message += f"{emoji} <code>{link}</code>\n\n"
        message += "<i>Нажмите на ссылку для копирования и вставьте в поддерживаемый клиент</i>\n\n"

    # # QR код и подписка
    # subscription_url = user_data.get('subscription_url')
    # if subscription_url:
    #     full_sub_url = f"https://your-domain.com{subscription_url}"
    #     message += f"📡 <b>Подписка:</b>\n<code>{full_sub_url}</code>\n\n"

    return message

def get_protocol_from_link(link):
    """Определяет протокол по ссылке"""
    if link.startswith('vless://'):
        return 'vless'
    elif link.startswith('vmess://'):
        return 'vmess'
    elif link.startswith('ss://'):
        return 'shadowsocks'
    elif link.startswith('trojan://'):
        return 'trojan'
    return 'unknown'

def get_port_from_links(links, protocol):
    """Извлекает порт из ссылок"""
    for link in links:
        if get_protocol_from_link(link) == protocol:
            try:
                # Парсим порт из URL
                import urllib.parse
                parsed = urllib.parse.urlparse(link)
                return parsed.port or 'N/A'
            except:
                return 'N/A'
    return 'N/A'

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