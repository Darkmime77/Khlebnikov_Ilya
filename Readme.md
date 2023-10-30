<p align="center">
    <h1 align="center">Система контроллеров через Swagger FastApi</h1>
</p>
<h4>Реализованная функциональность</h4>
<ul>
    <li>Контроллер аккаунтов / Админ контроллер аккаунтов;</li>
    <li>Контроллер оплаты;</li>
    <li>Контроллер транспорта / Админ контроллер транспорта;</li>
    <li>Контроллер аренды / Админ контроллер аренды.</li>
</ul> 

Начало работы
------------
Для запуска вам необходимо установить базу данных postgresql
<ul>
<li>Офф сайт - https://www.postgresql.org/;</li>
<li>Через панель администратора <b>pgAdmin</b> создать сервер;</li>
<li>В файле <b>database.py</b> в строке заменить ссылку на сервер - postgresql://postgres:<b>PASS</b>@localhost/<b>LOGIN</b>
</li>
<li>Установить стек библиотек командой:
</ul>

```
pip install -r requirements.txt
```
Для запуска FastApi ввести команду:

```
uvicorn main:app --reload       
```
После его запуска на сервере должны появиться 3 следующих таблицы
<ul>
<li>Rent;</li>
<li>Transport;</li>
<li>Users.</li>
</ul>
Перейти по сгенерированному адресу http://127.0.0.1:8000/docs.

Первая авторизация
------------
<p>Первый зарегистрированный пользователь по умолчанию становится администратором, для регистрации используйте <b>/api/Account/SignUp</b>.</p>
<p>После регистрации необходимо ввести логин и пароль в <b>/api/Account/login</b>. Система сгенерирует временный токен который будет действовать 30 минут, его можно вводить в основное поле авторизации.</p>
<p>После всех этих шагов вам откроется функционал.</p>
<p><b>При изменении аккаунта система сбросит его активность, это значит что при его изменении необходимо заново запрашивать токен!</b>

РАЗРАБОТЧИК

<h4>Хлебников Илья</h4>