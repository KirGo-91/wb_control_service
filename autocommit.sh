#!/bin/bash

# Переход в директорию проекта
cd /root/marketplace_data_service || exit

# Добавление всех изменений
git add .

# Создание коммита с текущей датой и временем
git commit -m "autocommit $(date '+%Y-%m-%d %H:%M')" || exit

# Отправка изменений в удалённый репозиторий
git push origin master
