# Руководство по развертыванию CPSS

## Требования

- Docker и Docker Compose
- Минимум 2GB RAM
- 10GB свободного места на диске

## Быстрый старт

### 1. Клонирование и настройка

```bash
# Клонируйте репозиторий (если используется Git)
# или распакуйте архив проекта

cd cpss
```

### 2. Настройка переменных окружения

Скопируйте `env.example.txt` в `.env`:

```bash
cp env.example.txt .env
```

Отредактируйте `.env` и установите необходимые значения:

```env
# --------------------------------------------
# СЕТЕВЫЕ НАСТРОЙКИ
# --------------------------------------------
# IP адрес для привязки сервисов
# 0.0.0.0 - все интерфейсы (рекомендуется)
# 78.107.254.30 - внешний IP
# 192.168.88.50 - локальный IP
HOST_IP=0.0.0.0

# Порты (диапазон 1000-2000)
FRONTEND_PORT=1800      # Веб-интерфейс
BACKEND_PORT=1800       # API Backend
POSTGRES_PORT=1543      # PostgreSQL
REDIS_PORT=1637         # Redis

# CORS - разрешенные источники
CORS_ORIGINS=http://78.107.254.30:1800,http://192.168.88.50:1800

# --------------------------------------------
# БЕЗОПАСНОСТЬ
# --------------------------------------------
ADMIN_PASSWORD=ваш_надежный_пароль
SECRET_KEY=случайная_строка_32_символа

# --------------------------------------------
# БАЗА ДАННЫХ
# --------------------------------------------
DB_USER=cpss_user
DB_PASSWORD=надежный_пароль_БД

# --------------------------------------------
# БОТЫ
# --------------------------------------------
TELEGRAM_TOKEN=токен_от_BotFather
DISCORD_TOKEN=токен_от_Discord_Developer_Portal
```

**Важно:** 
- Не используйте значения по умолчанию в продакшене!
- Все порты должны быть в диапазоне 1000-2000
- Убедитесь, что порты не заняты другими приложениями

### 3. Создание ботов

#### Telegram бот

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `.env` как `TELEGRAM_TOKEN`
5. Добавьте бота в ваш канал/группу как администратора

#### Discord бот

