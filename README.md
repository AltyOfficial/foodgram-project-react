# SPA Проект продуктового помощника FoodGram

## Проект расположен по адресу http://84.201.158.36/ и http://foodgram-alty.ddns.net/

Проект позволяет пользователям создавать свой рецепт, просматривать рецепты других пользователей, подписываться на них, добавлять рецепты в избранное и так же скачивать pdf-файл с ингредиентами, необходимыми для приготовления рецептов, попавших в корзину пользователя

### Следует создать и заполнить файл .env, находящийся в директории "/infra/"
#### Шаблон наполнения env-файла (кавычки убрать)
```sh
SECRE_KEY=*СЕКРЕТНЫЙ КЛЮЧ ДЖАНГО ПРОЕКТА*
DB_ENGINE='DB_ENGINE'
DB_NAME='DB_NAME'
POSTGRES_USER='USER'
POSTGRES_PASSWORD='PASSWORD'
DB_HOST='HOST'
DB_PORT='PORT'
```

## Установка проекта локально
#### Клонировать проект 
```sh
https://github.com/Arkellain/foodgram-project-react.git
```
#### Создать и установить виртуальное окружение
```sh
python -m venv venv
source venv/Scripts/activate
```
#### Перейти в директорию с проектом
```sh
cd backend/
```
#### Установить зависимости
```sh
pip install -r requirements.txt
```
#### Выполнить миграции и запустить веб-сервер
```sh
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Запуск проекта в контейнерах
#### Выполнить команды для запуска контейнеров
```sh
cd /infra/
docker-compose up -d --build
```
- Команда ```-d``` нужна для фоновой работы контейнера
- Файлы конфигурации описаны в ```/infra/nginx.conf``` и ```/infra/docker-compose.yml```, при необходимости изменить

#### После запуска контейнеров выполнить команды миграции, создания суперпользователя и сбора статики
```sh
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input 
```
#### Установить список готовых ингредиентов и тегов
```sh
docker-compose exec web python manage.py load_ingredients
docker-compose exec web python manage.py load_tags
```