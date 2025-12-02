from flask import Blueprint, request, render_template, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path

lab6 = Blueprint('lab6', __name__)

def db_connect():
    if current_app.config.get('DB_TYPE') == 'postgres':
        # Подключение к PostgreSQL
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='anna_kirdyachkina_knowledge_base',
            user='anna_kirdyachkina_knowledge_base',
            password='123'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        # Подключение к SQLite (для PythonAnywhere)
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

def error_response(id, code, message):
    return {
        'jsonrpc': '2.0',
        'error': {
            'code': code,
            'message': message
        },
        'id': id
    }

@lab6.route('/lab6/')
def main():
    return render_template('lab6/lab6.html')

@lab6.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    data = request.json
    id = data.get('id')
    method = data.get('method')
    
    if not id or not method:
        return error_response(id or None, -32600, 'Invalid Request')
    
    if method == 'info':
        conn, cur = db_connect()
        
        # Для SQLite используем ?, для PostgreSQL — %s
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("SELECT number, tenant, price FROM offices ORDER BY number")
        else:
            cur.execute("SELECT number, tenant, price FROM offices ORDER BY number")
        
        offices_db = cur.fetchall()
        db_close(conn, cur)
        
        # Преобразуем в список словарей
        result = []
        for office in offices_db:
            # Проверяем тип объекта (PostgreSQL или SQLite)
            if hasattr(office, 'get'):  # PostgreSQL с RealDictCursor
                tenant = office.get('tenant') if office.get('tenant') else ""
                result.append({
                    "number": office.get('number'),
                    "tenant": tenant,
                    "price": office.get('price')
                })
            else:  # SQLite с row_factory
                tenant = office['tenant'] if office['tenant'] else ""
                result.append({
                    "number": office['number'],
                    "tenant": tenant,
                    "price": office['price']
                })
        
        return {
            'jsonrpc': '2.0',
            'result': result,
            'id': id
        }
    
    login = session.get('login')
    if not login:
        return error_response(id, 1, 'Unauthorized')
    
    if method == 'booking':
        office_number = data.get('params')
        if not office_number:
            return error_response(id, -32602, 'Invalid params')
        
        conn, cur = db_connect()
        
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("SELECT tenant FROM offices WHERE number = %s", (office_number,))
        else:
            cur.execute("SELECT tenant FROM offices WHERE number = ?", (office_number,))
        
        office = cur.fetchone()
        
        if not office:
            db_close(conn, cur)
            return error_response(id, 3, 'Office not found')
        
        # Проверяем тип объекта
        if hasattr(office, 'get'):
            tenant = office.get('tenant')
        else:
            tenant = office['tenant']
        
        if tenant:
            db_close(conn, cur)
            return error_response(id, 2, 'Already booked')
        
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("UPDATE offices SET tenant = %s WHERE number = %s", 
                        (login, office_number))
        else:
            cur.execute("UPDATE offices SET tenant = ? WHERE number = ?", 
                        (login, office_number))
        
        db_close(conn, cur)
        
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }
    
    if method == 'cancellation':
        office_number = data.get('params')
        if not office_number:
            return error_response(id, -32602, 'Invalid params')
        
        conn, cur = db_connect()
        
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("SELECT tenant FROM offices WHERE number = %s", (office_number,))
        else:
            cur.execute("SELECT tenant FROM offices WHERE number = ?", (office_number,))
        
        office = cur.fetchone()
        
        if not office:
            db_close(conn, cur)
            return error_response(id, 3, 'Office not found')
        
        # Проверяем тип объекта
        if hasattr(office, 'get'):
            tenant = office.get('tenant')
        else:
            tenant = office['tenant']
        
        if not tenant:
            db_close(conn, cur)
            return error_response(id, 4, 'Office is not booked')
        
        if tenant != login:
            db_close(conn, cur)
            return error_response(id, 5, 'Not your booking')
        
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("UPDATE offices SET tenant = NULL WHERE number = %s", 
                        (office_number,))
        else:
            cur.execute("UPDATE offices SET tenant = NULL WHERE number = ?", 
                        (office_number,))
        
        db_close(conn, cur)
        
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }
    
    return { 
        'jsonrpc': '2.0', 
        'error': { 
            'code': -32601, 
            'message': 'Method not found' 
        }, 
        'id': id 
    }