1. Перейдите на [Discord Developer Portal](https://discord.com/developers/applications)
2. Создайте новое приложение
3. Перейдите в раздел "Bot" и создайте бота
4. Скопируйте токен в `.env` как `DISCORD_TOKEN`
5. В разделе "OAuth2" -> "URL Generator":
   - Выберите scope: `bot`
   - Выберите permissions: `Send Messages`, `Read Message History`, `Attach Files`, `Embed Links`
6. Используйте сгенерированный URL для приглашения бота на сервер

### 4. Запуск системы

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### 5. Доступ к системе

После запуска система будет доступна по следующим адресам:

**Внешний доступ (если HOST_IP=0.0.0.0 или 78.107.254.30):**
- Веб-интерфейс: http://78.107.254.30:1800
- API документация: http://78.107.254.30:1800/api/docs
- API: http://78.107.254.30:1800/api

**Локальный доступ:**
- Веб-интерфейс: http://192.168.88.50:1800
- API документация: http://192.168.88.50:1800/api/docs
- API: http://192.168.88.50:1800/api

**Порты по умолчанию (можно изменить в .env):**
- Frontend: 1800
- Backend: 1800
- PostgreSQL: 1543
- Redis: 1637

**Учетные данные:**
- Логин: `admin`
- Пароль: значение из `ADMIN_PASSWORD` в `.env`

## Настройка на Raspberry Pi

### Установка Docker

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo apt install docker-compose -y
```

### Настройка для ограниченных ресурсов

Для Raspberry Pi может потребоваться оптимизация в `docker-compose.yml`:

```yaml
services:
  postgres:
    # Добавьте лимиты памяти
    mem_limit: 512m
    memswap_limit: 512m
  
  redis:
    mem_limit: 128m
    memswap_limit: 128m
  
  backend:
    mem_limit: 512m
    memswap_limit: 512m
```

## Настройка портов и сетевых параметров

### Пользовательские порты

Все порты настраиваются через переменные окружения в `.env`. По умолчанию используются:
- Frontend: 1800
- Backend: 1800  
- PostgreSQL: 1543
- Redis: 1637

Для изменения портов отредактируйте `.env`:

```env
FRONTEND_PORT=1900    # Изменить порт фронтенда
BACKEND_PORT=1900     # Изменить порт бэкенда
POSTGRES_PORT=1543    # Изменить порт PostgreSQL
REDIS_PORT=1637       # Изменить порт Redis
```

**Важно:** Все порты должны быть в диапазоне 1000-2000.

### Привязка к конкретному IP

Если нужно привязать сервисы к конкретному IP:

```env
# Привязка только к внешнему IP
HOST_IP=78.107.254.30

# Или только к локальному
HOST_IP=192.168.88.50

# Все интерфейсы (рекомендуется)
HOST_IP=0.0.0.0
```

### Проверка доступности портов

Перед запуском убедитесь, что порты свободны:

```bash
# Проверка портов
sudo netstat -tulpn | grep -E ':(1543|1637|1800)'
# или
sudo ss -tulpn | grep -E ':(1543|1637|1800)'
```

Если порты заняты, измените их в `.env` на другие значения из диапазона 1000-2000.

## Настройка Reverse Proxy (опционально)

### Nginx

Пример конфигурации для `/etc/nginx/sites-available/cpss`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://78.107.254.30:1800;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://78.107.254.30:1800;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активация:

```bash
sudo ln -s /etc/nginx/sites-available/cpss /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL с Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Резервное копирование

### База данных

```bash
# Создание резервной копии
docker-compose exec postgres pg_dump -U cpss_user cpss > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление
docker-compose exec -T postgres psql -U cpss_user cpss < backup_file.sql
```

### Автоматическое резервное копирование

Создайте скрипт `/usr/local/bin/cpss-backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
mkdir -p $BACKUP_DIR
docker-compose exec -T postgres pg_dump -U cpss_user cpss > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql
# Удаление резервных копий старше 30 дней
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

Добавьте в crontab:

```bash
crontab -e
# Ежедневное резервное копирование в 3:00
0 3 * * * /usr/local/bin/cpss-backup.sh
```

## Мониторинг

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f telegram-bot
docker-compose logs -f discord-bot
```

### Проверка статуса

```bash
docker-compose ps
```

### Использование ресурсов

```bash
docker stats
```

## Обновление

```bash
# Остановка сервисов
docker-compose down

# Обновление кода (если используете Git)
git pull

# Пересборка образов
docker-compose build --no-cache

# Запуск
docker-compose up -d
```

## Решение проблем

### Боты не подключаются

1. Проверьте токены в `.env`
2. Проверьте логи: `docker-compose logs telegram-bot` или `docker-compose logs discord-bot`
3. Убедитесь, что боты добавлены в каналы/серверы с необходимыми правами

### База данных не запускается

1. Проверьте, не используется ли порт из `.env` (по умолчанию 1543): `sudo lsof -i :1543`
2. Проверьте права доступа к volumes: `ls -la`
3. Проверьте логи: `docker-compose logs postgres`
4. Убедитесь, что `POSTGRES_PORT` в `.env` находится в диапазоне 1000-2000

### Frontend не доступен

1. Проверьте, запущен ли контейнер: `docker-compose ps`
2. Проверьте логи: `docker-compose logs frontend`
3. Проверьте порты: `netstat -tulpn | grep :1800` (или ваш `FRONTEND_PORT`)
4. Убедитесь, что порт открыт в firewall:
   ```bash
   # Для Ubuntu/Debian с ufw
   sudo ufw allow 1800/tcp
   
   # Для CentOS/RHEL с firewalld
   sudo firewall-cmd --permanent --add-port=1800/tcp
   sudo firewall-cmd --reload
   ```

### Проблемы с доступом по IP

1. Убедитесь, что `HOST_IP` в `.env` настроен правильно (0.0.0.0 для всех интерфейсов)
2. Проверьте, что IP адрес правильный: `ip addr show` или `ifconfig`
3. Убедитесь, что `CORS_ORIGINS` содержит все необходимые адреса
4. Проверьте firewall настройки сервера

## Поддержка

Для получения помощи и отчетов об ошибках создайте issue в репозитории проекта.

