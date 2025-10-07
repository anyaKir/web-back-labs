from flask import Flask, url_for, request, redirect, render_template, abort
import datetime
app = Flask(__name__)

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
            <li><a href="/lab2">Вторая лабораторная</a></li>
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
        </html>"""

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
        </body>
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

@app.route('/lab2/a')
def a():
    return 'без слэша'

@app.route('/lab2/a/')
def a2():
    return 'со слэшем'

flower_list = ['роза', 'тюльпан', 'незабудка', 'ромашка']

@app.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    if flower_id >= len(flower_list):
        abort(404)
    flower = flower_list[flower_id]
    return render_template('flower.html', flower=flower, flower_id=flower_id)

@app.route("/lab2/clear_flowers")
def clear_flowers():
    global flower_list
    flower_list.clear()
    return redirect(url_for('all_flowers'))

@app.route('/lab2/all_flowers')
def all_flowers():
    return render_template('all_flowers.html', flower_list=flower_list)

@app.route('/lab2/add_flower/<name>')
def add_flower(name):
    flower_list.append(name)
    return render_template('add_flower.html', name=name, flower_list=flower_list)


@app.route('/lab2/add_flower/')
def add_flower_no_name():
    return render_template('error400.html'), 400

@app.route('/lab2/calc/')
def calc_default():
    """Перенаправление на калькулятор с значениями по умолчанию"""
    return redirect('/lab2/calc/1/1')

@app.route('/lab2/calc/<int:a>')
def calc_single(a):
    """Перенаправление на калькулятор с одним числом (второе = 1)"""
    return redirect(f'/lab2/calc/{a}/1')

@app.route('/lab2/calc/<int:a>/<int:b>')
def calc(a, b):
    """Калькулятор с двумя числами"""
    return render_template('calc.html', a=a, b=b)

# Список книг
books = [
    {
        'id': 1,
        'title': 'Мастер и Маргарита',
        'author': 'Михаил Булгаков',
        'genre': 'Роман',
        'pages': 480
    },
    {
        'id': 2,
        'title': 'Преступление и наказание',
        'author': 'Фёдор Достоевский',
        'genre': 'Психологический роман',
        'pages': 672
    },
    {
        'id': 3,
        'title': 'Война и мир',
        'author': 'Лев Толстой',
        'genre': 'Эпопея',
        'pages': 1225
    },
    {
        'id': 4,
        'title': '1984',
        'author': 'Джордж Оруэлл',
        'genre': 'Антиутопия',
        'pages': 328
    },
    {
        'id': 5,
        'title': 'Гарри Поттер и философский камень',
        'author': 'Джоан Роулинг',
        'genre': 'Фэнтези',
        'pages': 432
    },
    {
        'id': 6,
        'title': 'Три товарища',
        'author': 'Эрих Мария Ремарк',
        'genre': 'Роман',
        'pages': 480
    },
    {
        'id': 7,
        'title': 'Маленький принц',
        'author': 'Антуан де Сент-Экзюпери',
        'genre': 'Философская сказка',
        'pages': 96
    },
    {
        'id': 8,
        'title': 'Убить пересмешника',
        'author': 'Харпер Ли',
        'genre': 'Роман воспитания',
        'pages': 416
    },
    {
        'id': 9,
        'title': 'Тёмные начала',
        'author': 'Филип Пулман',
        'genre': 'Фэнтези',
        'pages': 448
    },
    {
        'id': 10,
        'author': 'Джон Рональд Руэл Толкин',
        'title': 'Властелин колец: Братство Кольца',
        'genre': 'Фэнтези',
        'pages': 576
    },
    {
        'id': 11,
        'title': 'Анна Каренина',
        'author': 'Лев Толстой',
        'genre': 'Роман',
        'pages': 864
    },
    {
        'id': 12,
        'title': 'Сто лет одиночества',
        'author': 'Габриэль Гарсиа Маркес',
        'genre': 'Магический реализм',
        'pages': 416
    }
]
@app.route('/lab2/books')
def books_list():
    """Список всех книг"""
    return render_template('books.html', books=books)

cats = [
    {
        'id': 1,
        'name': 'Барсик',
        'breed': 'Британская короткошёрстная',
        'description': 'Серый красавец с изумрудными глазами. Очень независимый и умный.',
        'age': 3,
        'color': 'Серый',
        'image': 'cat1.png'
    },
    {
        'id': 2,
        'name': 'Мурка',
        'breed': 'Сиамская',
        'description': 'Элегантная кошка с голубыми глазами. Очень разговорчивая и ласковая.',
        'age': 2,
        'color': 'Кремовый с тёмными отметинами',
        'image': 'cat2.png'
    },
    {
        'id': 3,
        'name': 'Васька',
        'breed': 'Дворовый',
        'description': 'Рыжий проказник с весёлым характером. Обожает играть и бегать.',
        'age': 1,
        'color': 'Рыжий',
        'image': 'cat3.png'
    },
    {
        'id': 4,
        'name': 'Снежок',
        'breed': 'Персидская',
        'description': 'Пушистое белое облачко. Спокойный и флегматичный аристократ.',
        'age': 4,
        'color': 'Белый',
        'image': 'cat4.png'
    },
    {
        'id': 5,
        'name': 'Рыжик',
        'breed': 'Мейн-кун',
        'description': 'Величественный гигант с кисточками на ушах. Добрый и общительный.',
        'age': 2,
        'color': 'Рыжий мраморный',
        'image': 'cat5.png'
    },
    {
        'id': 6,
        'name': 'Муся',
        'breed': 'Шотландская вислоухая',
        'description': 'Милая кошечка с прижатыми ушками. Любит спать в необычных позах.',
        'age': 1,
        'color': 'Серый полосатый',
        'image': 'cat6.png'
    },
    {
        'id': 7,
        'name': 'Черныш',
        'breed': 'Бомбейская',
        'description': 'Чёрная пантера в миниатюре. Глаза как золотые монеты.',
        'age': 3,
        'color': 'Чёрный',
        'image': 'cat7.png'
    },
    {
        'id': 8,
        'name': 'Пушинка',
        'breed': 'Сибирская',
        'description': 'Пушистая красавица с густой шерстью. Отличный охотник.',
        'age': 2,
        'color': 'Трёхцветная',
        'image': 'cat8.png'
    },
    {
        'id': 9,
        'name': 'Гаврош',
        'breed': 'Дворовый',
        'description': 'Полосатый непоседа. Любит исследовать новые территории.',
        'age': 1,
        'color': 'Серый полосатый',
        'image': 'cat9.png'
    },
    {
        'id': 10,
        'name': 'Злата',
        'breed': 'Абиссинская',
        'description': 'Стройная и грациозная. Шерсть переливается золотыми оттенками.',
        'age': 2,
        'color': 'Золотистый',
        'image': 'cat10.png'
    },
    {
        'id': 11,
        'name': 'Симба',
        'breed': 'Бенгальская',
        'description': 'Дикая внешность, но ласковый характер. Любит воду.',
        'age': 1,
        'color': 'Леопардовый',
        'image': 'cat11.png'
    },
    {
        'id': 12,
        'name': 'Багира',
        'breed': 'Ориентальная',
        'description': 'Утончённая кошка с большими ушами. Очень привязывается к хозяину.',
        'age': 3,
        'color': 'Шоколадный',
        'image': 'cat12.png'
    },
    {
        'id': 13,
        'name': 'Маркиз',
        'breed': 'Русская голубая',
        'description': 'Серебристо-голубая шерсть и зелёные глаза. Сдержанный и интеллигентный.',
        'age': 4,
        'color': 'Голубой',
        'image': 'cat13.png'
    },
    {
        'id': 14,
        'name': 'Луна',
        'breed': 'Турецкая ангора',
        'description': 'Белоснежная красавица с разноцветными глазами. Игривая и любопытная.',
        'age': 2,
        'color': 'Белый',
        'image': 'cat14.png'
    },
    {
        'id': 15,
        'name': 'Тигра',
        'breed': 'Дворовый',
        'description': 'Полосатая охотница. Независимая и свободолюбивая.',
        'age': 3,
        'color': 'Тигровый',
        'image': 'cat15.png'
    },
    {
        'id': 16,
        'name': 'Сёма',
        'breed': 'Экзотическая короткошёрстная',
        'description': 'Мордашка как у перса, но без проблем с дыханием. Очень милый и спокойный.',
        'age': 2,
        'color': 'Кремовый',
        'image': 'cat16.png'
    },
    {
        'id': 17,
        'name': 'Ириска',
        'breed': 'Невская маскарадная',
        'description': 'Пушистая кошка с тёмной маской на мордочке. Дружелюбная и общительная.',
        'age': 3,
        'color': 'Колор-пойнт',
        'image': 'cat17.png'
    },
    {
        'id': 18,
        'name': 'Филя',
        'breed': 'Корниш-рекс',
        'description': 'Кудрявая шерсть и большие уши. Энергичный и ласковый.',
        'age': 1,
        'color': 'Белый с чёрным',
        'image': 'cat18.png'
    },
    {
        'id': 19,
        'name': 'Жужа',
        'breed': 'Сфинкс',
        'description': 'Безшёрстная кошка. Очень теплолюбивая и нуждается в особом уходе.',
        'age': 2,
        'color': 'Розовый',
        'image': 'cat19.png'
    },
    {
        'id': 20,
        'name': 'Кексик',
        'breed': 'Британская длинношёрстная',
        'description': 'Пушистый комочек с круглыми глазами. Флегматичный домосед.',
        'age': 2,
        'color': 'Серебристый',
        'image': 'cat20.png'
    }
]
@app.route('/lab2/cats')
def cats_list():
    """Список всех котиков"""
    return render_template('cats.html', cats=cats)

@app.route('/lab2/example')
def example():
    name = 'Анна Кирдячкина'
    lab_number = 'Лабораторная работа 2'
    group = 'ФБИ-32'
    course = 'Курс 3'
    fruits = [
        {'name': 'яблоки', 'price': 100},
        {'name': 'груши', 'price': 120},
        {'name': 'апельсины', 'price': 80},
        {'name': 'мандарины', 'price': 95},
        {'name': 'манго', 'price': 321}
    ]
    return render_template('example.html', name=name, lab_number=lab_number, group=group, course=course, fruits=fruits)

@app.route('/lab2/')
def lab2():
    return render_template('lab2.html')

@app.route('/lab2/filters')
def filters():
    phrase = "О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных..."
    return render_template('filter.html', phrase=phrase)

if __name__ == '__main__':
    app.run(debug=True)