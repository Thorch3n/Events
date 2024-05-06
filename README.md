# Events

Веб-приложение, внутри которого центры смогут настраивать
расписание мероприятий, регистрировать людей.

Ход установки:
1. Для настройки проекта необходимо установить PostgreSQL `sudo apt-get install postgresql postgresql-contrib`
2. Далее необходимо переключиться на сессию пользователя postrges `sudo su - postgres`
3. После этого запустите консоль Postgres `psql`
4. Создаем новую роль `CREATE ROLE admin WITH LOGIN CREATEDB CREATEROLE;`
5. Задаем пароль новому пользователю `\password имя_роли`
6. Далее создаем базу данных `CREATE DATABASE events;`
7. Выходим из postgres командой `\q`
8. Теперь устанавливаем зависимости `pip install -r requirements.txt`
8. Переходим в папку events `cd events`
9. Вводим команду `python manage.py migrate` для применения миграций
10. Запускаем сервер `python manage.py runserver`