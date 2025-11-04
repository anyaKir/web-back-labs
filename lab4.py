from flask import Blueprint, render_template, request, make_response, redirect, session
import datetime
lab4 = Blueprint('lab4', __name__)


@lab4.route('/lab4/')
def lab():
    return render_template('lab4/lab4.html')


@lab4.route('/lab4/div-form')
def div_form():
    return render_template('lab4/div-form.html')


@lab4.route('/lab4/div', methods = ['POST'])
def div():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/div.html', error='Оба поля должны быть заполнены!')
    x1 = int(x1)
    x2 = int(x2)

    if x2 == 0:
        return render_template('lab4/div.html', error='На ноль делить нельзя!')
    result = x1 / x2
    return render_template('lab4/div.html', x1=x1, x2=x2, result=result)

# ---------- 2. Сложение ----------
@lab4.route('/lab4/sum-form')
def sum_form():
    return render_template('lab4/sum-form.html')

@lab4.route('/lab4/sum', methods=['POST'])
def sum_numbers():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')

    x1 = int(x1) if x1 else 0
    x2 = int(x2) if x2 else 0

    result = x1 + x2
    return render_template('lab4/sum.html', x1=x1, x2=x2, result=result)

# ---------- 3. Умножение ----------
@lab4.route('/lab4/mul-form')
def mul_form():
    return render_template('lab4/mul-form.html')

@lab4.route('/lab4/mul', methods=['POST'])
def mul():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')

    x1 = int(x1) if x1 else 1
    x2 = int(x2) if x2 else 1

    result = x1 * x2
    return render_template('lab4/mul.html', x1=x1, x2=x2, result=result)

# ---------- 4. Вычитание ----------
@lab4.route('/lab4/sub-form')
def sub_form():
    return render_template('lab4/sub-form.html')

@lab4.route('/lab4/sub', methods=['POST'])
def sub():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')

    if not x1 or not x2:
        return render_template('lab4/sub.html', error='Оба поля должны быть заполнены!')

    x1 = int(x1)
    x2 = int(x2)

    result = x1 - x2
    return render_template('lab4/sub.html', x1=x1, x2=x2, result=result)


# ---------- 5. Возведение в степень ----------
@lab4.route('/lab4/pow-form')
def pow_form():
    return render_template('lab4/pow-form.html')

@lab4.route('/lab4/pow', methods=['POST'])
def pow_():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')

    if not x1 or not x2:
        return render_template('lab4/pow.html', error='Оба поля должны быть заполнены!')

    x1 = int(x1)
    x2 = int(x2)

    if x1 == 0 and x2 == 0:
        return render_template('lab4/pow.html', error='0 в степени 0 не определено!')

    result = x1 ** x2
    return render_template('lab4/pow.html', x1=x1, x2=x2, result=result)

tree_count = 0
@lab4.route('/lab4/tree', methods = ['GET', 'POST'])
def tree():
    global tree_count

    if request.method == 'POST':
        operation = request.form.get('operation')

        if operation == 'plant' and tree_count < 10:
            tree_count += 1
        elif operation == 'cut' and tree_count > 0:
            tree_count -= 1

        return redirect('/lab4/tree')  

    return render_template('lab4/tree.html', tree_count=tree_count)

users = [
    {'login': 'alex', 'password': '123', 'name': 'Александр Иванов', 'gender': 'м'},
    {'login': 'bob', 'password': '555', 'name': 'Борис Петров', 'gender': 'м'},
    {'login': 'anya', 'password': '999', 'name': 'Анна Смирнова', 'gender': 'ж'},
    {'login': 'nastya', 'password': '444', 'name': 'Анастасия Кузнецова', 'gender': 'ж'},
]

# ---------- REGISTER ----------
@lab4.route('/lab4/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login_value = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm', '').strip()
        name = request.form.get('name', '').strip()

        if not login_value or not password or not confirm or not name:
            error = "❌ Все поля должны быть заполнены"
            return render_template('lab4/register.html', error=error, login=login_value, name=name)
        if password != confirm:
            error = "❌ Пароли не совпадают"
            return render_template('lab4/register.html', error=error, login=login_value, name=name)
        if any(u['login'] == login_value for u in users):
            error = "❌ Пользователь с таким логином уже существует"
            return render_template('lab4/register.html', error=error, login=login_value, name=name)

        users.append({'login': login_value, 'password': password, 'name': name, 'gender': ''})
        return redirect('/lab4/login')

    return render_template('lab4/register.html', error='', login='', name='')

