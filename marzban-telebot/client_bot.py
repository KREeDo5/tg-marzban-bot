import logging
import asyncio

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from shared import (
    CLIENT_BOT_TOKEN,
    MESSAGES,
    MarzbanAPI,
    get_client_keyboard,
    get_server_status_message,
    get_subscription_message,
    get_commands_message
)

from shared.buttons import (
    CLIENT_BUTTON_CONFIGS,
    CLIENT_BUTTON_SUBSCRIPTION,
    CLIENT_BUTTON_COMMANDS,
    CLIENT_BUTTON_RESTART,
    CLIENT_TRAFFIC_RESET
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class ClientBot:
    def __init__(self):
        self.api = MarzbanAPI()
        self.application = Application.builder().token(CLIENT_BOT_TOKEN).build()

        self.CLIENT_BUTTON_CONFIGS = CLIENT_BUTTON_CONFIGS
        self.CLIENT_BUTTON_SUBSCRIPTION = CLIENT_BUTTON_SUBSCRIPTION
        self.CLIENT_BUTTON_COMMANDS = CLIENT_BUTTON_COMMANDS
        self.CLIENT_BUTTON_RESTART = CLIENT_BUTTON_RESTART
        self.CLIENT_TRAFFIC_RESET = CLIENT_TRAFFIC_RESET

        self.setup_handlers()

    async def show_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать доступные команды"""
        await update.message.reply_text(get_commands_message(), parse_mode='HTML')

    async def reset_traffic(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сбросить трафик пользователя"""
        telegram_id = update.effective_user.id
        telegram_name = update.effective_user.username
        user_data = self.api.get_user(telegram_id, telegram_name)
        if not user_data:
            await update.message.reply_text(
                MESSAGES['user_not_found'],
            )
            return

        username = user_data.get('username')

        # Отправляем сообщение о начале сброса
        reset_message = await update.message.reply_text(
            "🔄 Сбрасываем трафик...",
            reply_markup=ReplyKeyboardRemove()
        )

        # Сохраняем ID сообщения для последующего обновления
        context.chat_data['last_reset_message_id'] = reset_message

        # Выполняем сброс трафика
        success, message = self.api.reset_user_traffic(username)

        if success:
            # Обновляем сообщение об успехе
            await update.message.reply_text(
                f"✅ {message}\n\n"
                f"Трафик пользователя {username} был сброшен.",
                reply_markup=ReplyKeyboardMarkup(get_client_keyboard(), resize_keyboard=True)
            )

            # Показываем обновленную информацию о подписке
            await asyncio.sleep(1)
            await self.subscription_info(update, context)
        else:
            # Обновляем сообщение об ошибке
            await update.message.reply_text(
                f"❌ {message}",
                reply_markup=ReplyKeyboardMarkup(get_client_keyboard(), resize_keyboard=True)
            )

    async def subscription_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Информация о подписке"""
        telegram_id = update.effective_user.id
        telegram_name = update.effective_user.username
        user_data = self.api.get_user(telegram_id, telegram_name)
        if not user_data:
            await update.message.reply_text(
                MESSAGES['user_not_found'],
            )
            return
        message = get_subscription_message(user_data)
        await update.message.reply_text(message, parse_mode='HTML')

    async def user_configs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статус сервера для клиентов"""
        telegram_id = update.effective_user.id
        telegram_name = update.effective_user.username
        user_data = self.api.get_user(telegram_id, telegram_name)
        if not user_data:
            await update.message.reply_text(
                MESSAGES['user_not_found'],
            )
            return
        message = get_server_status_message(user_data)
        await update.message.reply_text(message, parse_mode='HTML')

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("restart", self.restart_bot))
        self.application.add_handler(CommandHandler("my_configs", self.user_configs))
        self.application.add_handler(CommandHandler("my_info", self.subscription_info))
        self.application.add_handler(CommandHandler("reset_traffic", self.reset_traffic))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        first_name = update.effective_user.first_name
        welcome_text = f"👋 Добро пожаловать, {first_name}!\n\nИспользуй меню для получения информации."
        reply_markup = ReplyKeyboardMarkup(get_client_keyboard(), resize_keyboard=True)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    async def restart_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🔄 Обновляем интерфейс...",
            reply_markup=ReplyKeyboardRemove()
        )
        await asyncio.sleep(0.8)
        await self.start(update, context)

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        await {
            CLIENT_BUTTON_CONFIGS: self.user_configs,
            CLIENT_BUTTON_SUBSCRIPTION: self.subscription_info,
            CLIENT_BUTTON_COMMANDS: self.show_commands,
            CLIENT_BUTTON_RESTART: self.restart_bot,
            CLIENT_TRAFFIC_RESET: self.reset_traffic,
        }.get(text, lambda u, c: u.message.reply_text(MESSAGES['unknown_command']))(update, context)


def main():
    """Запуск клиентского бота"""
    print("🤖 Запуск TG-Marzban-Client Bot...")

    if not CLIENT_BOT_TOKEN:
        print("❌ Ошибка: CLIENT_BOT_TOKEN не настроен")
        return

    bot = ClientBot()
    bot.application.run_polling()

if __name__ == '__main__':
    main()