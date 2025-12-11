import os
import logging
import asyncio
from typing import Optional
from dotenv import load_dotenv
from telegram import Update, Message, Chat
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
    CommandHandler
)
from telegram.error import TelegramError
import httpx

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is required")


class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_TOKEN).build()
        self.backend_url = BACKEND_URL
        self.rate_limit_cache = {}  # Простой rate limiting
        
        # Регистрация обработчиков
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков сообщений"""
        # Обработчик только для каналов/групп (не личные сообщения)
        message_filter = filters.ChatType.CHANNELS | filters.ChatType.GROUPS
        
        self.application.add_handler(
            MessageHandler(message_filter & ~filters.COMMAND, self.handle_message)
        )
        self.application.add_handler(
            MessageHandler(message_filter & filters.COMMAND, self.handle_command)
        )
        self.application.add_handler(
            CommandHandler("start", self.start_command)
        )
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        if update.effective_chat.type in (Chat.CHANNEL, Chat.GROUP, Chat.SUPERGROUP):
            await update.message.reply_text(
                "Бот для синхронизации контента активирован!\n"
                "Бот работает только в каналах и группах."
            )
        else:
            await update.message.reply_text(
                "Этот бот работает только в каналах и группах.\n"
                "Личные сообщения не обрабатываются."
            )
    
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команд (пропускаем)"""
        pass
    
    async def check_rate_limit(self, chat_id: int) -> bool:
        """Проверка rate limiting"""
        import time
        current_time = time.time()
        
        if chat_id in self.rate_limit_cache:
            last_time, count = self.rate_limit_cache[chat_id]
            if current_time - last_time < 60:  # 1 минута
                if count >= 20:  # Максимум 20 сообщений в минуту
                    return False
                self.rate_limit_cache[chat_id] = (last_time, count + 1)
            else:
                self.rate_limit_cache[chat_id] = (current_time, 1)
        else:
            self.rate_limit_cache[chat_id] = (current_time, 1)
        
        return True
    
    async def get_sync_channels(self) -> list:
        """Получение списка каналов для синхронизации"""
        try:
            async with httpx.AsyncClient() as client:
                # В реальной реализации здесь должен быть токен аутентификации
                # Для упрощения используем прямой вызов
                response = await client.get(f"{self.backend_url}/api/sync/channels")
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error fetching sync channels: {e}")
        return []
    
    async def sync_to_discord(self, message: Message, sync_channel: dict):
        """Синхронизация сообщения в Discord"""
        try:
            # Получение данных сообщения
            message_data = {
                "channel_id": str(message.chat.id),
                "platform": "telegram",
                "platform_message_id": str(message.message_id),
                "content": message.text or message.caption or "",
                "metadata": {
                    "chat_title": message.chat.title,
                    "author": message.from_user.username if message.from_user else None,
                    "date": message.date.isoformat(),
                }
            }
            
            # Если есть медиа
            if message.photo:
                message_data["metadata"]["has_photo"] = True
                # Скачивание фото для передачи в Discord
                file = await message.photo[-1].get_file()
                message_data["metadata"]["photo_file_id"] = file.file_id
            
            if message.video:
                message_data["metadata"]["has_video"] = True
                file = await message.video.get_file()
                message_data["metadata"]["video_file_id"] = file.file_id
            
            if message.document:
                message_data["metadata"]["has_document"] = True
                file = await message.document.get_file()
                message_data["metadata"]["document_file_id"] = file.file_id
            
            # Отправка в backend для синхронизации
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/sync/message",
                    json=message_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Message {message.message_id} synced to Discord")
                else:
                    logger.error(f"Failed to sync message: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error syncing to Discord: {e}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка сообщений из каналов/групп"""
        message = update.effective_message
        
        # Проверка типа чата
        if message.chat.type == Chat.PRIVATE:
            logger.warning(f"Received private message from {message.chat.id}, ignoring")
            return
        
        # Rate limiting
        if not await self.check_rate_limit(message.chat.id):
            logger.warning(f"Rate limit exceeded for chat {message.chat.id}")
            return
        
        # Логирование
        logger.info(
            f"Received message {message.message_id} "
            f"from chat {message.chat.id} ({message.chat.title})"
        )
        
        # Получение настроек синхронизации для этого канала
        sync_channels = await self.get_sync_channels()
        current_channel_sync = None
        
        for sync_channel in sync_channels:
            if (sync_channel.get("channel_id") == str(message.chat.id) and
                sync_channel.get("platform") == "telegram" and
                sync_channel.get("is_active")):
                current_channel_sync = sync_channel
                break
        
        if current_channel_sync:
            # Синхронизация с Discord
            await self.sync_to_discord(message, current_channel_sync)
        else:
            logger.debug(f"No sync configuration for channel {message.chat.id}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ошибок"""
        logger.error(f"Update {update} caused error {context.error}")
    
    async def update_health_status(self):
        """Обновление статуса здоровья бота в backend"""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.backend_url}/api/bots/health",
                    json={"platform": "telegram", "status": "online"},
                    timeout=5.0
                )
        except Exception as e:
            logger.debug(f"Failed to update health status: {e}")
    
    async def health_check_loop(self):
        """Периодическое обновление статуса"""
        while True:
            await asyncio.sleep(60)  # Каждую минуту
            await self.update_health_status()
    
    def run(self):
        """Запуск бота"""
        logger.info("Starting Telegram bot...")
        
        # Запуск health check в фоне
        loop = asyncio.get_event_loop()
        loop.create_task(self.health_check_loop())
        
        # Запуск бота
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()

