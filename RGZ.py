from flask import Blueprint, request, render_template, session, redirect, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import re
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path

RGZ = Blueprint('RGZ', __name__)
RGZ.secret_key = 'ваш-секретный-ключ-для-сессий-здесь'

def get_db_type():
    """Определяем тип базы данных"""
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='anna_kirdyachkina_knowledge_base',
            user='anna_kirdyachkina_knowledge_base',
            password='123'
        )
        conn.close()
        return 'postgres'
    except:
        return 'sqlite'

def db_connect():
    """Подключение к БД"""
    db_type = get_db_type()
    
    if db_type == 'postgres':
        try:
            conn = psycopg2.connect(
                host='127.0.0.1',
                database='anna_kirdyachkina_knowledge_base',
                user='anna_kirdyachkina_knowledge_base',
                password='123'
            )
            cur = conn.cursor(cursor_factory=RealDictCursor)
            return conn, cur, 'postgres'
        except Exception as e:
            print(f"Ошибка подключения к PostgreSQL: {e}")
            # Пробуем SQLite как запасной вариант
    
    # SQLite как запасной вариант
    try:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        return conn, cur, 'sqlite'
    except Exception as e:
        print(f"Ошибка подключения к SQLite: {e}")
        raise

def db_close(conn, cur):
    """Закрытие соединения с БД"""
    try:
        conn.commit()
    except:
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def execute_query(cur, query, params, db_type):
    """Универсальное выполнение запроса"""
    if db_type == 'postgres':
        cur.execute(query.replace('?', '%s'), params)
    else:
        cur.execute(query, params)

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
        where.append("title LIKE ?")
        args.append(f"%{title}%")

    if author:
        where.append("author LIKE ?")
        args.append(f"%{author}%")

    if publisher:
        where.append("publisher LIKE ?")
        args.append(f"%{publisher}%")

    if pages_from:
        where.append("pages >= ?")
        args.append(int(pages_from))

    if pages_to:
        where.append("pages <= ?")
        args.append(int(pages_to))

    sql = "SELECT * FROM books"
    if where:
        sql += " WHERE " + " AND ".join(where)

    if sort not in ['title','author','pages','publisher','title DESC','author DESC','pages DESC','publisher DESC']:
        sort = 'title'

    sql += f" ORDER BY {sort} LIMIT 20 OFFSET ?"
    args.append(offset)

    conn, cur, db_type = db_connect()
    execute_query(cur, sql, args, db_type)
    books = cur.fetchall()
    db_close(conn, cur)

    # Преобразуем Row в dict для JSON
    books_list = [dict(book) for book in books]
    return jsonify(books_list)

