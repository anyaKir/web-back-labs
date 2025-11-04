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