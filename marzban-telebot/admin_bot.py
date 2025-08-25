import logging
import asyncio
import os
import sys
import telegram
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

from shared import (
    ADMIN_BOT_TOKEN,
    ADMIN_ID,
    MarzbanAPI,
    get_admin_keyboard,
)

from shared.buttons import (
    ADMIN_BUTTON_BROADCAST,
    BUTTON_RESTART,
)

from shared.file_broadcast import broadcast_manager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Состояния для ConversationHandler
BROADCAST_MESSAGE, CONFIRM_BROADCAST = range(2)

class AdminBot:
    def __init__(self):
        self.api = MarzbanAPI()
        self.application = Application.builder().token(ADMIN_BOT_TOKEN).build()
        self.setup_handlers()

    async def broadcast_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            return ConversationHandler.END

        await update.message.reply_text(
            "📢 <b>Массовая рассылка</b>\n\n"
            "Введите сообщение для отправки всем пользователям:",
            parse_mode='HTML',
            reply_markup=ReplyKeyboardRemove()
        )
        return BROADCAST_MESSAGE

    async def receive_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение сообщения для рассылки"""
        if update.message.text.startswith('/'):
            await update.message.reply_text("❌ Введите текст сообщения, а не команду")
            return BROADCAST_MESSAGE

        context.user_data['broadcast_message'] = update.message.text
        users_count = self.get_users_count()

        confirm_keyboard = ReplyKeyboardMarkup([['✅ Да', '❌ Нет']], resize_keyboard=True)

        await update.message.reply_text(
            f"📊 <b>Подтверждение рассылки</b>\n\n"
            f"📝 Сообщение:\n<code>{update.message.text}</code>\n\n"
            f"👥 Получателей: {users_count} пользователей\n\n"
            f"✅ Отправить рассылку?",
            parse_mode='HTML',
            reply_markup=confirm_keyboard
        )
        return CONFIRM_BROADCAST

     # Обновляем метод confirm_broadcast
    async def confirm_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение и отправка рассылки"""
        if update.message.text == '❌ Нет':
            await update.message.reply_text(
                "❌ Рассылка отменена",
                reply_markup=ReplyKeyboardMarkup(get_admin_keyboard(), resize_keyboard=True)
            )
            return ConversationHandler.END

        processing_msg = await update.message.reply_text(
            "🔄 Создаем рассылку...",
            reply_markup=ReplyKeyboardRemove()
        )

        message = context.user_data['broadcast_message']

        # Используем файловую систему вместо прямой отправки
        # Передаем update как параметр
        success_count, no_telegram_count, error_count = await self.send_broadcast(message, update)

        try:
            await processing_msg.delete()
        except:
            pass

        result_text = (
            f"✅ <b>Рассылка создана!</b>\n\n"
            f"📊 Статистика:\n"
            f"• Пользователей с Telegram: {success_count}\n"
            f"• Без Telegram: {no_telegram_count}\n"
            f"• Ошибок: {error_count}\n\n"
            f"📝 Сообщение будет доставлено в течение нескольких минут.\n\n"
            f"<code>{message[:100]}...</code>"  # Показываем только начало сообщения
        )

        await update.message.reply_text(
            result_text,
            parse_mode='HTML',
            reply_markup=ReplyKeyboardMarkup(get_admin_keyboard(), resize_keyboard=True)
        )

        context.user_data.clear()
        return ConversationHandler.END

    async def cancel_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "❌ Рассылка отменена",
            reply_markup=ReplyKeyboardMarkup(get_admin_keyboard(), resize_keyboard=True)
        )
        context.user_data.clear()
        return ConversationHandler.END

    async def send_broadcast(self, message, update: Update):
        """Отправка рассылки через файловую систему"""
        try:
            # Создаем файл рассылки
            broadcast_file = broadcast_manager.create_broadcast(
                message,
                update.effective_user.id  # Теперь update передается как параметр
            )

            print(f"✅ Файл рассылки создан: {broadcast_file}")

            # Получаем пользователей для статистики
            users = self.api.get_all_users()
            total_users = len(users) if users else 0

            # Считаем пользователей с telegram_id
            users_with_telegram = 0
            users_without_telegram = 0

            for user in users:
                note = user.get('note', '')
                note_data = self.api.extract_data_from_note(note)
                if note_data.get('telegram_id'):
                    users_with_telegram += 1
                else:
                    users_without_telegram += 1
            print(f"📊 Статистика рассылки: {users_with_telegram} с Telegram, {users_without_telegram} без Telegram")
            return users_with_telegram, users_without_telegram, 0

        except Exception as e:
            print(f"❌ Ошибка создания рассылки: {e}")
            return 0, 0, 1

    def get_users_count(self):
        try:
            users = self.api.get_all_users()
            return len(users) if users else 0
        except Exception as e:
            print(f"⚠️ Ошибка получения пользователей: {e}")
            return "неизвестно"

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start для админа"""
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ Этот бот только для администратора")
            return ConversationHandler.END

        reply_markup = ReplyKeyboardMarkup(get_admin_keyboard(), resize_keyboard=True)
        await update.message.reply_text(
            "👑 <b>Панель администратора</b>\n\n"
            "Доступные команды:\n"
            "• /broadcast - Массовая рассылка\n"
            "• /restart - Перезапустить бота\n\n"
            "Или используйте кнопки ниже:",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        return ConversationHandler.END

    async def restart_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Перезапуск бота для админа"""
        if update.effective_user.id != ADMIN_ID:
            return
        try:
            restart_message = await update.message.reply_text(
                "🔄 Перезапускаем админ-бота...",
                reply_markup=ReplyKeyboardRemove()
            )
            await asyncio.sleep(1)
            try:
                await restart_message.edit_text("✅ Бот перезапущен!")
            except telegram.error.BadRequest:
                await update.message.reply_text("✅ Бот перезапущен!")
            await asyncio.sleep(0.5)
            await self.start(update, context)
        except Exception as e:
            print(f"⚠️ Ошибка при перезапуске бота: {e}")

    def setup_handlers(self):
        """Настройка обработчиков для админского бота"""
        # ConversationHandler для рассылки (ДОЛЖЕН БЫТЬ ПЕРВЫМ)
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('broadcast', self.broadcast_start),
                MessageHandler(filters.Regex(f'^{ADMIN_BUTTON_BROADCAST}$'), self.broadcast_start)
            ],
            states={
                BROADCAST_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_broadcast_message)
                ],
                CONFIRM_BROADCAST: [
                    MessageHandler(filters.Regex('^(✅ Да|❌ Нет)$'), self.confirm_broadcast)
                ]
            },
            fallbacks=[
                CommandHandler('cancel', self.cancel_broadcast),
                CommandHandler('start', self.cancel_broadcast)
            ],
            allow_reentry=True
        )

        self.application.add_handler(conv_handler)

        # Команды
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("restart", self.restart_bot))

        # Общий обработчик текста (ПОСЛЕДНИМ)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений админа"""
        if update.effective_user.id != ADMIN_ID:
            return

        text = update.message.text

        if text == ADMIN_BUTTON_BROADCAST:
            await self.broadcast_start(update, context)
        elif text == BUTTON_RESTART:
            await self.restart_bot(update, context)
        else:
            await update.message.reply_text(
                "❌ Неизвестная команда\n\n"
                "Используйте:\n"
                "• /broadcast - для рассылки\n"
                "• /restart - для перезапуска\n"
                "• Или кнопки меню",
                reply_markup=ReplyKeyboardMarkup(get_admin_keyboard(), resize_keyboard=True)
            )

def main():
    """Запуск админского бота"""
    print("👑 Запуск Admin Bot...")

    if not ADMIN_BOT_TOKEN:
        print("❌ Ошибка: ADMIN_BOT_TOKEN не настроен")
        return

    try:
        bot = AdminBot()
        print("✅ Admin Bot запущен")
        bot.application.run_polling()
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()