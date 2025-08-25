import logging
import asyncio
from datetime import time  # Исправляем импорт

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from shared import (
    CLIENT_BOT_TOKEN,
    MESSAGES,
    MarzbanAPI,
    get_client_keyboard,
    get_configs_message,
    get_subscription_message,
    get_commands_message
)

from shared.file_broadcast import broadcast_manager

from shared.buttons import (
    CLIENT_BUTTON_CONFIGS,
    CLIENT_BUTTON_SUBSCRIPTION,
    CLIENT_BUTTON_COMMANDS,
    BUTTON_RESTART,
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
        # Правильная инициализация Application с JobQueue
        self.application = Application.builder().token(CLIENT_BOT_TOKEN).build()

        self.CLIENT_BUTTON_CONFIGS = CLIENT_BUTTON_CONFIGS
        self.CLIENT_BUTTON_SUBSCRIPTION = CLIENT_BUTTON_SUBSCRIPTION
        self.CLIENT_BUTTON_COMMANDS = CLIENT_BUTTON_COMMANDS
        self.CLIENT_BUTTON_RESTART = BUTTON_RESTART
        self.CLIENT_TRAFFIC_RESET = CLIENT_TRAFFIC_RESET

        self.setup_handlers()
        self.setup_jobs()  # Настраиваем задачи после инициализации

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("restart", self.restart_bot))
        self.application.add_handler(CommandHandler("my_configs", self.user_configs))
        self.application.add_handler(CommandHandler("my_info", self.subscription_info))
        self.application.add_handler(CommandHandler("reset_traffic", self.reset_traffic))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

    def setup_jobs(self):
        """Настройка фоновых задач"""
        # Проверка рассылок каждые 30 секунд
        self.application.job_queue.run_repeating(
            self.check_broadcasts,
            interval=30.0,
            first=10.0,
            name="check_broadcasts"
        )
        # Очистка старых рассылок каждый день в 3:00
        self.application.job_queue.run_daily(
            self.cleanup_old_broadcasts,
            time=time(hour=3, minute=0),
            days=(0, 1, 2, 3, 4, 5, 6),
            name="cleanup_broadcasts"
        )

    async def cleanup_old_broadcasts(self, context: ContextTypes.DEFAULT_TYPE):
        try:
            broadcast_manager.cleanup_old_broadcasts(days=1)
            print("✅ Очистка старых рассылок завершена")
        except Exception as e:
            print(f"❌ Ошибка очистки рассылок: {e}")

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
                f"✅ {message}\n\n",
                reply_markup=ReplyKeyboardMarkup(get_client_keyboard(), resize_keyboard=True)
            )
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
        message = get_configs_message(user_data)
        await update.message.reply_text(message, parse_mode='HTML')

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
            BUTTON_RESTART: self.restart_bot,
            CLIENT_TRAFFIC_RESET: self.reset_traffic,
        }.get(text, lambda u, c: u.message.reply_text(MESSAGES['unknown_command']))(update, context)

    async def check_broadcasts(self, context: ContextTypes.DEFAULT_TYPE):
        """Фоновая задача проверки новых рассылок"""
        try:
            broadcasts = broadcast_manager.get_pending_broadcasts()
            if not broadcasts:
                return

            print(f"🚀 Начинаем обработку {len(broadcasts)} рассылок")

            for file_path, broadcast_data in broadcasts:
                message = broadcast_data['message']
                admin_id = broadcast_data['admin_id']

                print(f"📨 Обрабатываем рассылку от admin_{admin_id}")

                # Отправляем сообщение всем пользователям
                sent_count = await self.deliver_broadcast(message)
                print(f"✅ Доставлено {sent_count} сообщений")

                # Помечаем как обработанную
                broadcast_manager.mark_as_processed(file_path)

        except Exception as e:
            print(f"❌ Ошибка проверки рассылок: {e}")

    async def deliver_broadcast(self, message):
        """Доставка рассылки пользователям"""
        try:
            users = self.api.get_all_users()
            if not users:
                print("❌ Нет пользователей для рассылки")
                return 0
            sent_count = 0
            error_count = 0
            print(f"👥 Начинаем рассылку для {len(users)} пользователей")
            for user in users:
                try:
                    note = user.get('note', '')
                    note_data = self.api.extract_data_from_note(note)
                    telegram_id = note_data.get('telegram_id')
                    if not telegram_id:
                        continue
                    # Отправляем сообщение
                    await self.application.bot.send_message(
                        chat_id=telegram_id,
                        text=f"📢 <b>Уведомление от администратора:</b>\n\n{message}",
                        parse_mode='HTML'
                    )
                    sent_count += 1
                    # Задержка чтобы не превысить лимиты Telegram
                    if sent_count % 10 == 0:  # Каждые 10 сообщений
                        print(f"📤 Отправлено {sent_count} сообщений...")
                        await asyncio.sleep(1)
                    else:
                        await asyncio.sleep(0.1)
                except Exception as e:
                    error_count += 1
                    if error_count < 5:  # Логируем только первые 5 ошибок
                        print(f"⚠️ Ошибка отправки пользователю {user.get('username')}: {e}")
                    continue
            print(f"✅ Рассылка завершена. Успешно: {sent_count}, Ошибок: {error_count}")
            return sent_count
        except Exception as e:
            print(f"❌ Критическая ошибка доставки рассылки: {e}")
            return 0

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