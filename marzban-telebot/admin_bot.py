import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from shared.config import ADMIN_BOT_TOKEN, ADMIN_ID, MESSAGES
from shared.marzban_api import MarzbanAPI
from shared.keyboards import get_admin_keyboard

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Состояния для ConversationHandler
BROADCAST_MESSAGE = 1

class AdminBot:
    def __init__(self):
        self.api = MarzbanAPI()
        self.application = Application.builder().token(ADMIN_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Только админские команды"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("users", self.list_users))
        # self.application.add_handler(CommandHandler("status", self.server_status))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast_start))
        
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('broadcast', self.broadcast_start)],
            states={
                BROADCAST_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.broadcast_message)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
        
        self.application.add_handler(conv_handler)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start для админа"""
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ Этот бот только для администратора")
            return
        
        reply_markup = ReplyKeyboardMarkup(get_admin_keyboard(), resize_keyboard=True)
        await update.message.reply_text(MESSAGES['admin_welcome'], reply_markup=reply_markup)
    
    async def server_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статус сервера с детальной информацией для админа"""
        if update.effective_user.id != ADMIN_ID:
            return
        
        status = self.api.get_server_status()
        # Более детальная информация для админа
        message = (
            f"📊 <b>Детальный статус сервера</b>\n\n"
            f"🖥️ CPU: {status['cpu_usage']}%\n"
            f"💾 Память: {status['memory_usage']}%\n"
            f"📶 Трафик: {status['network_usage']}\n"
            f"👥 Всего пользователей: {status['total_users']}\n"
            f"⚡ Активных: {status['active_users']}\n"
            f"💤 Неактивных: {status['total_users'] - status['active_users']}\n"
            f"⏰ Аптайм: {status['uptime']}"
        )
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def list_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Список всех пользователей"""
        if update.effective_user.id != ADMIN_ID:
            return
        
        users = self.api.get_all_users()
        
        if not users:
            await update.message.reply_text("❌ Пользователи не найдены")
            return
        
        message = "👥 <b>Список пользователей:</b>\n\n"
        for user in users:
            message += f"👤 {user['username']} - {user['status']} - {user['used_traffic']}/{user['data_limit']}\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def broadcast_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало рассылки"""
        if update.effective_user.id != ADMIN_ID:
            return
        
        await update.message.reply_text(
            "📢 Введите сообщение для рассылки всем пользователям:",
            reply_markup=ReplyKeyboardRemove()
        )
        return BROADCAST_MESSAGE
    
    async def broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка рассылки"""
        if update.effective_user.id != ADMIN_ID:
            return
        
        message = update.message.text
        users = self.api.get_all_users()
        
        success_count = 0
        for user in users:
            if user.get('telegram_id'):
                self.api.send_message_to_user(user['username'], message)
                success_count += 1
        
        reply_markup = ReplyKeyboardMarkup(get_admin_keyboard(), resize_keyboard=True)
        await update.message.reply_text(
            f"✅ Рассылка завершена! Отправлено {success_count} пользователям",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена операции"""
        if update.effective_user.id != ADMIN_ID:
            return
        
        reply_markup = ReplyKeyboardMarkup(get_admin_keyboard(), resize_keyboard=True)
        await update.message.reply_text("Операция отменена", reply_markup=reply_markup)
        return ConversationHandler.END
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений админа"""
        if update.effective_user.id != ADMIN_ID:
            return
        
        text = update.message.text
        
        # if text == '📊 Статус сервера':
        #     await self.server_status(update, context)
        if text == '👥 Все пользователи':
            await self.list_users(update, context)
        elif text == '📢 Рассылка':
            await self.broadcast_start(update, context)
        elif text == '🆘 Помощь':
            await update.message.reply_text("ℹ️ Админские команды:\n/start - панель\n/users - список пользователей\n/status - статус\n/broadcast - рассылка")
        else:
            await update.message.reply_text("❌ Неизвестная команда.")

def main():
    """Запуск админского бота"""
    print("👑 Запуск Admin Bot...")
    
    if not ADMIN_BOT_TOKEN:
        print("❌ Ошибка: ADMIN_BOT_TOKEN не настроен")
        return
    
    bot = AdminBot()
    print("✅ Admin Bot запущен. Нажмите Ctrl+C для остановки.")
    bot.application.run_polling()

if __name__ == '__main__':
    main()