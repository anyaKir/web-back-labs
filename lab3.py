from flask import Blueprint, render_template, request, make_response, redirect
import datetime
lab3 = Blueprint('lab3', __name__)

@lab3.route('/lab3/')
def lab():
    name = request.cookies.get('name')
    name_color = request.cookies.get('name_color')
    return render_template('lab3/lab3.html', name=name, name_color=name_color)


@lab3.route('/lab3/cookie')
def cookie():
    resp = make_response(redirect('/lab3/'))
    resp.set_cookie('name', 'Alex', max_age=5)
    resp.set_cookie('age', '20')
    resp.set_cookie('name_color', 'magenta')
    return resp


@lab3.route('/lab3/del_cookie')
def del_cookie():
    resp = make_response(redirect('/lab3/'))
    resp.delete_cookie('name')
    resp.delete_cookie('age')
    resp.delete_cookie('name_color')
    return resp 


@lab3.route('/lab3/clear_settings')
def clear_settings():
    resp = make_response(redirect('/lab3/settings'))
    resp.delete_cookie('color')
    resp.delete_cookie('bgcolor')
    resp.delete_cookie('fontsize')
    resp.delete_cookie('fontstyle')
    return resp


@lab3.route('/lab3/form1')
def form1():
    errors = {}
    user = request.args.get('user')  
    age = request.args.get('age')    
    sex = request.args.get('sex')    
    
    if user == '':
        errors['user'] = 'Заполните поле!'
        user = None

    return render_template('lab3/form1.html', user=user, age=age, sex=sex, errors=errors)

@lab3.route('/lab3/order')
def order():
    return render_template('lab3/order.html')

@lab3.route('/lab3/pay')
def pay():
    price = 0
    drink = request.args.get('drink')

    if drink == 'cofee':
        price = 120
    elif drink == 'black-tea':
        price = 80
    else:
        price = 70
    
    if request.args.get('milk') == 'on':
        price += 30
    if request.args.get('sugar') == 'on':
        price += 10

    return render_template('lab3/pay.html', price=price)

@lab3.route('/lab3/success')
def success():
    price = request.args.get('price')
    return render_template('lab3/success.html', price=price)

@lab3.route('/lab3/settings')
def settings():
    color = request.args.get('color')
    bgcolor = request.args.get('bgcolor')
    fontsize = request.args.get('fontsize')
    fontstyle = request.args.get('fontstyle')

    if color or bgcolor or fontsize or fontstyle:
        resp = make_response(redirect('/lab3/settings'))
        if color:
            resp.set_cookie('color', color)
        if bgcolor:
            resp.set_cookie('bgcolor', bgcolor)
        if fontsize:
            resp.set_cookie('fontsize', fontsize)
        if fontstyle:
            resp.set_cookie('fontstyle', fontstyle)
        return resp
    
    color = request.cookies.get('color')
    bgcolor = request.cookies.get('bgcolor')
    fontsize = request.cookies.get('fontsize')
    fontstyle = request.cookies.get('fontstyle')

    return render_template('lab3/settings.html',
                           color=color,
                           bgcolor=bgcolor,
                           fontsize=fontsize,
                           fontstyle=fontstyle)

@lab3.route('/lab3/ticket', methods=['GET', 'POST'])
def ticket_form():
    errors = {}
    data = {}

    if request.method == 'POST':
        # Получаем данные из формы
        data['fio'] = request.form.get('fio', '').strip()
        data['berth'] = request.form.get('berth', '').strip()
        data['linen'] = request.form.get('linen')
        data['luggage'] = request.form.get('luggage')
        data['age'] = request.form.get('age', '').strip()
        data['departure'] = request.form.get('departure', '').strip()
        data['destination'] = request.form.get('destination', '').strip()
        data['date'] = request.form.get('date', '').strip()
        data['insurance'] = request.form.get('insurance')

        # Проверка всех полей на пустоту
        for field in ['fio', 'berth', 'age', 'departure', 'destination', 'date']:
            if not data[field]:
                errors[field] = 'Обязательное поле!'

        # Проверка возраста
        try:
            age_val = int(data['age'])
            if not (1 <= age_val <= 120):
                errors['age'] = 'Возраст должен быть от 1 до 120 лет!'
        except:
            errors['age'] = 'Введите корректный возраст!'

        if not errors:
            # Рассчет стоимости
            price = 1000 if age_val >= 18 else 700
            if data['berth'] in ['нижняя', 'нижняя боковая']:
                price += 100
            if data['linen'] == 'on':
                price += 75
            if data['luggage'] == 'on':
                price += 250
            if data['insurance'] == 'on':
                price += 150

            data['price'] = price
            data['child_ticket'] = age_val < 18

            return render_template('lab3/ticket_result.html', data=data)

    return render_template('lab3/ticket_form.html', errors=errors, data=data)

