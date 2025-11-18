from flask import Blueprint, request, render_template, session, redirect, current_app, url_for
import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash

lab5 = Blueprint('lab5', __name__)

def db_connect():
    if current_app.config.get('DB_TYPE') == 'postgres':
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

# Главная страница
@lab5.route('/lab5/')
def lab():
    return render_template('lab5/lab5.html', login=session.get('login'))

# Регистрация (обновленная - с полем real_name)
@lab5.route('/lab5/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html', login=session.get('login'))

    login = request.form.get('login')
    password = request.form.get('password')
    real_name = request.form.get('real_name', '')

    if not login or not password:
        return render_template('lab5/register.html', error='Заполните логин и пароль', login=session.get('login'))

    conn, cur = db_connect()

    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("SELECT login FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT login FROM users WHERE login=?;", (login,))
    
    if cur.fetchone():
        db_close(conn, cur)
        return render_template('lab5/register.html',
                               error="Такой пользователь уже существует", login=session.get('login'))

    password_hash = generate_password_hash(password)

    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("INSERT INTO users (login, password, real_name) VALUES (%s, %s, %s);", 
                   (login, password_hash, real_name))
    else:
        cur.execute("INSERT INTO users (login, password, real_name) VALUES (?, ?, ?);", 
                   (login, password_hash, real_name))

    db_close(conn, cur)
    return render_template('lab5/success.html', login=login)

# Вход
@lab5.route('/lab5/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html', login=session.get('login'))

    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return render_template('lab5/login.html', error="Заполните поля", login=session.get('login'))

    conn, cur = db_connect()

    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("SELECT * FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT * FROM users WHERE login=?;", (login,))
    
    user = cur.fetchone()

    if not user:
        db_close(conn, cur)
        return render_template('lab5/login.html',
                               error="Логин и/или пароль неверны", login=session.get('login'))

    if not check_password_hash(user['password'], password):
        db_close(conn, cur)
        return render_template('lab5/login.html',
                               error="Логин и/или пароль неверны", login=session.get('login'))

    session['login'] = login
    session['user_id'] = user['id']
    db_close(conn, cur)
    return redirect('/lab5/')

# Выход
@lab5.route('/lab5/logout')
def logout():
    session.pop('login', None)
    session.pop('user_id', None)
    return redirect('/lab5/')

# Список пользователей
@lab5.route('/lab5/users')
def list_users():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("SELECT login, real_name FROM users ORDER BY login;")
    else:
        cur.execute("SELECT login, real_name FROM users ORDER BY login;")
    
    users = cur.fetchall()
    db_close(conn, cur)
    
    return render_template('lab5/users.html', users=users, login=login)

# Смена имени и пароля
@lab5.route('/lab5/profile', methods=['GET', 'POST'])
def profile():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("SELECT * FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT * FROM users WHERE login=?;", (login,))
    
    user = cur.fetchone()

    if request.method == 'GET':
        db_close(conn, cur)
        return render_template('lab5/profile.html', user=user, login=login)

    # Обработка формы
    real_name = request.form.get('real_name')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    errors = []

    # Проверка текущего пароля
    if current_password and not check_password_hash(user['password'], current_password):
        errors.append("Текущий пароль неверен")

    # Проверка нового пароля
    if new_password:
        if new_password != confirm_password:
            errors.append("Новый пароль и подтверждение не совпадают")
        if len(new_password) < 3:
            errors.append("Новый пароль должен быть не менее 3 символов")

    if errors:
        db_close(conn, cur)
        return render_template('lab5/profile.html', user=user, login=login, errors=errors)

    # Обновление данных
    if current_app.config.get('DB_TYPE') == 'postgres':
        if new_password:
            password_hash = generate_password_hash(new_password)
            cur.execute("UPDATE users SET real_name=%s, password=%s WHERE login=%s;", 
                       (real_name, password_hash, login))
        else:
            cur.execute("UPDATE users SET real_name=%s WHERE login=%s;", (real_name, login))
    else:
        if new_password:
            password_hash = generate_password_hash(new_password)
            cur.execute("UPDATE users SET real_name=?, password=? WHERE login=?;", 
                       (real_name, password_hash, login))
        else:
            cur.execute("UPDATE users SET real_name=? WHERE login=?;", (real_name, login))

    db_close(conn, cur)
    return redirect('/lab5/profile?success=1')

# Список статей (обновленный - с избранными и публичными)
@lab5.route('/lab5/list')
def list_articles():
    login = session.get('login')
    user_id = session.get('user_id')

    conn, cur = db_connect()

    if login and user_id:
        # Для авторизованных пользователей - их статьи с избранными первыми
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("""
                SELECT * FROM articles 
                WHERE user_id=%s 
                ORDER BY is_favorite DESC, id DESC;
            """, (user_id,))
        else:
            cur.execute("""
                SELECT * FROM articles 
                WHERE user_id=? 
                ORDER BY is_favorite DESC, id DESC;
            """, (user_id,))
        
        articles = cur.fetchall()
        db_close(conn, cur)
        return render_template('lab5/list.html', articles=articles, login=login)
    else:
        # Для неавторизованных - только публичные статьи
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("""
                SELECT a.*, u.login as author_login 
                FROM articles a 
                JOIN users u ON a.user_id = u.id 
                WHERE a.is_public = TRUE 
                ORDER BY a.id DESC;
            """)
        else:
            cur.execute("""
                SELECT a.*, u.login as author_login 
                FROM articles a 
                JOIN users u ON a.user_id = u.id 
                WHERE a.is_public = 1 
                ORDER BY a.id DESC;
            """)
        
        public_articles = cur.fetchall()
        db_close(conn, cur)
        return render_template('lab5/public_articles.html', articles=public_articles, login=login)