# ---------------- ВХОД ТОЛЬКО ДЛЯ АДМИНА ----------------
@RGZ.route('/rgz/login', methods=['GET','POST'])
def rgz_login():
    if request.method == 'GET':
        return render_template('RGZ/rgz_login.html')

    login = request.form.get('login')
    password = request.form.get('password')

    print(f"=== ДЕБАГ ВХОДА ===")
    print(f"Введён логин: '{login}'")
    print(f"Введён пароль: '{password}'")

    if not login or not password:
        return render_template('RGZ/rgz_login.html', error='Заполните все поля')

    conn, cur, db_type = db_connect()
    
    # Проверяем наличие таблицы usersbooks
    try:
        execute_query(cur, "SELECT * FROM usersbooks WHERE login=?", (login,), db_type)
        user = cur.fetchone()
    except Exception as e:
        print(f"Ошибка запроса пользователя: {e}")
        user = None
    
    db_close(conn, cur)

    if not user:
        print("Пользователь не найден")
        return render_template('RGZ/rgz_login.html', error='Пользователь не найден')

    # Преобразуем Row в dict
    user_dict = dict(user)
    print(f"Найден пользователь: {user_dict}")
    print(f"Хеш пароля в базе: {user_dict['password']}")
    print(f"Длина хеша: {len(user_dict['password'])}")

    # Проверяем пароль
    print(f"Проверяем пароль '{password}' с хешем...")
    
    # ДЛЯ ОТЛАДКИ - также сгенерируем хеш для введённого пароля
    test_hash = generate_password_hash(password)
    print(f"Новый хеш для введённого пароля: {test_hash}")
    
    if not check_password_hash(user_dict['password'], password):
        print(f"Хеши не совпадают!")
        return render_template('RGZ/rgz_login.html', error='Неверный пароль. Доступ только для администратора')

    print(f"Успешный вход! Роль: {user_dict['role']}")
    
    if user_dict['role'] != 'admin':
        return render_template('RGZ/rgz_login.html', error='Только администраторы могут входить')

    session['login'] = user_dict['login']
    session['role'] = user_dict['role']
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

    conn, cur, db_type = db_connect()
    execute_query(cur, "SELECT * FROM books ORDER BY id", [], db_type)
    books = cur.fetchall()
    db_close(conn, cur)

    # Преобразуем Row в dict для шаблона
    books_list = [dict(book) for book in books]
    
    return render_template(
        'RGZ/rgz_admin.html',
        books=books_list,
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
    
    conn, cur, db_type = db_connect()
    try:
        query = """
            INSERT INTO books (title, author, pages, publisher, cover)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (data['title'], data['author'], pages, data.get('publisher', ''), data.get('cover', '/static/RGZ/default-book.png'))
        
        execute_query(cur, query, params, db_type)
        
        if db_type == 'postgres':
            # Для PostgreSQL получаем ID через RETURNING
            cur.execute("SELECT lastval()")
            book_id = cur.fetchone()[0]
        else:
            # Для SQLite используем lastrowid
            book_id = cur.lastrowid
            
        db_close(conn, cur)
        return jsonify({'success': True, 'id': book_id})
    except Exception as e:
        db_close(conn, cur)
        return jsonify({'error': str(e)}), 500

@RGZ.route('/rgz/api/admin/books/<int:book_id>', methods=['PUT', 'DELETE'])
def api_admin_book(book_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    conn, cur, db_type = db_connect()
    
    if request.method == 'DELETE':
        try:
            execute_query(cur, "DELETE FROM books WHERE id=?", (book_id,), db_type)
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
            query = """
                UPDATE books 
                SET title=?, author=?, pages=?, publisher=?, cover=?
                WHERE id=?
            """
            params = (data['title'], data['author'], pages, data.get('publisher', ''), 
                      data.get('cover', '/static/RGZ/default-book.png'), book_id)
            
            execute_query(cur, query, params, db_type)
            db_close(conn, cur)
            return jsonify({'success': True})
        except Exception as e:
            db_close(conn, cur)
            return jsonify({'error': str(e)}), 500

# ---------------- СОЗДАНИЕ АДМИНА ----------------
@RGZ.route('/rgz/init_admin')
def init_admin():
    conn, cur, db_type = db_connect()
    
    # Удаляем если уже есть
    execute_query(cur, "DELETE FROM usersbooks WHERE login='admin'", [], db_type)
    
    # Создаем админа (пароль: admin123)
    hashed_password = generate_password_hash('admin123')
    execute_query(cur, "INSERT INTO usersbooks (login, password, role) VALUES (?, ?, 'admin')", 
                  ('admin', hashed_password), db_type)
    
    db_close(conn, cur)
    return "Админ создан: login: admin, password: admin123"

# ---------------- ФОРМЫ ДЛЯ АДМИНА ----------------
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

        conn, cur, db_type = db_connect()
        execute_query(cur, """
            INSERT INTO books (title, author, pages, publisher, cover)
            VALUES (?, ?, ?, ?, ?)
        """, (title, author, pages, publisher, cover), db_type)
        db_close(conn, cur)

        return redirect('/rgz/admin')

    return render_template('RGZ/rgz_book_form.html', book=None)

@RGZ.route('/rgz/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
def admin_edit_book(book_id):
    if session.get('role') != 'admin':
        return redirect('/rgz/login')

    conn, cur, db_type = db_connect()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        pages = request.form['pages']
        publisher = request.form['publisher']
        cover = request.form['cover']

        execute_query(cur, """
            UPDATE books
            SET title=?, author=?, pages=?, publisher=?, cover=?
            WHERE id=?
        """, (title, author, pages, publisher, cover, book_id), db_type)
        db_close(conn, cur)

        return redirect('/rgz/admin')

    execute_query(cur, "SELECT * FROM books WHERE id=?", (book_id,), db_type)
    book = cur.fetchone()
    db_close(conn, cur)

    if book:
        book = dict(book)  # Преобразуем Row в dict
    
    return render_template('RGZ/rgz_book_form.html', book=book)

@RGZ.route('/rgz/admin/books/delete/<int:book_id>')
def admin_delete_book(book_id):
    if session.get('role') != 'admin':
        return redirect('/rgz/login')

    conn, cur, db_type = db_connect()
    execute_query(cur, "DELETE FROM books WHERE id=?", (book_id,), db_type)
    db_close(conn, cur)

    return redirect('/rgz/admin')

# ---------------- ТЕСТОВЫЕ ЭНДПОИНТЫ ----------------
@RGZ.route('/rgz/test')
def test_db():
    """Тестовый эндпоинт для проверки базы данных"""
    try:
        conn, cur, db_type = db_connect()
        
        # Проверяем usersbooks
        execute_query(cur, "SELECT COUNT(*) as user_count FROM usersbooks", [], db_type)
        user_result = cur.fetchone()
        user_count = user_result['user_count'] if user_result else 0
        
        # Проверяем books
        execute_query(cur, "SELECT COUNT(*) as book_count FROM books", [], db_type)
        book_result = cur.fetchone()
        book_count = book_result['book_count'] if book_result else 0
        
        # Показываем несколько книг
        execute_query(cur, "SELECT title, author FROM books LIMIT 3", [], db_type)
        sample_books = cur.fetchall()
        
        db_close(conn, cur)
        
        result = {
            "status": "ok",
            "db_type": db_type,
            "users": user_count,
            "books": book_count,
            "sample_books": [dict(book) for book in sample_books] if sample_books else []
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@RGZ.route('/rgz/check_tables')
def check_tables():
    """Проверка наличия таблиц"""
    try:
        conn, cur, db_type = db_connect()
        
        tables = []
        if db_type == 'postgres':
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
        else:
            # SQLite
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        
        for row in cur.fetchall():
            tables.append(row[0])
        
        db_close(conn, cur)
        
        return jsonify({
            "status": "ok",
            "db_type": db_type,
            "tables": tables
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})