products = [
    {"name": "iPhone 15", "price": 1200, "brand": "Apple", "color": "Black"},
    {"name": "Samsung Galaxy S23", "price": 950, "brand": "Samsung", "color": "White"},
    {"name": "Google Pixel 8", "price": 800, "brand": "Google", "color": "Blue"},
    {"name": "OnePlus 11", "price": 700, "brand": "OnePlus", "color": "Red"},
    {"name": "Xiaomi 13", "price": 600, "brand": "Xiaomi", "color": "Green"},
    {"name": "Huawei P60", "price": 750, "brand": "Huawei", "color": "Black"},
    {"name": "Sony Xperia 1 IV", "price": 1000, "brand": "Sony", "color": "Gray"},
    {"name": "Motorola Edge 40", "price": 550, "brand": "Motorola", "color": "Blue"},
    {"name": "Nokia G400", "price": 300, "brand": "Nokia", "color": "White"},
    {"name": "Asus Zenfone 10", "price": 650, "brand": "Asus", "color": "Black"},
    {"name": "Realme GT3", "price": 400, "brand": "Realme", "color": "Yellow"},
    {"name": "Oppo Find X6", "price": 850, "brand": "Oppo", "color": "Silver"},
    {"name": "Vivo X90", "price": 700, "brand": "Vivo", "color": "Gold"},
    {"name": "Lenovo Legion Y90", "price": 900, "brand": "Lenovo", "color": "Black"},
    {"name": "ZTE Axon 50", "price": 500, "brand": "ZTE", "color": "Blue"},
    {"name": "Honor Magic 6", "price": 650, "brand": "Honor", "color": "Green"},
    {"name": "Alcatel 1S", "price": 150, "brand": "Alcatel", "color": "Red"},
    {"name": "Fairphone 5", "price": 450, "brand": "Fairphone", "color": "Gray"},
    {"name": "Micromax IN 2b", "price": 100, "brand": "Micromax", "color": "Black"},
    {"name": "Tecno Camon 20", "price": 200, "brand": "Tecno", "color": "White"}
]
# Очистка фильтра (сброс)
@lab3.route('/lab3/products/reset')
def products_reset():
    resp = make_response(redirect('/lab3/products'))
    resp.delete_cookie('min_price')
    resp.delete_cookie('max_price')
    return resp

# Основной маршрут с фильтром
@lab3.route('/lab3/products', methods=['GET'])
def products_list():
    # Получаем значения из формы или из куки
    min_price = request.args.get('min_price') or request.cookies.get('min_price')
    max_price = request.args.get('max_price') or request.cookies.get('max_price')

    # Безопасное преобразование к float
    def safe_float(val):
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    min_val = safe_float(min_price)
    max_val = safe_float(max_price)

    # Автоперестановка, если min > max
    if min_val is not None and max_val is not None and min_val > max_val:
        min_val, max_val = max_val, min_val

    # Фильтрация товаров
    filtered = products.copy()
    if min_val is not None:
        filtered = [p for p in filtered if p["price"] >= min_val]
    if max_val is not None:
        filtered = [p for p in filtered if p["price"] <= max_val]

    resp = make_response(render_template(
        'lab3/products.html',
        products=filtered,
        min_price=min_val,
        max_price=max_val,
        count=len(filtered),
        all_min=min([p["price"] for p in products]),
        all_max=max([p["price"] for p in products])
    ))

    # Сохраняем значения в куки при поиске
    if request.args.get('search'):
        if min_val is not None:
            resp.set_cookie('min_price', str(min_val), max_age=30*24*60*60)
        if max_val is not None:
            resp.set_cookie('max_price', str(max_val), max_age=30*24*60*60)

    return resp