# Создание статьи (обновленное - с полями is_favorite и is_public)
@lab5.route('/lab5/create', methods=['GET', 'POST'])
def create():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    if request.method == 'GET':
        return render_template('lab5/create_article.html', login=login)

    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_favorite = bool(request.form.get('is_favorite'))
    is_public = bool(request.form.get('is_public'))

    if not title or not article_text:
        return render_template('lab5/create_article.html', 
                             error='Заполните все поля', 
                             login=login)

    conn, cur = db_connect()

    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("SELECT id FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT id FROM users WHERE login=?;", (login,))
    
    user = cur.fetchone()
    user_id = user['id']

    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("""
            INSERT INTO articles (user_id, title, article_text, is_favorite, is_public) 
            VALUES (%s, %s, %s, %s, %s);
        """, (user_id, title, article_text, is_favorite, is_public))
    else:
        cur.execute("""
            INSERT INTO articles (user_id, title, article_text, is_favorite, is_public) 
            VALUES (?, ?, ?, ?, ?);
        """, (user_id, title, article_text, is_favorite, is_public))

    db_close(conn, cur)
    return redirect('/lab5/list')

# Редактирование статьи (обновленное)
@lab5.route('/lab5/edit/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    # Проверяем, что статья принадлежит пользователю
    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("SELECT id FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT id FROM users WHERE login=?;", (login,))
    
    user = cur.fetchone()
    user_id = user['id']

    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("SELECT * FROM articles WHERE id=%s AND user_id=%s;", (article_id, user_id))
    else:
        cur.execute("SELECT * FROM articles WHERE id=? AND user_id=?;", (article_id, user_id))
    
    article = cur.fetchone()

    if not article:
        db_close(conn, cur)
        return redirect('/lab5/list')

    if request.method == 'GET':
        db_close(conn, cur)
        return render_template('lab5/edit_article.html', 
                             article=article, 
                             login=login)

    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_favorite = bool(request.form.get('is_favorite'))
    is_public = bool(request.form.get('is_public'))

    if not title or not article_text:
        db_close(conn, cur)
        return render_template('lab5/edit_article.html', 
                             article=article,
                             error='Заполните все поля', 
                             login=login)

    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("""
            UPDATE articles 
            SET title=%s, article_text=%s, is_favorite=%s, is_public=%s 
            WHERE id=%s;
        """, (title, article_text, is_favorite, is_public, article_id))
    else:
        cur.execute("""
            UPDATE articles 
            SET title=?, article_text=?, is_favorite=?, is_public=? 
            WHERE id=?;
        """, (title, article_text, is_favorite, is_public, article_id))

    db_close(conn, cur)
    return redirect('/lab5/list')

# Удаление статьи
@lab5.route('/lab5/delete/<int:article_id>')
def delete_article(article_id):
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    # Проверяем, что статья принадлежит пользователю
    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("SELECT id FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT id FROM users WHERE login=?;", (login,))
    
    user = cur.fetchone()
    user_id = user['id']

    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("DELETE FROM articles WHERE id=%s AND user_id=%s;", (article_id, user_id))
    else:
        cur.execute("DELETE FROM articles WHERE id=? AND user_id=?;", (article_id, user_id))

    db_close(conn, cur)
    return redirect('/lab5/list')

# Переключение избранного
@lab5.route('/lab5/toggle_favorite/<int:article_id>')
def toggle_favorite(article_id):
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    # Проверяем, что статья принадлежит пользователю
    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("SELECT id FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT id FROM users WHERE login=?;", (login,))
    
    user = cur.fetchone()
    user_id = user['id']

    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("SELECT * FROM articles WHERE id=%s AND user_id=%s;", (article_id, user_id))
    else:
        cur.execute("SELECT * FROM articles WHERE id=? AND user_id=?;", (article_id, user_id))
    
    article = cur.fetchone()

    if article:
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("UPDATE articles SET is_favorite = NOT is_favorite WHERE id=%s;", (article_id,))
        else:
            cur.execute("UPDATE articles SET is_favorite = NOT is_favorite WHERE id=?;", (article_id,))

    db_close(conn, cur)
    return redirect('/lab5/list')

# Публичные статьи
@lab5.route('/lab5/public')
def public_articles():
    conn, cur = db_connect()

    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute("""
            SELECT a.*, u.login as author_login 
            FROM articles a 
            JOIN users u ON a.user_id = u.id 
            WHERE a.is_public = TRUE 
            ORDER BY a.id DESC;
        """)
    else:
        cur.execute("""
            SELECT a.*, u.login as author_login 
            FROM articles a 
            JOIN users u ON a.user_id = u.id 
            WHERE a.is_public = 1 
            ORDER BY a.id DESC;
        """)
    
    public_articles = cur.fetchall()
    db_close(conn, cur)
    return render_template('lab5/public_articles.html', articles=public_articles, login=session.get('login'))
