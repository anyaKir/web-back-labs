from flask import Blueprint, url_for, request, redirect, render_template, abort
import datetime
lab2 = Blueprint('lab2', __name__)


@lab2.route('/lab2/a')
def a():
    return 'без слэша'


@lab2.route('/lab2/a/')
def a2():
    return 'со слэшем'

flower_list = [
    {"name": "роза", "price": 300},
    {"name": "тюльпан", "price": 310},
    {"name": "незабудка", "price": 320},
    {"name": "ромашка", "price": 330},
    {"name": "георгин", "price": 300},
    {"name": "гладиолус", "price": 310}
]


@lab2.route('/lab2/flowers')
def all_flowers():
    return render_template('lab2/all_flowers.html', flower_list=flower_list)


@lab2.route('/lab2/del_flower/<int:flower_id>')
def del_flower(flower_id):
    if 0 <= flower_id < len(flower_list):
        flower_list.pop(flower_id)
        return redirect(url_for('lab2/lab2.all_flowers'))
    else:
        abort(404)


@lab2.route('/lab2/clear_flowers')
def clear_flowers():
    flower_list.clear()
    return redirect(url_for('lab2/lab2.all_flowers'))


@lab2.route('/lab2/add_flower/<name>')
def add_flower(name):
    flower_list.append({"name": name, "price": 300})
    return redirect(url_for('lab2/lab2.all_flowers'))


@lab2.route('/lab2/add_flower', methods=['POST'])
def add_flower_post():
    name = request.form.get('flower_name')
    price = request.form.get('flower_price', type=int)
    if not name or not price:
        return render_template('error400.html'), 400
    flower_list.append({"name": name, "price": price})
    return redirect(url_for('lab2/lab2.all_flowers'))


@lab2.route('/lab2/calc/')
def calc_default():
    """Перенаправление на калькулятор с значениями по умолчанию"""
    return redirect('lab2//lab2/calc/1/1')


@lab2.route('/lab2/calc/<int:a>')
def calc_single(a):
    """Перенаправление на калькулятор с одним числом (второе = 1)"""
    return redirect(f'lab2//lab2/calc/{a}/1')


@lab2.route('/lab2/calc/<int:a>/<int:b>')
def calc(a, b):
    """Калькулятор с двумя числами"""
    return render_template('lab2/calc.html', a=a, b=b)

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


@lab2.route('/lab2/books')
def books_list():
    """Список всех книг"""
    return render_template('lab2/books.html', books=books)

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


@lab2.route('/lab2/cats')
def cats_list():
    """Список всех котиков"""
    return render_template('lab2/cats.html', cats=cats)


@lab2.route('/lab2/example')
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
    return render_template('lab2/example.html', name=name, lab_number=lab_number, group=group, course=course, fruits=fruits)


@lab2.route('/lab2/')
def lab():
    return render_template('lab2/lab2.html')


@lab2.route('/lab2/filters')
def filters():
    phrase = "О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных..."
    return render_template('lab2/filter.html', phrase=phrase)

