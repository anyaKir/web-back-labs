from flask import Blueprint, request, render_template, session, redirect, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
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

# ---------------- API для книг (доступно всем) ----------------
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

    if sort not in ['title','author','pages','publisher','title DESC','author DESC','pages DESC','publisher DESC']:
        sort = 'title'

    sql += f" ORDER BY {sort} LIMIT 20 OFFSET %s"
    args.append(offset)

    conn, cur = db_connect()
    cur.execute(sql, args)
    books = cur.fetchall()
    db_close(conn, cur)

    return jsonify(books)

# ---------------- ВХОД ТОЛЬКО ДЛЯ АДМИНА ----------------
@RGZ.route('/rgz/login', methods=['GET','POST'])
def rgz_login():
    if request.method == 'GET':
        return render_template('RGZ/rgz_login.html')

    login = request.form.get('login')
    password = request.form.get('password')

    # ДЛЯ ОТЛАДКИ - печатаем что ввели
    print(f"=== ДЕБАГ ВХОДА ===")
    print(f"Введён логин: '{login}'")
    print(f"Введён пароль: '{password}'")

    if not login or not password:
        return render_template('RGZ/rgz_login.html', error='Заполните все поля')

    conn, cur = db_connect()
    
    # ДЛЯ ОТЛАДКИ - смотрим что в базе
    cur.execute("SELECT * FROM usersbooks")
    all_users = cur.fetchall()
    print(f"Все пользователи в базе: {all_users}")
    
    cur.execute("SELECT * FROM usersbooks WHERE login=%s", (login,))
    user = cur.fetchone()
    
    print(f"Найден пользователь: {user}")
    
    if user:
        print(f"Хеш пароля в базе: {user['password']}")
        print(f"Длина хеша: {len(user['password'])}")
    
    db_close(conn, cur)

    if not user:
        return render_template('RGZ/rgz_login.html', error='Пользователь не найден')

    # Проверяем пароль
    print(f"Проверяем пароль '{password}' с хешем...")
    from werkzeug.security import check_password_hash
    
    # ДЛЯ ОТЛАДКИ - также сгенерируем хеш для введённого пароля
    test_hash = generate_password_hash(password)
    print(f"Новый хеш для введённого пароля: {test_hash}")
    
    if not check_password_hash(user['password'], password):
        print(f"Хеши не совпадают!")
        return render_template('RGZ/rgz_login.html', error='Неверный пароль. Доступ только для администратора')

    print(f"Успешный вход! Роль: {user['role']}")
    
    if user['role'] != 'admin':
        return render_template('RGZ/rgz_login.html', error='Только администраторы могут входить')

    session['login'] = user['login']
    session['role'] = user['role']
    return redirect('/rgz/')
# ---------------- ВЫХОД ----------------
@RGZ.route('/rgz/logout')
def rgz_logout():
    session.clear()
    return redirect('/rgz/')

# ---------------- АДМИН ПАНЕЛЬ ----------------
@RGZ.route('/rgz/admin')
def rgz_admin():
    if session.get('role') != 'admin':
        return redirect('/rgz/login')

    conn, cur = db_connect()
    cur.execute("SELECT * FROM books ORDER BY id")
    books = cur.fetchall()
    db_close(conn, cur)

    return render_template(
        'RGZ/rgz_admin.html',
        books=books,
        login=session.get('login')
    )

