#!/bin/bash
# Скрипт для автоматического обновления проекта с git и пересборки Docker контейнеров

set -e  # Остановка при ошибках

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Путь к проекту (измените на ваш путь)
PROJECT_DIR="${1:-$HOME/cpss}"

echo -e "${GREEN}=== Обновление проекта CPSS ===${NC}"
echo "Директория проекта: $PROJECT_DIR"

# Переход в директорию проекта
cd "$PROJECT_DIR" || {
    echo -e "${RED}Ошибка: Не удалось перейти в директорию $PROJECT_DIR${NC}"
    exit 1
}

# Сохранение локальных изменений (если есть)
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}Обнаружены локальные изменения, сохраняю в stash...${NC}"
    git stash push -m "Auto-stash before update $(date +%Y-%m-%d_%H-%M-%S)"
fi

# Удаление неотслеживаемых файлов, которые могут конфликтовать
if [ -f "frontend/package-lock.json" ] && ! git ls-files --error-unmatch frontend/package-lock.json >/dev/null 2>&1; then
    echo -e "${YELLOW}Удаляю неотслеживаемый package-lock.json...${NC}"
    rm -f frontend/package-lock.json
fi

# Получение обновлений из git
echo -e "${GREEN}Получение обновлений из git...${NC}"
if ! git pull; then
    echo -e "${RED}Ошибка при выполнении git pull${NC}"
    exit 1
fi

# Остановка контейнеров
echo -e "${GREEN}Остановка Docker контейнеров...${NC}"
docker compose down || true

# Пересборка контейнеров
echo -e "${GREEN}Пересборка Docker контейнеров...${NC}"
if docker compose build --no-cache; then
    echo -e "${GREEN}Сборка завершена успешно${NC}"
else
    echo -e "${RED}Ошибка при сборке контейнеров${NC}"
    exit 1
fi

# Запуск контейнеров
echo -e "${GREEN}Запуск Docker контейнеров...${NC}"
if docker compose up -d; then
    echo -e "${GREEN}Контейнеры запущены успешно${NC}"
else
    echo -e "${RED}Ошибка при запуске контейнеров${NC}"
    exit 1
fi

# Показать статус
echo -e "${GREEN}=== Статус контейнеров ===${NC}"
docker compose ps

echo -e "${GREEN}=== Обновление завершено успешно! ===${NC}"

