#!/bin/bash

# Переход в директорию проекта
cd /root/wb_control_service || exit

# Добавление всех изменений
git add .

# Создание коммита с текущей датой и временем
git commit -m "autocommit $(date '+%Y-%m-%d %H:%M')" || echo "No changes to commit"

# Отправка изменений в удалённый репозиторий
git push https://$GITHUB_TOKEN@github.com/KirGo-91/wb_control_service.git