# ---------- USERS LIST ----------
@lab4.route('/lab4/users', methods=['GET', 'POST'])
def users_list():
    if 'login' not in session:
        return redirect('/lab4/login')

    current_user = next(u for u in users if u['login'] == session['login'])

    # Удаление пользователя
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            users.remove(current_user)
            session.pop('login')
            return redirect('/lab4/login')
        elif action == 'edit':
            new_login = request.form.get('login', '').strip()
            new_name = request.form.get('name', '').strip()
            new_password = request.form.get('password', '').strip()
            confirm = request.form.get('confirm', '').strip()

            if new_password or confirm:
                if new_password != confirm:
                    error = "❌ Пароли не совпадают"
                    return render_template('lab4/users.html', users=users, current_user=current_user, error=error)
                current_user['password'] = new_password

            if new_login:
                if any(u['login'] == new_login and u != current_user for u in users):
                    error = "❌ Логин уже занят"
                    return render_template('lab4/users.html', users=users, current_user=current_user, error=error)
                current_user['login'] = new_login
                session['login'] = new_login

            if new_name:
                current_user['name'] = new_name

            return redirect('/lab4/users')

    return render_template('lab4/users.html', users=users, current_user=current_user, error='')
# ---------- LOGIN / LOGOUT (обновленный) ----------
@lab4.route('/lab4/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'login' in session:
            user = next((u for u in users if u['login'] == session['login']), None)
            if user:
                return render_template("lab4/login.html", authorized=True, name=user['name'])
        return render_template("lab4/login.html", authorized=False, login='', error='')

    login_value = request.form.get('login', '').strip()
    password = request.form.get('password', '').strip()

    if not login_value:
        return render_template("lab4/login.html", error="❌ Не введён логин", authorized=False, login=login_value)
    if not password:
        return render_template("lab4/login.html", error="❌ Не введён пароль", authorized=False, login=login_value)

    for user in users:
        if login_value == user['login'] and password == user['password']:
            session['login'] = login_value
            return redirect('/lab4/login')

    error = '❌ Неверные логин и/или пароль'
    return render_template("lab4/login.html", error=error, authorized=False, login=login_value)

@lab4.route('/lab4/logout', methods=['POST'])
def logout():
    session.pop('login', None)
    return redirect('/lab4/login')


@lab4.route('/lab4/fridge', methods=['GET', 'POST'])
def fridge():
    temperature = None
    message = ''
    snowflakes = 0
    error = ''

    if request.method == 'POST':
        temp_str = request.form.get('temperature', '').strip()

        if temp_str == '':
            error = 'Ошибка: не задана температура'
        else:
            try:
                temperature = int(temp_str)

                if temperature < -12:
                    error = 'Не удалось установить температуру — слишком низкое значение'
                elif temperature > -1:
                    error = 'Не удалось установить температуру — слишком высокое значение'
                elif -12 <= temperature <= -9:
                    message = f'Установлена температура: {temperature}°C'
                    snowflakes = 3
                elif -8 <= temperature <= -5:
                    message = f'Установлена температура: {temperature}°C'
                    snowflakes = 2
                elif -4 <= temperature <= -1:
                    message = f'Установлена температура: {temperature}°C'
                    snowflakes = 1

            except ValueError:
                error = 'Ошибка: введите число'

    return render_template(
        'lab4/fridge.html',
        temperature=temperature,
        message=message,
        snowflakes=snowflakes,
        error=error
    )


@lab4.route('/lab4/grain', methods=['GET', 'POST'])
def grain_order():
    grains = {
        'ячмень': 12000,
        'овёс': 8500,
        'пшеница': 9000,
        'рожь': 15000
    }

    result = None
    error = ''
    discount_info = ''
    selected_grain = ''
    weight = ''

    if request.method == 'POST':
        selected_grain = request.form.get('grain')
        weight_str = request.form.get('weight', '').strip()

        # Проверяем наличие данных
        if not weight_str:
            error = 'Ошибка: не указан вес!'
        else:
            try:
                weight = float(weight_str)
                if weight <= 0:
                    error = 'Ошибка: вес должен быть больше 0!'
                elif weight > 100:
                    error = 'Ошибка: такого объёма сейчас нет в наличии.'
                elif selected_grain not in grains:
                    error = 'Ошибка: выберите тип зерна.'
                else:
                    price_per_ton = grains[selected_grain]
                    total = weight * price_per_ton
                    discount = 0

                    if weight > 10:
                        discount = 0.1
                        total *= (1 - discount)
                        discount_info = '✅ Применена скидка 10% за большой объём.'

                    result = f'Заказ успешно сформирован. Вы заказали {selected_grain}. Вес: {weight} т. Сумма к оплате: {int(total):,} руб.'.replace(',', ' ')
            except ValueError:
                error = 'Ошибка: введите корректное число!'

    return render_template(
        'lab4/grain.html',
        grains=grains,
        result=result,
        error=error,
        discount_info=discount_info,
        selected_grain=selected_grain,
        weight=weight
    )