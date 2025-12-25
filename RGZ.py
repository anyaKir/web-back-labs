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
    """Определяем тип базы данных - на PythonAnywhere всегда SQLite"""
    return 'sqlite'  # На PythonAnywhere используем только SQLite

def db_connect():
    """Подключение к SQLite базе"""
    try:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        print(f"DEBUG: Подключаемся к базе по пути: {db_path}")
        
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
    try:
        conn, cur, db_type = db_connect()
        
        # Сначала проверяем, есть ли таблица books
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
        if not cur.fetchone():
            db_close(conn, cur)
            return jsonify([])
        
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

        print(f"DEBUG: Выполняем SQL: {sql}")
        print(f"DEBUG: Параметры: {args}")
        
        cur.execute(sql, args)
        books = cur.fetchall()
        db_close(conn, cur)

        # Преобразуем Row в dict для JSON
        books_list = [dict(book) for book in books]
        print(f"DEBUG: Найдено книг: {len(books_list)}")
        return jsonify(books_list)
        
    except Exception as e:
        print(f"ERROR в api_books: {e}")
        return jsonify([])

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

    try:
        conn, cur, db_type = db_connect()
        
        # Проверяем существование таблицы usersbooks
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='usersbooks' OR name='Usersbooks' OR name='USERSBOOKS')")
        tables = cur.fetchall()
        print(f"DEBUG: Найдены таблицы: {tables}")
        
        # Ищем таблицу в любом регистре
        table_name = None
        for table in tables:
            if 'usersbooks' in table[0].lower():
                table_name = table[0]
                break
        
        if not table_name:
            print("ERROR: Таблица usersbooks не найдена!")
            db_close(conn, cur)
            return render_template('RGZ/rgz_login.html', error='Ошибка базы данных')
        
        print(f"DEBUG: Используем таблицу: {table_name}")
        
        # Выполняем запрос с правильным именем таблицы
        cur.execute(f"SELECT * FROM {table_name} WHERE login=?", (login,))
        user = cur.fetchone()
        
        if user:
            user_dict = dict(user)
            print(f"DEBUG: Найден пользователь: {user_dict}")
        else:
            print(f"DEBUG: Пользователь {login} не найден")
            
        db_close(conn, cur)

        if not user:
            return render_template('RGZ/rgz_login.html', error='Пользователь не найден')

        # Проверяем пароль
        print(f"DEBUG: Проверяем пароль...")
        
        # Используем scrypt метод для генерации нового хеша при необходимости
        try:
            if user_dict['password'].startswith('$2b$'):
                # Старый bcrypt хеш
                if not check_password_hash(user_dict['password'], password):
                    print(f"DEBUG: Пароль неверный (bcrypt)")
                    return render_template('RGZ/rgz_login.html', error='Неверный пароль')
            else:
                # Предполагаем scrypt или другой метод
                new_hash = generate_password_hash(password, method='scrypt')
                if not check_password_hash(new_hash, password):
                    print(f"DEBUG: Пароль неверный (scrypt)")
                    return render_template('RGZ/rgz_login.html', error='Неверный пароль')
                
        except Exception as e:
            print(f"ERROR при проверке пароля: {e}")
            return render_template('RGZ/rgz_login.html', error='Ошибка проверки пароля')

        print(f"DEBUG: Успешный вход! Роль: {user_dict.get('role', 'unknown')}")
        
        if user_dict.get('role') != 'admin':
            return render_template('RGZ/rgz_login.html', error='Только администраторы могут входить')

        session['login'] = user_dict['login']
        session['role'] = user_dict['role']
        return redirect('/rgz/')
        
    except Exception as e:
        print(f"ERROR в rgz_login: {e}")
        return render_template('RGZ/rgz_login.html', error='Ошибка сервера')

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

    try:
        conn, cur, db_type = db_connect()
        cur.execute("SELECT * FROM books ORDER BY id")
        books = cur.fetchall()
        db_close(conn, cur)

        books_list = [dict(book) for book in books]
        
        return render_template(
            'RGZ/rgz_admin.html',
            books=books_list,
            login=session.get('login')
        )
    except Exception as e:
        print(f"ERROR в rgz_admin: {e}")
        return "Ошибка загрузки админ-панели"

