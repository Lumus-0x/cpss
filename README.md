# Cross-Platform Sync System (CPSS)

Система для двусторонней синхронизации контента между Telegram и Discord с веб-интерфейсом управления.

## Структура проекта

```
.
├── backend/          # FastAPI приложение
├── frontend/         # React приложение
├── telegram-bot/     # Telegram бот
├── discord-bot/      # Discord бот
├── docker-compose.yml
└── env.example.txt   # Пример конфигурации
```

## Конфигурация и сетевые настройки

### Порты (диапазон 1000-2000)

Система использует порты в диапазоне 1000-2000. Все порты настраиваются через переменные окружения в файле `.env`:

- **FRONTEND_PORT** (по умолчанию: 1800) - Веб-интерфейс
- **BACKEND_PORT** (по умолчанию: 1800) - API Backend  
- **POSTGRES_PORT** (по умолчанию: 1543) - PostgreSQL
- **REDIS_PORT** (по умолчанию: 1637) - Redis

### IP адреса

Настройка IP адресов для привязки сервисов:

- **HOST_IP** - IP для привязки всех сервисов
  - `0.0.0.0` - все интерфейсы (по умолчанию)
  - `78.107.254.30` - внешний IP сервера
  - `192.168.88.50` - локальный IP

### Быстрый старт

1. Создайте файл `.env` на основе примера:
```bash
cp env.example.txt .env
```

2. Отредактируйте `.env` и укажите:
   - Ваши IP адреса (78.107.254.30 / 192.168.88.50)
   - Порты в диапазоне 1000-2000 (по умолчанию уже настроены)
   - Пароли и токены

3. Запустите все сервисы:
```bash
docker-compose up -d
```

4. Откройте браузер:
   - Внешний доступ: http://78.107.254.30:1800
   - Локальный доступ: http://192.168.88.50:1800

## Настройка

### Пример конфигурации для вашего сервера

В файле `.env`:

```env
# Сетевые настройки
HOST_IP=0.0.0.0
FRONTEND_PORT=1800
BACKEND_PORT=1800
POSTGRES_PORT=1543
REDIS_PORT=1637

# CORS для ваших IP
CORS_ORIGINS=http://78.107.254.30:1800,http://192.168.88.50:1800

# Безопасность
ADMIN_PASSWORD=ваш_надежный_пароль
SECRET_KEY=случайная_строка_32_символа

# База данных
DB_USER=cpss_user
DB_PASSWORD=надежный_пароль_БД

# Боты
TELEGRAM_TOKEN=ваш_токен_telegram
DISCORD_TOKEN=ваш_токен_discord
```

### Telegram бот
1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен и добавьте его в `.env` как `TELEGRAM_TOKEN`
3. Добавьте бота в канал/группу с правами администратора

### Discord бот
1. Создайте приложение в [Discord Developer Portal](https://discord.com/developers/applications)
2. Создайте бота и получите токен
3. Добавьте токен в `.env` как `DISCORD_TOKEN`
4. Пригласите бота на сервер с необходимыми разрешениями

## Компоненты

- **Backend**: FastAPI + PostgreSQL + Redis
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Telegram Bot**: python-telegram-bot 20.x
- **Discord Bot**: discord.py 2.0+

## Документация API

После запуска backend доступен по адресу: http://localhost:8000/docs

## Разработка

Для разработки с hot-reload используйте volumes в docker-compose.yml (уже настроены).

## Документация

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Полное руководство по развертыванию
- [NETWORK_CONFIG.md](./NETWORK_CONFIG.md) - Детальная конфигурация сети и портов
- [CONFIGURATION.md](./CONFIGURATION.md) - Руководство по конфигурации переменных окружения
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - Структура проекта

## Основные возможности

- ✅ Двусторонняя синхронизация между Telegram и Discord
- ✅ Веб-интерфейс для управления
- ✅ Система пресетов для публикации
- ✅ Загрузка и публикация медиафайлов
- ✅ Планировщик публикаций
- ✅ Мониторинг статуса ботов
- ✅ Аудит действий

## Структура проекта

- `backend/` - FastAPI приложение с REST API
- `frontend/` - React приложение с TypeScript
- `telegram-bot/` - Бот для Telegram
- `discord-bot/` - Бот для Discord
- `docker-compose.yml` - Конфигурация Docker Compose


