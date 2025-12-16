from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for, current_app
import random
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path

lab9 = Blueprint('lab9', __name__)

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

def is_authenticated():
    """Проверка, авторизован ли пользователь"""
    return session.get('user_authenticated', False)

def generate_non_overlapping_positions():
    """Генерация случайных непересекающихся позиций для коробок"""
    positions = []
    attempts = 0
    max_attempts = 1000
    box_width = 10  # Ширина коробки в процентах
    box_height = 10  # Высота коробки в процентах
    
    while len(positions) < 10 and attempts < max_attempts:
        # Генерируем случайные позиции в процентах от 5% до 85%
        top = random.randint(5, 85 - box_height)
        left = random.randint(5, 85 - box_width)
        
        # Проверяем, не пересекается ли новая позиция с существующими
        overlap = False
        for t, l in positions:
            # Проверка пересечения: если расстояния по вертикали и горизонтали меньше размеров коробки
            if (abs(top - t) < box_height and abs(left - l) < box_width):
                overlap = True
                break
        
        if not overlap:
            positions.append((top, left))
        
        attempts += 1
    
    # Если не удалось сгенерировать 10 непересекающихся позиций,
    # добавляем оставшиеся со случайными позициями
    while len(positions) < 10:
        top = random.randint(5, 85 - box_height)
        left = random.randint(5, 85 - box_width)
        positions.append((top, left))
    
    return positions

@lab9.route('/lab9/')
def main():
    conn, cur, db_type = db_connect()
    
    # Создаем ID пользователя если его нет
    if 'lab9_user_id' not in session:
        session['lab9_user_id'] = str(uuid.uuid4())
    user_id = session['lab9_user_id']
    
    # Проверяем аутентификацию
    is_auth = is_authenticated()
    auth_user_id = session.get('auth_user_id')
    
    # Создаем запись пользователя если её нет
    if db_type == 'postgres':
        cur.execute("SELECT id FROM lab9_users WHERE id = %s", (user_id,))
    else:
        cur.execute("SELECT id FROM lab9_users WHERE id = ?", (user_id,))
    
    if not cur.fetchone():
        if db_type == 'postgres':
            cur.execute("INSERT INTO lab9_users (id, auth_user_id) VALUES (%s, %s)", 
                       (user_id, auth_user_id))
        else:
            cur.execute("INSERT INTO lab9_users (id, auth_user_id) VALUES (?, ?)", 
                       (user_id, auth_user_id))
    
    # Проверяем есть ли подарки для этого пользователя
    if db_type == 'postgres':
        cur.execute("SELECT COUNT(*) as cnt FROM lab9_gifts WHERE user_id = %s", (user_id,))
    else:
        cur.execute("SELECT COUNT(*) as cnt FROM lab9_gifts WHERE user_id = ?", (user_id,))
    
    gift_count = cur.fetchone()['cnt']
    
    # Если подарков нет - создаем их
    if gift_count == 0:
        messages = [
            "С Новым годом!",
            "Счастья, удачи!",
            "Успехов в работе и творчестве!",
            "Счастья, радости и тепла в вашем доме!",
            "Всего хорошего!",
            "Кайф, успех!",
            "Вперед, к целям!",
            "Здоровья, счастья!",
            "Праздничного настроения!",
            "Удачной сессии!"
        ]
        
        # Проверяем правильные пути к изображениям
        gift_images = [f"gift{i+1}.png" for i in range(10)]
        box_images = [f"box{i+1}.png" for i in range(10)]
        
        positions = generate_non_overlapping_positions()
        
        for i in range(10):
            top, left = positions[i]
            require_auth = i >= 5  # Последние 5 подарков требуют авторизации
            params = (user_id, i, top, left, messages[i], 
                     gift_images[i], box_images[i], require_auth)
            
            if db_type == 'postgres':
                cur.execute("""
                    INSERT INTO lab9_gifts 
                    (user_id, position_id, top_position, left_position, message, image, box_image, require_auth)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, params)
            else:
                cur.execute("""
                    INSERT INTO lab9_gifts 
                    (user_id, position_id, top_position, left_position, message, image, box_image, require_auth)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, params)
    
    # Получаем все подарки пользователя
    if db_type == 'postgres':
        cur.execute("""
            SELECT position_id, top_position, left_position, opened, message, 
                   image, box_image, require_auth 
            FROM lab9_gifts 
            WHERE user_id = %s 
            ORDER BY position_id
        """, (user_id,))
    else:
        cur.execute("""
            SELECT position_id, top_position, left_position, opened, message, 
                   image, box_image, require_auth 
            FROM lab9_gifts 
            WHERE user_id = ? 
            ORDER BY position_id
        """, (user_id,))
    
    gifts = cur.fetchall()
    
    # Считаем открытые подарки
    if db_type == 'postgres':
        cur.execute("SELECT COUNT(*) as cnt FROM lab9_gifts WHERE user_id = %s AND opened = TRUE", (user_id,))
    else:
        cur.execute("SELECT COUNT(*) as cnt FROM lab9_gifts WHERE user_id = ? AND opened = TRUE", (user_id,))
    
    opened_count = cur.fetchone()['cnt']
    
    # Определяем сколько можно еще открыть
    max_allowed = 10 if is_auth else 3
    remaining = max(0, max_allowed - opened_count)
    
    db_close(conn, cur)
    
    return render_template('lab9/index.html', 
                         gifts=gifts, 
                         opened_count=opened_count, 
                         remaining=remaining, 
                         is_auth=is_auth,
                         login=session.get('login'))

