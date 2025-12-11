import os
import logging
import asyncio
from typing import Optional
from dotenv import load_dotenv
import discord
from discord.ext import commands
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
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
ALLOWED_ROLES = os.getenv("ALLOWED_ROLES", "").split(",") if os.getenv("ALLOWED_ROLES") else []

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required")


class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(command_prefix="!", intents=intents)
        self.backend_url = BACKEND_URL
        self.allowed_roles = [role.strip() for role in ALLOWED_ROLES if role.strip()]
        self.rate_limit_cache = {}
    
    async def setup_hook(self):
        """Инициализация при запуске"""
        logger.info("Discord bot initialized")
        # Запуск фоновой задачи для health check
        self.loop.create_task(self.health_check_loop())
    
    async def health_check_loop(self):
        """Периодическое обновление статуса"""
        await self.wait_until_ready()
        while not self.is_closed():
            await asyncio.sleep(60)  # Каждую минуту
            await self.update_health_status()
    
    async def update_health_status(self):
        """Обновление статуса здоровья бота в backend"""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.backend_url}/api/bots/health",
                    json={"platform": "discord", "status": "online"},
                    timeout=5.0
                )
        except Exception as e:
            logger.debug(f"Failed to update health status: {e}")
    
    def check_permissions(self, member: discord.Member) -> bool:
        """Проверка разрешений пользователя"""
        if not self.allowed_roles:
            return True  # Если роли не настроены, разрешаем всем
        
        user_roles = [role.name for role in member.roles]
        return any(role in self.allowed_roles for role in user_roles)
    
    async def check_rate_limit(self, channel_id: int) -> bool:
        """Проверка rate limiting"""
        import time
        current_time = time.time()
        
        if channel_id in self.rate_limit_cache:
            last_time, count = self.rate_limit_cache[channel_id]
            if current_time - last_time < 60:  # 1 минута
                if count >= 20:  # Максимум 20 сообщений в минуту
                    return False
                self.rate_limit_cache[channel_id] = (last_time, count + 1)
            else:
                self.rate_limit_cache[channel_id] = (current_time, 1)
        else:
            self.rate_limit_cache[channel_id] = (current_time, 1)
        
        return True
    
    async def get_sync_channels(self) -> list:
        """Получение списка каналов для синхронизации"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/api/sync/channels")
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error fetching sync channels: {e}")
        return []
    
    async def sync_to_telegram(self, message: discord.Message, sync_channel: dict):
        """Синхронизация сообщения в Telegram"""
        try:
            # Получение данных сообщения
            message_data = {
                "channel_id": str(message.channel.id),
                "platform": "discord",
                "platform_message_id": str(message.id),
                "content": message.content or "",
                "metadata": {
                    "channel_name": message.channel.name,
                    "author": str(message.author),
                    "guild_name": message.guild.name if message.guild else None,
                    "date": message.created_at.isoformat(),
                }
            }
            
            # Обработка вложений
            if message.attachments:
                attachments_data = []
                for attachment in message.attachments:
                    attachments_data.append({
                        "filename": attachment.filename,
                        "url": attachment.url,
                        "content_type": attachment.content_type,
                        "size": attachment.size
                    })
                message_data["metadata"]["attachments"] = attachments_data
            
            # Обработка embed
            if message.embeds:
                embeds_data = []
                for embed in message.embeds:
                    embeds_data.append({
                        "title": embed.title,
                        "description": embed.description,
                        "url": embed.url,
                        "color": embed.color.value if embed.color else None
                    })
                message_data["metadata"]["embeds"] = embeds_data
            
            # Отправка в backend для синхронизации
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/sync/message",
                    json=message_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Message {message.id} synced to Telegram")
                else:
                    logger.error(f"Failed to sync message: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error syncing to Telegram: {e}")
    
    async def on_ready(self):
        """Обработчик готовности бота"""
        logger.info(f"{self.user} has connected to Discord!")
        logger.info(f"Bot is in {len(self.guilds)} guilds")
    
    async def on_message(self, message: discord.Message):
        """Обработка новых сообщений"""
        # Игнорируем сообщения от ботов
        if message.author.bot:
            return
        
        # Игнорируем личные сообщения (DM)
        if not message.guild:
            return
        
        # Rate limiting
        if not await self.check_rate_limit(message.channel.id):
            logger.warning(f"Rate limit exceeded for channel {message.channel.id}")
            return
        
        # Проверка разрешений (опционально)
        if not self.check_permissions(message.author):
            logger.debug(f"User {message.author} doesn't have required permissions")
            # Можно добавить уведомление пользователю
        
        # Логирование
        logger.info(
            f"Received message {message.id} "
            f"from channel {message.channel.id} ({message.channel.name})"
        )
        
        # Получение настроек синхронизации для этого канала
        sync_channels = await self.get_sync_channels()
        current_channel_sync = None
        
        for sync_channel in sync_channels:
            if (sync_channel.get("channel_id") == str(message.channel.id) and
                sync_channel.get("platform") == "discord" and
                sync_channel.get("is_active")):
                current_channel_sync = sync_channel
                break
        
        if current_channel_sync:
            # Синхронизация с Telegram
            await self.sync_to_telegram(message, current_channel_sync)
        
        # Обработка команд
        await self.process_commands(message)
    
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Обработка редактирования сообщений"""
        if after.author.bot or not after.guild:
            return
        
        logger.info(f"Message {after.id} edited in channel {after.channel.id}")
        
        # Получение настроек синхронизации
        sync_channels = await self.get_sync_channels()
        
        for sync_channel in sync_channels:
            if (sync_channel.get("channel_id") == str(after.channel.id) and
                sync_channel.get("platform") == "discord" and
                sync_channel.get("is_active")):
                # Синхронизация обновления
                await self.sync_message_edit(after, sync_channel)
                break
    
    async def sync_message_edit(self, message: discord.Message, sync_channel: dict):
        """Синхронизация редактированного сообщения"""
        try:
            message_data = {
                "channel_id": str(message.channel.id),
                "platform": "discord",
                "platform_message_id": str(message.id),
                "content": message.content or "",
                "action": "edit"
            }
            
            async with httpx.AsyncClient() as client:
                await client.put(
                    f"{self.backend_url}/api/sync/message",
                    json=message_data,
                    timeout=30.0
                )
        
        except Exception as e:
            logger.error(f"Error syncing message edit: {e}")
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Обработка ошибок команд"""
        logger.error(f"Command error: {error}")
        if isinstance(error, commands.CommandNotFound):
            return  # Игнорируем неизвестные команды
        await ctx.send(f"Произошла ошибка: {error}")


# Создание и запуск бота
bot = DiscordBot()

if __name__ == "__main__":
    logger.info("Starting Discord bot...")
    bot.run(DISCORD_TOKEN)

