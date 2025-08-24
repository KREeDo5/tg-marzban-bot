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
    CLIENT_BUTTON_STATUS,
    CLIENT_BUTTON_SUBSCRIPTION,
    CLIENT_BUTTON_COMMANDS,
    CLIENT_BUTTON_RESTART
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

        self.CLIENT_BUTTON_STATUS = CLIENT_BUTTON_STATUS
        self.CLIENT_BUTTON_SUBSCRIPTION = CLIENT_BUTTON_SUBSCRIPTION
        self.CLIENT_BUTTON_COMMANDS = CLIENT_BUTTON_COMMANDS
        self.CLIENT_BUTTON_RESTART = CLIENT_BUTTON_RESTART

        self.setup_handlers()

    async def show_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать доступные команды"""
        await update.message.reply_text(get_commands_message(), parse_mode='HTML')

    async def server_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("restart", self.restart_bot))
        self.application.add_handler(CommandHandler("status", self.server_status))
        self.application.add_handler(CommandHandler("myinfo", self.subscription_info))
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
            CLIENT_BUTTON_STATUS: self.server_status,
            CLIENT_BUTTON_SUBSCRIPTION: self.subscription_info,
            CLIENT_BUTTON_COMMANDS: self.show_commands,
            CLIENT_BUTTON_RESTART: self.restart_bot,
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