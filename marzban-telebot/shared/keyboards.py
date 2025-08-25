from shared.buttons import (
    CLIENT_BUTTON_CONFIGS,
    CLIENT_BUTTON_SUBSCRIPTION,
    CLIENT_TRAFFIC_RESET,
    CLIENT_BUTTON_COMMANDS,
    ADMIN_BUTTON_BROADCAST,
    BUTTON_RESTART,
)

def get_client_keyboard():
    """Клавиатура для клиентов"""
    return [
        [CLIENT_BUTTON_CONFIGS, CLIENT_BUTTON_SUBSCRIPTION],
        [CLIENT_TRAFFIC_RESET, CLIENT_BUTTON_COMMANDS],
        [BUTTON_RESTART]
    ]

def get_admin_keyboard():
    """Клавиатура для администратора"""
    return [
        [ADMIN_BUTTON_BROADCAST],
        [BUTTON_RESTART]
    ]