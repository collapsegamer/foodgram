# Foodgram
Foodgram - приложение, с помощью которого, пользователи могут создавать рецепты, добавлять в избраное, создавать список покупок и подписываться на авторов рецептов.

## Стек технологий

* Django
* Dgango REST
* PostgreSQL
* Nginx
* Docker
* Gunicorn

## Запуск

В папке infra есть пример файла для сборки и запуска docker-compose.yaml.example.  

команда для сборки и запуска  
```
docker compose -f infra/docker-compose.yaml up -d --build
```

Создайте файл .env пример содержимого  
```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram

DB_HOST=db
DB_PORT=5432
SECRET_KEY="ваш_секретный_ключ"
```

Для миграций выполните следующую команду внутри контейнера  
```
docker compose -f docker-compose.yaml exec backend python manage.py migrate
```

Для статики  
```
docker compose -f docker-compose.yaml exec backend python manage.py collectstatic
docker compose -f docker-compose.yaml exec backend cp -r /app/collected_static/. /backend_static/static/
```

Загрузить перечень ингридиентов можно командой  
```
docker compose -f docker-compose.yaml exec backend python manage.py load_ingredients --format csv
```
> Поддерживаемые форматы csv и json.

Создайте админскую учетку командой 
```
docker compose -f docker-compose.yaml exec backend python manage.py createsuperuser
```

В админской панеле создайте тэги.

По адресу http://localhost/api/docs/ находится спецификация API.

