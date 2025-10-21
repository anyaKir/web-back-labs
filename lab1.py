from flask import Blueprint, url_for, request, redirect, render_template
import datetime
lab1 = Blueprint('lab1', __name__)


@lab1.route("/lab1/500")
def error500():
    x = 1 / 0
    return str(x)


@lab1.route("/lab1/400")
def error400():
    return "<h1>400 — Недопустимый запрос (Bad Request)</h1>", 400


@lab1.route("/lab1/401")
def error401():
    return "<h1>401 — Неавторизован (Unauthorized)</h1>", 401


@lab1.route("/lab1/402")
def error402():
    return "<h1>402 — Требуется оплата (Payment Required)</h1>", 402


@lab1.route("/lab1/403")
def error403():
    return "<h1>403 — Доступ запрещён (Forbidden)</h1>", 403


@lab1.route("/lab1/405")
def error405():
    return "<h1>405 — Метод не поддерживается (Method Not Allowed)</h1>", 405


@lab1.route("/lab1/418")
def error418():
    return "<h1>418 — Я — чайник 😰💔 (I'm a teapot)</h1>", 418


@lab1.route("/lab1")
def lab():
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


@lab1.route("/lab1/web")
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


@lab1.route("/lab1/author")
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
        </html>"""


@lab1.route('/lab1/image')
def image():
    path = url_for("static", filename="мем.PNG")
    html = render_template('image.html', path=path)
    return html, 200, {
        "Content-Language": "ru",         
        "X-Student-Name": "Kirdyachkina Anna", 
        "X-Lab-Number": "1"                  
    }

count = 0


@lab1.route('/lab1/counter')
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


@lab1.route('/lab1/reset')
def reset():
     global count
     count=0
     return '''
    <!doctype html>
    <html>
        <body>
            <h1>Счетчик обнулен</h1>
            <a href="/lab1/counter">Вернуться к счетчику</a>
        </body>
    </html>
'''


@lab1.route("/lab1/info")
def info():
    return redirect("/lab1/author")


@lab1.route("/lab1/created")
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