# ---------------- ДОБАВЛЕНИЕ КНИГИ ----------------
@RGZ.route('/rgz/admin/books/add', methods=['GET', 'POST'])
def rgz_add_book():
    if session.get('role') != 'admin':
        return redirect('/rgz/login')
    
    if request.method == 'GET':
        return render_template('RGZ/rgz_book_form.html')
    
    # Обработка POST запроса
    try:
        title = request.form.get('title')
        author = request.form.get('author')
        pages = request.form.get('pages')
        publisher = request.form.get('publisher')
        cover = request.form.get('cover')
        
        if not title or not author or not pages:
            return "Заполните обязательные поля", 400
        
        conn, cur, db_type = db_connect()
        cur.execute(
            """
            INSERT INTO books (title, author, pages, publisher, cover)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                title,
                author,
                int(pages),
                publisher or None,
                cover if cover else None   # ← ВАЖНО
            )
        )
        conn.commit()
        db_close(conn, cur)
        
        return redirect('/rgz/admin')
        
    except Exception as e:
        print(f"ERROR в rgz_add_book: {e}")
        return f"Ошибка: {e}", 500

# ---------------- РЕДАКТИРОВАНИЕ КНИГИ ----------------
@RGZ.route('/rgz/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
def rgz_edit_book(book_id):
    if session.get('role') != 'admin':
        return redirect('/rgz/login')
    
    try:
        conn, cur, db_type = db_connect()
        
        if request.method == 'GET':
            cur.execute("SELECT * FROM books WHERE id = ?", (book_id,))
            book = cur.fetchone()
            db_close(conn, cur)
            
            if not book:
                return "Книга не найдена", 404
            
            return render_template('RGZ/rgz_book_form.html', book=dict(book))
        
        # Обработка POST запроса
        title = request.form.get('title')
        author = request.form.get('author')
        pages = request.form.get('pages')
        publisher = request.form.get('publisher')
        cover = request.form.get('cover')
        
        if not title or not author or not pages:
            return "Заполните обязательные поля", 400
        
        cur.execute("""
            UPDATE books 
            SET title = ?, author = ?, pages = ?, publisher = ?, cover = ?
            WHERE id = ?
        """, (title, author, int(pages), publisher or None, cover if cover else None, book_id))
        
        conn.commit()
        db_close(conn, cur)
        
        return redirect('/rgz/admin')
        
    except Exception as e:
        print(f"ERROR в rgz_edit_book: {e}")
        return f"Ошибка: {e}", 500

# ---------------- УДАЛЕНИЕ КНИГИ ----------------
@RGZ.route('/rgz/admin/books/delete/<int:book_id>')
def rgz_delete_book(book_id):
    if session.get('role') != 'admin':
        return redirect('/rgz/login')
    
    try:
        conn, cur, db_type = db_connect()
        cur.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        db_close(conn, cur)
        
        return redirect('/rgz/admin')
        
    except Exception as e:
        print(f"ERROR в rgz_delete_book: {e}")
        return f"Ошибка: {e}", 500
    

@RGZ.route('/rgz/simple_books')
def simple_books():
    """Простой вывод книг без JavaScript"""
    try:
        conn, cur, db_type = db_connect()
        cur.execute("SELECT * FROM books LIMIT 20")
        books = [dict(row) for row in cur.fetchall()]
        db_close(conn, cur)
        
        return render_template('RGZ/simple_books.html', 
                             books=books,
                             login=session.get('login'),
                             role=session.get('role'))
    except Exception as e:
        return f"Ошибка: {e}"