from flask import Flask, url_for, request, redirect, render_template
import datetime
app = Flask(__name__)

@app.errorhandler(404)
def not_found(err):
        return "нет такой страницы", 404

@app.route("/")
@app.route("/web")
def web():
    return """<!doctype html> 
        <html>
            <body> 
                <h1>web-сервер на flask</h1>
                <a href = "/author">author</a>
            </body>    
        </html>""", 200, {
             "X-Server": 'sample',
             'Content-Type': 'text/plain; charset=utf-8'
        }

@app.route("/author")
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
                <a href = "/web">web</a>
            </body>
        <html>"""

@app.route('/image')
def image():
    path = url_for("static", filename="мем.PNG")
    return render_template('image.html', path=path)
if __name__ == '__main__':
    app.run(debug=True)

count = 0
@app.route('/counter')
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
    </body>
</html>
'''

@app.route("/info")
def info():
    return redirect("/author")

@app.route("/lab1/created")
def created():
    return '''
<!doctype html>
<html>
    <body>
        <h1>Создано успешно</h1>
        <div><i>что-то создано...</i></div>
    <body>
</html>
''', 201