@lab9.route('/lab9/open_gift', methods=['POST'])
def open_gift():
    user_id = session.get('lab9_user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Пользователь не найден'})
    
    data = request.get_json()
    if not data or 'gift_id' not in data:
        return jsonify({'success': False, 'message': 'Не указан ID подарка'})
    
    gift_id = data['gift_id']
    is_auth = is_authenticated()
    
    conn, cur, db_type = db_connect()
    
    try:
        # Получаем информацию о подарке
        if db_type == 'postgres':
            cur.execute("""
                SELECT opened, require_auth 
                FROM lab9_gifts 
                WHERE user_id = %s AND position_id = %s
            """, (user_id, gift_id))
        else:
            cur.execute("""
                SELECT opened, require_auth 
                FROM lab9_gifts 
                WHERE user_id = ? AND position_id = ?
            """, (user_id, gift_id))
        
        gift = cur.fetchone()
        if not gift:
            return jsonify({'success': False, 'message': 'Подарок не найден'})
        
        if gift['opened']:
            return jsonify({'success': False, 'message': 'Этот подарок уже открыт!'})
        
        if gift['require_auth'] and not is_auth:
            return jsonify({'success': False, 'message': 'Требуется авторизация для этого подарка!'})
        
        # Проверяем сколько уже открыто
        if db_type == 'postgres':
            cur.execute("SELECT COUNT(*) as cnt FROM lab9_gifts WHERE user_id = %s AND opened = TRUE", (user_id,))
        else:
            cur.execute("SELECT COUNT(*) as cnt FROM lab9_gifts WHERE user_id = ? AND opened = TRUE", (user_id,))
        
        opened_count = cur.fetchone()['cnt']
        max_allowed = 10 if is_auth else 3
        
        if opened_count >= max_allowed:
            return jsonify({'success': False, 
                          'message': f'Можно открыть только {max_allowed} подарка(ов)!'})
        
        # Открываем подарок
        if db_type == 'postgres':
            cur.execute("""
                UPDATE lab9_gifts 
                SET opened = TRUE 
                WHERE user_id = %s AND position_id = %s
                RETURNING message, image
            """, (user_id, gift_id))
        else:
            cur.execute("""
                UPDATE lab9_gifts 
                SET opened = TRUE 
                WHERE user_id = ? AND position_id = ?
            """, (user_id, gift_id))
            
            # SQLite не поддерживает RETURNING, делаем отдельный запрос
            cur.execute("""
                SELECT message, image 
                FROM lab9_gifts 
                WHERE user_id = ? AND position_id = ?
            """, (user_id, gift_id))
        
        result = cur.fetchone()
        
        new_opened_count = opened_count + 1
        remaining = max(0, max_allowed - new_opened_count)
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': result['message'],
            'image': f"/static/lab9/{result['image']}",
            'opened_count': new_opened_count,
            'remaining': remaining
        })
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при открытии подарка: {e}")
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})
    
    finally:
        db_close(conn, cur)

