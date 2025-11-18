from flask import Blueprint, request, render_template, session, redirect, current_app
import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash

lab5 = Blueprint('lab5', __name__)


def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='anna_kirdyachkina_knowledge_base',
            user='anna_kirdyachkina_knowledge_base',
            password='123'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        db_path = os.path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()


def get_placeholder():
    return "%s" if current_app.config['DB_TYPE'] == 'postgres' else "?"


@lab5.route('/lab5/')
def lab():
    return render_template('lab5/lab5.html', login=session.get('login'))


@lab5.route('/lab5/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')

    login_user = request.form.get('login')
    password = request.form.get('password')

    if not login_user or not password:
        return render_template('lab5/register.html', error='Заполните все поля')

    conn, cur = db_connect()
    placeholder = get_placeholder()

    cur.execute(f"SELECT login FROM users WHERE login={placeholder};", (login_user,))
    if cur.fetchone():
        db_close(conn, cur)
        return render_template('lab5/register.html', error="Такой пользователь уже существует")

    password_hash = generate_password_hash(password)
    cur.execute(f"INSERT INTO users (login, password) VALUES ({placeholder}, {placeholder});", (login_user, password_hash))

    db_close(conn, cur)
    return render_template('lab5/success.html', login=login_user)


@lab5.route('/lab5/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html')

    login_user = request.form.get('login')
    password = request.form.get('password')

    if not login_user or not password:
        return render_template('lab5/login.html', error="Заполните поля")

    conn, cur = db_connect()
    placeholder = get_placeholder()

    cur.execute(f"SELECT * FROM users WHERE login={placeholder};", (login_user,))
    user = cur.fetchone()

    if not user or not check_password_hash(user['password'], password):
        db_close(conn, cur)
        return render_template('lab5/login.html', error="Логин и/или пароль неверны")

    session['login'] = login_user
    db_close(conn, cur)
    return render_template('lab5/success_login.html', login=login_user)


@lab5.route('/lab5/list')
def list_articles():
    login_user = session.get('login')
    if not login_user:
        return redirect('/lab5/login')

    conn, cur = db_connect()
    placeholder = get_placeholder()

    cur.execute(f"SELECT id FROM users WHERE login={placeholder};", (login_user,))
    user = cur.fetchone()
    user_id = user['id']

    cur.execute(f"SELECT * FROM articles WHERE user_id={placeholder} ORDER BY id DESC;", (user_id,))
    articles = cur.fetchall()

    db_close(conn, cur)
    return render_template('lab5/list.html', articles=articles)


@lab5.route('/lab5/create', methods=['GET', 'POST'])
def create():
    login_user = session.get('login')
    if not login_user:
        return redirect('/lab5/login')

    if request.method == 'GET':
        return render_template('lab5/create_article.html')

    title = request.form.get('title')
    article_text = request.form.get('article_text')

    if not (title and article_text):
        return render_template('lab5/create_article.html', error='Заполните все поля')

    conn, cur = db_connect()
    placeholder = get_placeholder()

    cur.execute(f"SELECT id FROM users WHERE login={placeholder};", (login_user,))
    user = cur.fetchone()
    user_id = user['id']

    cur.execute(f"INSERT INTO articles (user_id, title, article_text) VALUES ({placeholder}, {placeholder}, {placeholder});",
                (user_id, title, article_text))

    db_close(conn, cur)
    return redirect('/lab5/list')

