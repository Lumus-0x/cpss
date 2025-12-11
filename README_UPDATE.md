# Скрипт автоматического обновления

## Использование

### На сервере (Linux/Raspberry Pi):

1. Скопируйте скрипт `update-and-deploy.sh` на сервер:
```bash
# На вашем компьютере
scp update-and-deploy.sh admin@raspberrypi:~/cpss/
```

2. Сделайте скрипт исполняемым:
```bash
ssh admin@raspberrypi
chmod +x ~/cpss/update-and-deploy.sh
```

3. Запустите скрипт:
```bash
cd ~/cpss
./update-and-deploy.sh
```

Или с указанием пути:
```bash
./update-and-deploy.sh /path/to/cpss
```

### Автоматический запуск при старте системы

Для автоматического обновления при загрузке системы добавьте в crontab:

```bash
crontab -e
```

Добавьте строку (обновление каждый день в 3:00):
```
0 3 * * * /home/admin/cpss/update-and-deploy.sh >> /home/admin/cpss/update.log 2>&1
```

Или при каждой загрузке системы (через systemd):

Создайте файл `/etc/systemd/system/cpss-update.service`:
```ini
[Unit]
Description=CPSS Auto Update
After=network.target

[Service]
Type=oneshot
User=admin
WorkingDirectory=/home/admin/cpss
ExecStart=/home/admin/cpss/update-and-deploy.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Активируйте:
```bash
sudo systemctl enable cpss-update.service
sudo systemctl start cpss-update.service
```

## Что делает скрипт:

1. Сохраняет локальные изменения в stash (если есть)
2. Удаляет конфликтующие неотслеживаемые файлы
3. Выполняет `git pull` для получения обновлений
4. Останавливает Docker контейнеры
5. Пересобирает контейнеры с флагом `--no-cache`
6. Запускает контейнеры
7. Показывает статус контейнеров

