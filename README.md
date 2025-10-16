# WB Control Service

## Описание проекта
Проект реализует полный цикл автоматизированного сбора данных по API Wildberries, их загрузку в PostgreSQL-базу и визуализацию ключевых метрик через Metabase.  

Цель - разработать систему автоматического сбора данных по товарам для отслеживания их позиций на страницах поиска, 
чтобы обеспечить эффективный мониторинг и анализ вложений в рекламные кампании, оптимизировать рекламные стратегии для увеличения продаж.

## Структура проекта
<pre>
wb_control_service/
├── .env                        # переменные окружения
├── core/
│   ├── logger.py               # конфигурация логгирования
│   ├── api_client.py           # работа с API, ежечасная загрузка данных (`cron`)
│   ├── db_client.py            # работа с БД
├── services/
│   └── app.py                  # бизнес-логика
├── logs/                       # логи
├── main.py                     # точка входа
├── autocommit.sh               # автокоммит изменений
├── .gitignore
└── README.md                   # документация
</pre>

## Настройка и наполнение сервера (VPS)

- Выбираем VPS с конфигурациями, которые обеспечат работу наших программ.  
  Здесь и далее, если вы работаете под суперпользователем, то команду `sudo` можно не прописывать.  

  - Обновляем все пакеты:
    sudo apt update

  - Устанавливаем pip:
    sudo apt install python3-pip

  - Устанавливаем postgres:
    sudo apt-get -y install postgresql

  - Смена пользователя на postgres:
    su - postgres psql

  - Изменение пароля:
    ALTER USER postgres WITH PASSWORD 'новый_пароль';

  - Выход:
    \q

- Загружаем наш проект на сервер.  

  - Клонируем репозиторий с GitHub:
    git clone https://github.com/KirGo-91/wb_control_service.git

  - Заходим в репозиторий и устанавливаем виртуальное окружение:
    apt install python3.12-venv

  - Создаем папку с виртуальным окружением:
    python3 -m venv venv

  - Активируем виртуальное окружение:
    source venv/bin/activate

  - Устанавливаем зависимости из файла:
    pip install -r requirements.txt

  - Создаем shell-скрипт с автокоммитом:
    sudo nano autocommit.sh

  - Делаем файл исполняемым
    sudo chmod +x autocommit.sh

- Настройка Docker и Metabase.
  Последовательность команд для установки Docker:

  - Обновление списков пакетов:
    sudo apt update

  - Установка необходимых пакетов для работы с репозиториями по HTTPS:
    sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

  - Добавление официального GPG-ключа Docker:
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

  - Добавление репозитория Docker в источники apt:
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

  - Обновление списков пакетов с новым репозиторием:
    sudo apt update

  - Установка Docker Engine:
    sudo apt install -y docker-ce docker-ce-cli containerd.io

  - Проверка установки:
    docker --version

- Последовательность команд для установки Metabase в Docker и его настройки:

  - Скачиваем последнюю версию:
    docker pull metabase/metabase:latest

  - Запускаем контейнер с Metabase:
    docker run -d -p 3000:3000 --name metabase metabase/metabase

  - Проверка работы контейнера:
    docker ps -a

  - Удаление контейнера (если понадобится):
    docker rm -f <ID_контейнера>

Для обработки запросов к нашему серверу, а в нашем случае к Metabase, развернутому на нем, необходимо установить Nginx.
Когда пользователь зайдет на сайт, Nginx примет его запрос и поможет показать нужную страницу.

- Сценарий для запуска Metabase + Nginx:
  Metabase в Docker слушает на порту 3000 (в контейнере и проброшенный на хост).
  Nginx слушает порт 80 (или 443 для HTTPS) и проксирует запросы на Metabase.

  - Устанавливаем nginx:
    sudo apt install nginx

  - Создаем (или редактируем) конфигурацию nginx:
    nano /etc/nginx/sites-available/metabase.conf

    server {
      listen 80;

      server_name _;  # или укажите IP сервера, или доменное имя

      location / {
          proxy_pass http://127.0.0.1:3000;
        
          proxy_http_version 1.1;
          proxy_set_header Upgrade $http_upgrade;
          proxy_set_header Connection "upgrade";

          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
    }

  - Активируем конфигурацию nginx:
    sudo ln -s /etc/nginx/sites-available/metabase.conf /etc/nginx/sites-enabled/

  - Проверяем конфигурацию nginx:
    sudo nginx -t

  - Перезапускаем nginx:
    sudo systemctl reload nginx

Открываем в браузере http://IP_ВАШЕГО_СЕРВЕРА/. Должны увидеть интерфейс Metabase.

## Автоматизация  

- На сервере настроены следующие cron-задачи:

  - Ежечасно запускается основной скрипт `main.py`, который собирает данные по API и загружает их в базу данных (используя `app.py` -> `api_client.py` и `db_client.py`).
    Следом синхронизируются локальный (на виртуальном сервере) и удалённый (github) репозитории, чтобы избежать конфликтов при автокоммитах, 
    после чего выполняется автокоммит нового лог-файла на сервере, который пушится в удалённый репозиторий. 
    В crontab создана переменная с токеном от github, который встроен в `autocommit.sh` для аутентификации при пуше:
    ```
    0 * * * * /bin/bash -c 'export GITHUB_TOKEN=<ваш_токен> && 
    cd /root/wb_control_service && ./venv/bin/python main.py >> /root/wb_control_service/_logs/cron.log 2>&1 && 
    git pull origin master >> /root/wb_control_service/_logs/gitpull.log 2>&1 && 
    ./autocommit.sh >> /root/wb_control_service/_logs/autocommit.log 2>&1'
    ``` 
  - Ежечасно удаляем лог-файлов, чтобы не захламлять  репозиторий. Оставляем за последние 24 часа
    ```
    5 * * * * find /root/wb_control_service/_logs/ -type f -mtime 1 -delete
    ```
  Все задачи выполняются по московскому времени. Репозиторий остается чистым и синхронизированным.

- Дашборд на Metabase показывает оперативную и аналитическую информацию. Фильтрация предусмотрена по дате и городам.

## Дополнительно
- Все скрипты протестированы и работают стабильно  
- Данные обновляются ежечасно  
- Дашборд находится по [ссылке](http://91.229.8.216:3000/public/dashboard/bd5cafb2-06b9-454f-b3d6-8ece3161d62e).
  Так как сервер арендован временно, то доступа уже может не быть. Поэтому в репозитории имеется pdf-файл с дашбордом.
