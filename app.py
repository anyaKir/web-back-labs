from flask import Flask, url_for, request, redirect, render_template
import datetime
app = Flask(__name__)

@app.errorhandler(404)
def not_found(err):
        return "нет такой страницы", 404

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
            <li><a href="/lab1/web">Первая лабораторная</a></li>
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
             'Content-Type': 'text/html; charset=utf-8'
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
    return render_template('image.html', path=path)
if __name__ == '__main__':
    app.run(debug=True)

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
