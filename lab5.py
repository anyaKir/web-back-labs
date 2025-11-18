from flask import Blueprint, request, render_template, session
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash


lab5 = Blueprint('lab5', __name__)


# --------------------- ФУНКЦИИ БД ---------------------

def db_connect():
    conn = psycopg2.connect(
        host='127.0.0.1',
        database='anna_kirdyachkina_knowledge_base',
        user='anna_kirdyachkina_knowledge_base',
        password='123'
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    return conn, cur


def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()


# ---------------------- ГЛАВНАЯ -----------------------

@lab5.route('/lab5/')
def lab():
    return render_template('lab5/lab5.html', login=session.get('login'))


# ---------------------- РЕГИСТРАЦИЯ --------------------

@lab5.route('/lab5/register', methods=['GET', 'POST'])
def register():

    if request.method == 'GET':
        return render_template('lab5/register.html')

    login = request.form.get('login')
    password = request.form.get('password')

    # правильная проверка!
    if not login or not password:
        return render_template('lab5/register.html', error='Заполните все поля')

    conn, cur = db_connect()

    # проверка существования
    cur.execute("SELECT login FROM users WHERE login = %s;", (login,))
    if cur.fetchone():
        db_close(conn, cur)
        return render_template('lab5/register.html',
                               error="Такой пользователь уже существует")

    # хэширование пароля
    password_hash = generate_password_hash(password)

    # безопасная вставка
    cur.execute(
        "INSERT INTO users (login, password) VALUES (%s, %s);",
        (login, password_hash)
    )

    db_close(conn, cur)
    return render_template('lab5/success.html', login=login)


# ------------------------- ВХОД ------------------------

@lab5.route('/lab5/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('lab5/login.html')

    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return render_template('lab5/login.html', error="Заполните поля")

    conn, cur = db_connect()

    cur.execute("SELECT * FROM users WHERE login = %s;", (login,))
    user = cur.fetchone()

    if not user:
        db_close(conn, cur)
        return render_template('lab5/login.html',
                               error="Логин и/или пароль неверны")

    # проверка хэша
    if not check_password_hash(user['password'], password):
        db_close(conn, cur)
        return render_template('lab5/login.html',
                               error="Логин и/или пароль неверны")

    # успешный вход
    session['login'] = login

    db_close(conn, cur)
    return render_template('lab5/success_login.html', login=login)


# ------------------- ПРОЧИЕ СТРАНИЦЫ --------------------

@lab5.route('/lab5/list')
def list_articles():
    return render_template('lab5/list.html')


@lab5.route('/lab5/create')
def create_article():
    return render_template('lab5/create.html')

