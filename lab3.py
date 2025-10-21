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



