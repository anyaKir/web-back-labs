from flask import Blueprint, request, render_template, session, redirect, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
import re

RGZ = Blueprint('RGZ', __name__)

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

# ---------------- ГЛАВНАЯ ----------------
@RGZ.route('/rgz/')
def rgz_main():
    return render_template(
        'RGZ/RGZ.html',
        login=session.get('login'),
        role=session.get('role')
    )

# ---------------- API ----------------
@RGZ.route('/rgz/api/books')
def api_books():
    where = []
    args = []

    title = request.args.get('title')
    author = request.args.get('author')
    pages_from = request.args.get('pages_from')
    pages_to = request.args.get('pages_to')
    publisher = request.args.get('publisher')
    sort = request.args.get('sort', 'title')
    offset = int(request.args.get('offset', 0))

    if title:
        where.append("title ILIKE %s")
        args.append(f"%{title}%")

    if author:
        where.append("author ILIKE %s")
        args.append(f"%{author}%")

    if publisher:
        where.append("publisher ILIKE %s")
        args.append(f"%{publisher}%")

    if pages_from:
        where.append("pages >= %s")
        args.append(int(pages_from))

    if pages_to:
        where.append("pages <= %s")
        args.append(int(pages_to))

    sql = "SELECT * FROM books"
    if where:
        sql += " WHERE " + " AND ".join(where)

    if sort not in ['title','author','pages','publisher']:
        sort = 'title'

    sql += f" ORDER BY {sort} LIMIT 20 OFFSET %s"
    args.append(offset)

    conn, cur = db_connect()
    cur.execute(sql, args)
    books = cur.fetchall()
    db_close(conn, cur)

    return jsonify(books)

# ---------------- ВХОД ----------------
@RGZ.route('/rgz/login', methods=['GET','POST'])
def rgz_login():
    if request.method == 'GET':
        return render_template('RGZ/rgz_login.html')

    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return render_template('RGZ/rgz_login.html', error='Заполните все поля')

    conn, cur = db_connect()
    cur.execute("SELECT * FROM users WHERE login=%s", (login,))
    user = cur.fetchone()
    db_close(conn, cur)

    if not user or not check_password_hash(user['password'], password):
        return render_template('RGZ/rgz_login.html', error='Неверный логин или пароль')

    session['login'] = user['login']
    session['role'] = user['role']
    return redirect('/rgz/')

# ---------------- ВЫХОД ----------------
@RGZ.route('/rgz/logout')
def rgz_logout():
    session.clear()
    return redirect('/rgz/')

# ---------------- АДМИН ----------------
@RGZ.route('/rgz/admin')
def rgz_admin():
    if session.get('role') != 'admin':
        return redirect('/rgz/')
    return render_template('RGZ/rgz_admin.html')

# ---------------- РЕГИСТРАЦИЯ ----------------
@RGZ.route('/rgz/register', methods=['GET', 'POST'])
def rgz_register():
    if request.method == 'GET':
        return render_template('RGZ/rgz_register.html')

    login = request.form.get('login')
    password = request.form.get('password')
    confirm = request.form.get('confirm')

    # Проверка пароля
    if password != confirm:
        return render_template('RGZ/rgz_register.html', error="Пароли не совпадают")

    if not login or not password:
        return render_template('RGZ/rgz_register.html', error="Заполните все поля")

    # Проверка валидности логина (только латинские буквы и цифры)
    if not re.match(r'^[A-Za-z0-9]+$', login):
        return render_template('RGZ/rgz_register.html', error="Логин может содержать только латинские буквы и цифры")

    conn, cur = db_connect()
    cur.execute("SELECT * FROM users WHERE login=%s;", (login,))
    if cur.fetchone():
        db_close(conn, cur)
        return render_template('RGZ/rgz_register.html', error="Пользователь с таким логином уже существует")

    # Вставка нового пользователя
    hashed_password = generate_password_hash(password)
    cur.execute("INSERT INTO users (login, password, role) VALUES (%s, %s, 'user');", (login, hashed_password))
    db_close(conn, cur)

    return redirect('/rgz/login')
