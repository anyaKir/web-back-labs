from flask import Flask, url_for, request, redirect, render_template
import datetime
app = Flask(__name__)

error_log = []  

@app.errorhandler(404)
def not_found(err):
    from flask import request
    import datetime

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

@app.route("/lab1/500")
def error500():
    x = 1 / 0
    return str(x)

@app.route("/lab1/400")
def error400():
    return "<h1>400 — Недопустимый запрос (Bad Request)</h1>", 400

@app.route("/lab1/401")
def error401():
    return "<h1>401 — Неавторизован (Unauthorized)</h1>", 401

@app.route("/lab1/402")
def error402():
    return "<h1>402 — Требуется оплата (Payment Required)</h1>", 402

@app.route("/lab1/403")
def error403():
    return "<h1>403 — Доступ запрещён (Forbidden)</h1>", 403

@app.route("/lab1/405")
def error405():
    return "<h1>405 — Метод не поддерживается (Method Not Allowed)</h1>", 405

@app.route("/lab1/418")
def error418():
    return "<h1>418 — Я — чайник 😰💔 (I'm a teapot)</h1>", 418

@app.route("/lab1")
def lab1():
    return """<!doctype html>
<html>
    <head>
        <title>Лабораторная 1</title>
    </head>
    <body>
        <p>
            Flask — фреймворк для создания веб-приложений на языке
            программирования Python, использующий набор инструментов
            Werkzeug, а также шаблонизатор Jinja2. Относится к категории так
            называемых микрофреймворков — минималистичных каркасов
            веб-приложений, сознательно предоставляющих лишь самые базовые возможности.
        </p>
        <hr>
        <a href="/">На главную</a>

        <h2>Список роутов</h2>
        <ul>
            <li><a href="/lab1/400">/lab1/400</a></li>
            <li><a href="/lab1/401">/lab1/401</a></li>
            <li><a href="/lab1/402">/lab1/402</a></li>
            <li><a href="/lab1/403">/lab1/403</a></li>
            <li><a href="/lab1/405">/lab1/405</a></li>
            <li><a href="/lab1/418">/lab1/418</a></li>
            <li><a href="/lab1/500">/lab1/500</a></li>
            <li><a href="/404">/lab1/404</a></li>
            <li><a href="/lab1/web">/lab1/web</a></li>
            <li><a href="/lab1/author">/lab1/author</a></li>
            <li><a href="/lab1/image">/lab1/image</a></li>
            <li><a href="/lab1/counter">/lab1/counter</a></li>
            <li><a href="/lab1/reset">/lab1/reset</a></li>
            <li><a href="/lab1/info">/lab1/info</a></li>
            <li><a href="/lab1/created">/lab1/created</a></li>
        </ul>
    </body>
</html>
"""

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
        </ul>
        <hr>
        <footer>
            Кирдячкина Анна Константиновна, ФБИ-32, 3 курс, 2025
        </footer>
    </body>
</html>
"""
@app.route("/lab1/web")
def web():
    return """<!doctype html> 
        <html>
            <body> 
                <h1>web-сервер на flask</h1>
                <a href = "/lab1/author">author</a>
            </body>    
        </html>""", 200, {
             "X-Server": 'sample',
             'Content-Type': 'text/plain; charset=utf-8'
        }

@app.route("/lab1/author")
def author():
    name = "Кирдячкина Анна Константиновна"
    group = "ФБИ-32"
    faculty = "ФБ"

    return """<!doctype html>
        <html>
            <body>
                <p>Студент: """ + name + """</p>
                <p>Группа: """ + group + """</p>
                <p>Факультет: """ + faculty + """</p>
                <a href = "/lab1/web">web</a>
            </body>
        <html>"""

@app.route('/lab1/image')
def image():
    path = url_for("static", filename="мем.PNG")
    html = render_template('image.html', path=path)
    return html, 200, {
        "Content-Language": "ru",         
        "X-Student-Name": "Kirdyachkina Anna", 
        "X-Lab-Number": "1"                  
    }

count = 0
@app.route('/lab1/counter')
def counter():
    global count
    count +=1
    time = datetime.datetime.today()
    url = request.url
    client_ip = request.remote_addr

    return'''
<!doctype html>
<html>
    <body>
        Сколько раз вы сюда заходили: ''' + str(count) + '''
        <hr>
        Дата и время: ''' + str(time) + '''<br>        
        Запрошенный адрес: ''' + str(url) + '''<br>
        Ваш IP-адрес: '''+ str(client_ip) + '''<br>
        <hr>
        <a href="/lab1/reset">Очистить счетчик</a>
    </body>
</html>
'''

@app.route('/lab1/reset')
def reset():
     global count
     count=0
     return '''
    <!doctype html>
    <html>
        <body>
            <h1>Счетчик обнулен</h1>
            <a href="/lab1/counter">Вернуться к счетчику</a>
        <body>
    </html>
'''

@app.route("/lab1/info")
def info():
    return redirect("/lab1/author")

@app.route("/lab1/created")
def created():
    return '''
<!doctype html>
<html>
    <body>
        <h1>Создано успешно</h1>
        <div><i>что-то создано...</i></div>
    </body>
</html>
''', 201