@lab9.route('/lab9/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab9/login.html')
    
    login_val = request.form.get('login')
    password = request.form.get('password')
    
    if not login_val or not password:
        return render_template('lab9/login.html', error='Заполните все поля')
    
    conn, cur, db_type = db_connect()
    
    try:
        if db_type == 'postgres':
            cur.execute("SELECT id, password FROM lab9_auth_users WHERE login = %s", (login_val,))
        else:
            cur.execute("SELECT id, password FROM lab9_auth_users WHERE login = ?", (login_val,))
        
        user = cur.fetchone()
        
        if not user:
            return render_template('lab9/login.html', error='Неверный логин или пароль')
        
        if not check_password_hash(user['password'], password):
            return render_template('lab9/login.html', error='Неверный логин или пароль')
        
        # Сохраняем данные в сессии
        session['user_authenticated'] = True
        session['login'] = login_val
        session['auth_user_id'] = user['id']
        
        return redirect('/lab9/')
        
    except Exception as e:
        print(f"Ошибка входа: {e}")
        return render_template('lab9/login.html', error='Ошибка сервера')
    
    finally:
        db_close(conn, cur)

@lab9.route('/lab9/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab9/register.html')
    
    login_val = request.form.get('login')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([login_val, password, confirm_password]):
        return render_template('lab9/register.html', error='Заполните все поля')
    
    if password != confirm_password:
        return render_template('lab9/register.html', error='Пароли не совпадают')
    
    if len(password) < 4:
        return render_template('lab9/register.html', error='Пароль должен быть не менее 4 символов')
    
    conn, cur, db_type = db_connect()
    
    try:
        # Проверяем существование пользователя
        if db_type == 'postgres':
            cur.execute("SELECT id FROM lab9_auth_users WHERE login = %s", (login_val,))
        else:
            cur.execute("SELECT id FROM lab9_auth_users WHERE login = ?", (login_val,))
        
        if cur.fetchone():
            return render_template('lab9/register.html', error='Логин уже занят')
        
        # Хешируем пароль
        password_hash = generate_password_hash(password)
        
        # Создаем пользователя
        if db_type == 'postgres':
            cur.execute("""
                INSERT INTO lab9_auth_users (login, password) 
                VALUES (%s, %s) 
                RETURNING id
            """, (login_val, password_hash))
        else:
            cur.execute("""
                INSERT INTO lab9_auth_users (login, password) 
                VALUES (?, ?)
            """, (login_val, password_hash))
            
            cur.execute("SELECT last_insert_rowid() as id")
        
        user_id = cur.fetchone()['id']
        
        # Авторизуем
        session['user_authenticated'] = True
        session['login'] = login_val
        session['auth_user_id'] = user_id
        
        conn.commit()
        return redirect('/lab9/')
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка регистрации: {e}")
        return render_template('lab9/register.html', error='Ошибка сервера')
    
    finally:
        db_close(conn, cur)

@lab9.route('/lab9/logout')
def logout():
    session.pop('user_authenticated', None)
    session.pop('login', None)
    session.pop('auth_user_id', None)
    return redirect('/lab9/')

@lab9.route('/lab9/santa', methods=['POST'])
def santa():
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Только для авторизованных пользователей!'})
    
    user_id = session.get('lab9_user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Пользователь не найден'})
    
    conn, cur, db_type = db_connect()
    
    try:
        # Генерируем новые позиции
        positions = generate_non_overlapping_positions()
        
        # Сбрасываем все подарки
        for i in range(10):
            top, left = positions[i]
            if db_type == 'postgres':
                cur.execute("""
                    UPDATE lab9_gifts 
                    SET opened = FALSE, top_position = %s, left_position = %s
                    WHERE user_id = %s AND position_id = %s
                """, (top, left, user_id, i))
            else:
                cur.execute("""
                    UPDATE lab9_gifts 
                    SET opened = FALSE, top_position = ?, left_position = ?
                    WHERE user_id = ? AND position_id = ?
                """, (top, left, user_id, i))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '🎅 Дед Мороз наполнил все подарки заново!'
        })
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка сброса подарков: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при сбросе подарков'})
    
    finally:
        db_close(conn, cur)