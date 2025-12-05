from flask import Flask, url_for, request, redirect, render_template, abort
import os
import datetime
from lab1 import lab1
from lab2 import lab2
from lab3 import lab3
from lab4 import lab4
from lab5 import lab5
from lab6 import lab6
from lab7 import lab7

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'секретно-секретный-секрет')
app.config['DB_TYPE'] = os.getenv('DB_TYPE', 'postgres')

app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)
app.register_blueprint(lab4)
app.register_blueprint(lab5)
app.register_blueprint(lab6)
app.register_blueprint(lab7)

error_log = []  

@app.errorhandler(404)
def not_found(err):

    ip = request.remote_addr
    url = request.url
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    error_log.append(f"{time} | IP Пользователя: {ip} | URL пользователя: {url}")

    return f'''
    <!doctype html>
    <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>404</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #000000;
                    color: white;
                    text-align: center;
                    padding: 50px;
                }}
                h1 {{
                    font-size: 50px;
                    color: white;
                }}
                p {{
                    font-size: 20px;
                    color: #bbb;
                }}
                .container {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }}
                .container img {{
                    max-width: 400px;
                    margin-top: 30px;
                }}
                a {{
                    text-decoration: none;
                    color: white;
                    font-size: 18px;
                    margin-top: 20px;
                    display: inline-block;
                    padding: 10px 20px;
                    border: 2px solid purple;
                    border-radius: 5px;
                    background-color: #000000;
                }}
                a:hover {{
                    background-color: white;
                    color: purple;
                }}
                .log {{
                    text-align: left;
                    background: #111;
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 30px;
                    font-size: 14px;
                    max-width: 900px;
                    margin-left: auto;
                    margin-right: auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>404 - Упс...</h1>
                <img src="https://i.pinimg.com/736x/d7/88/f0/d788f02acfbfa2c9a83d4f3fa95b3e92.jpg" alt="404 Image">
                <p><b>Ваш IP:</b> {ip}</p>
                <p><b>Дата и время доступа:</b> {time}</p>
                <p><b>Запрошенный адрес:</b> {url}</p>
                <p>Не переживайте, вы можете вернуться на <a href="/">главную страницу</a></p>

                <h2>Полный лог обращений с ошибкой 404</h2>
                <div class="log">
                    {"<br>".join(error_log)}
                </div>
            </div>
        </body>
    </html>
    ''', 404

@app.errorhandler(500)
def internal_error(err):
    return '''
    <!doctype html>
    <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Ошибка 500</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #2b2b2b;
                    color: white;
                    text-align: center;
                    padding: 50px;
                }
                h1 { font-size: 50px; color: red; }
                p { font-size: 22px; }
                a {
                    color: white;
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <h1>500 — Внутренняя ошибка сервера</h1>
            <p>Произошла ошибка при обработке запроса.<br>
               Попробуйте позже или вернитесь на <a href="/">главную страницу</a>.
            </p>
        </body>
    </html>
    ''', 500

@app.route("/")
@app.route("/index")
def index():
    return """<!doctype html>
<html>
    <head>
        <title>НГТУ, ФБ, Лабораторные работы</title>
    </head>
    <body>
        <h1>НГТУ, ФБ, WEB-программирование, часть 2. Список лабораторных</h1>
        <ul>
            <li><a href="/lab1">Первая лабораторная</a></li>
            <li><a href="/lab2">Вторая лабораторная</a></li>
            <li><a href="/lab3/">Третья лабораторная</a></li>
            <li><a href="/lab4/">Четвертая лабораторная</a></li>
            <li><a href="/lab5/">Пятая лабораторная</a></li>
            <li><a href="/lab6/">Шестая лабораторная</a></li>
            <li><a href="/lab7/">Седьмая лабораторная</a></li>
        </ul>
        <hr>
        <footer>
            Кирдячкина Анна Константиновна, ФБИ-32, 3 курс, 2025
        </footer>
    </body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)