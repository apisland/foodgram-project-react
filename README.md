![foodgram_workflow](https://github.com/apisland/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

- Link: http://84.201.159.88/

# Проект: Foodgram (Продуктовый помощник)
Дипломный проект Яндекс.Практикум

## Описание
Foodgram это ресурс для публикации рецептов.
Пользователи могут создавать свои рецепты, читать рецепты других пользователей, подписываться на интересных авторов,
добавлять лучшие рецепты в избранное, а также создавать и скачивать список покупок


## Запуск проекта:
- Клонировать репозиторий:
```
git@github.com:apisland/foodgram-project-react.git
```
```
cd backend/foodgram
```
- Создать виртуальное окружение:
```
python -m venv env или python3 -m venv env
```
```
source env/Scripts/activate или . env/bin/activate
```
- установить зависимости из файла **requirements.txt**:
```
python3 -m pip install --upgrade pip
```
```
pip install -r backend/foodgram/requirements.txt
```

- Из директории **infra/:**
-  Запустить проект в контейнере
```
docker-compose up -d --build
```
- Выполнить миграции:
```
sudo docker-compose exec backend python manage.py migrate
```
- Загрузить CSV файлы в базу данных из __foodgram-project-react\backend\foodgram\data__ используя скрипт (при наличии файлов *.csv):
```
sudo docker-compose exec backend python manage.py load_ingredients
```
и
```
sudo docker-compose exec backend python manage.py load_tags
```

- Создать суперпользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser
```
- Собрать статику:
```
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
Если проект разворачивается на Ubuntu и статика не подгрузилась,
необходимо сделать следующее:
При запущенных контейнерах запустить команду
```
docker ps
```
Найти <container_id> для контейнера nginx, затем выполнить последовательно команды:
```
sudo docker exec -it <CONTAINER ID> /bin/sh
ls
cd /var/html/
ls -la /var/html/
```
Если у nginx нет прав на использование папки static, то добавляем эти права:
```
chmod a+rx /var/html/static/
ls -la /var/html/
exit
```
- Копируем файл с базами данных из папки /infra в папку /app (при наличии файла БД *.json):
```
docker cp dump.json <id контенера backend>:/app
```
- Команда для заполнения БД:
```
sudo docker-compose exec backend python manage.py loaddata dump.json
```
- Остановить проект в контейнере:
```
sudo docker-compose down -v
```
- Шаблон для наполнения файла .env:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
DEBUG=False
SECRET_KEY=<...>
ALLOWED_HOSTS=<...>
```
- учетные данные для проверки:
```
e-mail: admin@admin.ru
password: cfqqwwql
```
## Проект выполнен:
[Valentin Klimov](https://github.com/apisland)