# ---------------- API для админа (CRUD книг) ----------------
@RGZ.route('/rgz/api/admin/books', methods=['POST'])
def api_add_book():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    data = request.json
    # Валидация данных
    if not data.get('title') or not data.get('author'):
        return jsonify({'error': 'Название и автор обязательны'}), 400
    
    try:
        pages = int(data.get('pages', 0))
        if pages <= 0:
            return jsonify({'error': 'Количество страниц должно быть положительным'}), 400
    except:
        return jsonify({'error': 'Некорректное количество страниц'}), 400
    
    conn, cur = db_connect()
    try:
        cur.execute("""
            INSERT INTO books (title, author, pages, publisher, cover)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (data['title'], data['author'], pages, data.get('publisher', ''), data.get('cover', '/static/RGZ/default-book.png')))
        book_id = cur.fetchone()['id']
        db_close(conn, cur)
        return jsonify({'success': True, 'id': book_id})
    except Exception as e:
        db_close(conn, cur)
        return jsonify({'error': str(e)}), 500

@RGZ.route('/rgz/api/admin/books/<int:book_id>', methods=['PUT', 'DELETE'])
def api_admin_book(book_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    conn, cur = db_connect()
    
    if request.method == 'DELETE':
        try:
            cur.execute("DELETE FROM books WHERE id=%s", (book_id,))
            db_close(conn, cur)
            return jsonify({'success': True})
        except Exception as e:
            db_close(conn, cur)
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        data = request.json
        # Валидация
        if not data.get('title') or not data.get('author'):
            return jsonify({'error': 'Название и автор обязательны'}), 400
        
        try:
            pages = int(data.get('pages', 0))
            if pages <= 0:
                return jsonify({'error': 'Количество страниц должно быть положительным'}), 400
        except:
            return jsonify({'error': 'Некорректное количество страниц'}), 400
        
        try:
            cur.execute("""
                UPDATE books 
                SET title=%s, author=%s, pages=%s, publisher=%s, cover=%s
                WHERE id=%s
            """, (data['title'], data['author'], pages, data.get('publisher', ''), 
                  data.get('cover', '/static/RGZ/default-book.png'), book_id))
            db_close(conn, cur)
            return jsonify({'success': True})
        except Exception as e:
            db_close(conn, cur)
            return jsonify({'error': str(e)}), 500

# ---------------- СОЗДАНИЕ АДМИНА ПРИ НЕОБХОДИМОСТИ ----------------
@RGZ.route('/rgz/init_admin')
def init_admin():
    # Этот маршрут нужно удалить после создания админа!
    
    conn, cur = db_connect()
    
    # Удаляем если уже есть
    cur.execute("DELETE FROM usersbooks WHERE login='admin'")
    
    # Создаем админа (пароль: admin123)
    hashed_password = generate_password_hash('admin123')
    cur.execute("INSERT INTO usersbooks (login, password, role) VALUES (%s, %s, 'admin')", 
                ('admin', hashed_password))
    
    db_close(conn, cur)
    return "Админ создан: login: admin, password: admin123"

@RGZ.route('/rgz/admin/books/add', methods=['GET', 'POST'])
def admin_add_book():
    if session.get('role') != 'admin':
        return redirect('/rgz/login')

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        pages = request.form['pages']
        publisher = request.form['publisher']
        cover = request.form['cover']

        conn, cur = db_connect()
        cur.execute("""
            INSERT INTO books (title, author, pages, publisher, cover)
            VALUES (%s, %s, %s, %s, %s)
        """, (title, author, pages, publisher, cover))
        db_close(conn, cur)

        return redirect('/rgz/admin')

    return render_template('RGZ/rgz_book_form.html', book=None)

@RGZ.route('/rgz/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
def admin_edit_book(book_id):
    if session.get('role') != 'admin':
        return redirect('/rgz/login')

    conn, cur = db_connect()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        pages = request.form['pages']
        publisher = request.form['publisher']
        cover = request.form['cover']

        cur.execute("""
            UPDATE books
            SET title=%s, author=%s, pages=%s, publisher=%s, cover=%s
            WHERE id=%s
        """, (title, author, pages, publisher, cover, book_id))
        db_close(conn, cur)

        return redirect('/rgz/admin')

    cur.execute("SELECT * FROM books WHERE id=%s", (book_id,))
    book = cur.fetchone()
    db_close(conn, cur)

    return render_template('RGZ/rgz_book_form.html', book=book)


@RGZ.route('/rgz/admin/books/delete/<int:book_id>')
def admin_delete_book(book_id):
    if session.get('role') != 'admin':
        return redirect('/rgz/login')

    conn, cur = db_connect()
    cur.execute("DELETE FROM books WHERE id=%s", (book_id,))
    db_close(conn, cur)

    return redirect('/rgz/admin')