# Структура проекта CPSS

## Общая структура

```
.
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── core/        # Конфигурация и безопасность
│   │   ├── middleware/  # Middleware (IP tracking)
│   │   ├── models.py    # SQLAlchemy модели
│   │   ├── routers/     # API роутеры
│   │   ├── schemas.py   # Pydantic схемы
│   │   └── database.py  # Настройка БД
│   ├── main.py          # Точка входа
│   ├── requirements.txt # Python зависимости
│   └── Dockerfile
│
├── frontend/            # React Frontend
│   ├── src/
│   │   ├── components/  # React компоненты
│   │   ├── contexts/    # React Context (Auth)
│   │   ├── pages/       # Страницы приложения
│   │   ├── services/    # API клиент
│   │   └── ...
│   ├── package.json
│   └── Dockerfile
│
├── telegram-bot/        # Telegram Bot
│   ├── bot.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── discord-bot/         # Discord Bot
│   ├── bot.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml   # Docker Compose конфигурация
├── .env.example         # Пример переменных окружения
├── README.md            # Основная документация
└── DEPLOYMENT.md        # Руководство по развертыванию
```

## Backend (FastAPI)

### Основные модули

- **main.py** - Точка входа, настройка FastAPI приложения
- **app/core/** - Ядро приложения
  - `config.py` - Конфигурация из переменных окружения
  - `security.py` - JWT, хеширование паролей
- **app/models.py** - SQLAlchemy модели БД
- **app/schemas.py** - Pydantic схемы для валидации
- **app/routers/** - API endpoints
  - `auth.py` - Аутентификация
  - `bots.py` - Управление ботами
  - `presets.py` - Управление пресетами
  - `publish.py` - Публикация контента
  - `queue.py` - Очередь публикаций
  - `sync.py` - Синхронизация каналов

### База данных

Таблицы:
- `users` - Пользователи системы
- `bots_config` - Конфигурация ботов
- `sync_channels` - Каналы для синхронизации
- `sync_messages` - Сообщения в процессе синхронизации
- `presets` - Пресеты публикации
- `media_content` - Загруженные медиафайлы
- `publication_queue` - Очередь публикаций
- `audit_log` - Логи действий

## Frontend (React + TypeScript)

### Структура компонентов

- **pages/** - Основные страницы
  - `Login.tsx` - Авторизация
  - `Dashboard.tsx` - Главная панель
  - `BotConfig.tsx` - Настройка ботов
  - `PresetManager.tsx` - Управление пресетами
  - `Publisher.tsx` - Публикация контента

- **components/** - Переиспользуемые компоненты
  - `Auth/ProtectedRoute.tsx` - Защита маршрутов
  - `Layout/Layout.tsx` - Основной layout
  - `BotConfig/` - Компоненты настройки ботов

- **contexts/** - React Context
  - `AuthContext.tsx` - Контекст аутентификации

- **services/** - API клиент
  - `api.ts` - Axios клиент с interceptors

## Telegram Bot

### Основные функции

- Мониторинг каналов и групп
- Синхронизация сообщений с Discord
- Поддержка медиа (фото, видео, документы)
- Rate limiting
- Health check

## Discord Bot

### Основные функции

- Мониторинг каналов Discord
- Синхронизация сообщений с Telegram
- Обработка редактирования сообщений
- Контроль доступа по ролям
- Поддержка embed и вложений

## Docker

### Сервисы

1. **postgres** - PostgreSQL база данных
2. **redis** - Redis для кеширования/rate limiting
3. **backend** - FastAPI приложение
4. **frontend** - React приложение (Nginx)
5. **telegram-bot** - Telegram бот
6. **discord-bot** - Discord бот

### Volumes

- `postgres_data` - Данные PostgreSQL
- `redis_data` - Данные Redis
- `media_uploads` - Загруженные медиафайлы

## API Endpoints

### Аутентификация
- `POST /api/auth/login` - Вход в систему

### Боты
- `GET /api/bots/status` - Статус ботов
- `POST /api/bots/configure` - Настройка бота
- `GET /api/bots/configure/{platform}` - Получение конфигурации
- `POST /api/bots/health` - Health check (для ботов)

### Пресеты
- `GET /api/presets` - Список пресетов
- `POST /api/presets` - Создание пресета
- `PUT /api/presets/{id}` - Обновление пресета
- `DELETE /api/presets/{id}` - Удаление пресета

### Публикация
- `POST /api/publish/upload` - Загрузка медиа
- `POST /api/publish` - Создание публикации

### Очередь
- `GET /api/queue` - Получение очереди
- `GET /api/queue/{id}` - Получение публикации
- `DELETE /api/queue/{id}` - Удаление из очереди

### Синхронизация
- `GET /api/sync/channels` - Список каналов
- `POST /api/sync/channels` - Создание канала
- `PUT /api/sync/channels/{id}` - Обновление канала
- `DELETE /api/sync/channels/{id}` - Удаление канала
- `POST /api/sync/message` - Синхронизация сообщения (боты)

