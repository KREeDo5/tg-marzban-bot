import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)
from config import BOT_TOKEN, ADMIN_ID, MESSAGES
from marzban_api import MarzbanAPI

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Состояния для ConversationHandler
BROADCAST_MESSAGE, USER_MESSAGE, SELECT_USER = range(3)

class MarzbanBot:
    def __init__(self):
        self.api = MarzbanAPI()
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Настройка обработчиков команд"""

        # Команды для всех пользователей
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("status", self.server_status))
        self.application.add_handler(CommandHandler("myinfo", self.subscription_info))

        # Команды только для админа
        self.application.add_handler(CommandHandler("admin", self.admin_panel))
        self.application.add_handler(CommandHandler("users", self.list_users))

        # Обработчики текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        first_name = update.effective_user.first_name

        welcome_text = f"👋 Привет, {first_name}!\n\n{MESSAGES['start']}"

        if user_id == ADMIN_ID:
            keyboard = [['📊 Статус сервера', '📋 Моя подписка'],
                       ['👥 Все пользователи', '🆘 Помощь']]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                welcome_text + "\n\n" + MESSAGES['admin_welcome'],
                reply_markup=reply_markup
            )
        else:
            keyboard = [['📊 Статус сервера', '📋 Моя подписка'], ['🆘 Помощь']]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup
            )

    async def server_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статус сервера"""
        status = self.api.get_server_status()

        message = (
            f"📊 <b>Статус сервера</b>\n\n"
            f"🖥️ CPU: {status['cpu_usage']}%\n"
            f"💾 Память: {status['memory_usage']}%\n"
            f"📶 Трафик: {status['network_usage']}\n"
            f"👥 Пользователей: {status['total_users']}\n"
            f"⚡ Активных: {status['active_users']}\n"
            f"⏰ Аптайм: {status['uptime']}"
        )

        await update.message.reply_text(message, parse_mode='HTML')

    async def subscription_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Информация о подписке пользователя"""
        user_id = update.effective_user.id
        user_info = self.api.get_user(user_id)

        message = (
            f"📋 <b>Ваша подписка</b>\n\n"
            f"👤 Имя: {user_info['username']}\n"
            f"📅 Создана: {user_info['created_at']}\n"
            f"📅 Истекает: {user_info['expire']}\n"
            f"📊 Использовано: {user_info['used_traffic']}\n"
            f"📈 Лимит: {user_info['data_limit']}\n"
            f"🔧 Статус: {user_info['status']}"
        )

        await update.message.reply_text(message, parse_mode='HTML')

    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Панель администратора"""
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ Доступ запрещен")
            return

        keyboard = [['📊 Статус сервера', '👥 Все пользователи'],
                   ['📋 Моя подписка', '🆘 Помощь']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            MESSAGES['admin_welcome'],
            reply_markup=reply_markup
        )

    async def list_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Список всех пользователей"""
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ Доступ запрещен")
            return

        users = self.api.get_all_users()

        if not users:
            await update.message.reply_text("❌ Пользователи не найдены")
            return

        message = "👥 <b>Список пользователей:</b>\n\n"
        for user in users:
            message += f"👤 {user['username']} - {user['status']}\n"

        await update.message.reply_text(message, parse_mode='HTML')

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text
        user_id = update.effective_user.id

        if text == '📊 Статус сервера':
            await self.server_status(update, context)
        elif text == '📋 Моя подписка':
            await self.subscription_info(update, context)
        elif text == '👥 Все пользователи' and user_id == ADMIN_ID:
            await self.list_users(update, context)
        elif text == '🆘 Помощь':
            await update.message.reply_text("ℹ️ Доступные команды:\n/start - начать\n/status - статус сервера\n/myinfo - моя подписка\n/admin - админ панель")
        else:
            await update.message.reply_text("❌ Неизвестная команда. Используйте меню или команды.")

def main():
    """Запуск бота"""
    print("🤖 Запуск Marzban Telegram Bot...")
    print("⚠️  Используются MOCK данные для тестирования")

    if not BOT_TOKEN or BOT_TOKEN == "your_test_bot_token_here":
        print("❌ Ошибка: TELEGRAM_API_TOKEN не настроен в .env файле")
        return

    bot = MarzbanBot()
    print("✅ Бот запущен. Нажмите Ctrl+C для остановки.")
    bot.application.run_polling()

if __name__ == '__main__':
    main()