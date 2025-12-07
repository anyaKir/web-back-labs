from flask import Blueprint, render_template, request, abort, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from os import path
import sqlite3
from datetime import datetime
import json

lab7 = Blueprint('lab7', __name__)

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

def validate_film(film):
    errors = {}
    current_year = datetime.now().year

    title = film.get('title', '').strip()
    title_ru = film.get('title_ru', '').strip()

    if not title and not title_ru:
        errors['title'] = 'Необходимо указать хотя бы одно название: оригинальное или русское'
    if not title and title_ru:
        title = title_ru

    try:
        year_int = int(film.get('year', 0))
        if year_int < 1895:
            errors['year'] = 'Год фильма не может быть раньше 1895'
        elif year_int > current_year:
            errors['year'] = f'Год фильма не может быть больше {current_year}'
    except (ValueError, TypeError):
        errors['year'] = 'Год фильма должен быть числом'

    description = film.get('description', '').strip()
    if not description:
        errors['description'] = 'Описание обязательно для заполнения'
    elif len(description) > 2000:
        errors['description'] = f'Описание не должно превышать 2000 символов (сейчас: {len(description)})'

    validated_film = {
        'title': title,
        'title_ru': title_ru,
        'year': year_int if 'year_int' in locals() else 0,
        'description': description
    }

    return errors, validated_film


@lab7.route('/lab7/')
def main():
    return render_template('lab7/index.html')


@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    conn, cur = db_connect()
    cur.execute("SELECT id, title, title_ru, year, description FROM movies ORDER BY id")
    films = [dict(row) for row in cur.fetchall()]
    db_close(conn, cur)
    return json.dumps(films, ensure_ascii=False), 200, {'Content-Type': 'application/json'}


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id, title, title_ru, year, description FROM movies WHERE id = %s", (id,))
        film = cur.fetchone()
        db_close(conn, cur)
        if not film:
            abort(404)
        return json.dumps(dict(film), ensure_ascii=False), 200, {'Content-Type': 'application/json'}
    else:
        cur.execute("SELECT id, title, title_ru, year, description FROM movies WHERE id = ?", (id,))
        film = cur.fetchone()
        db_close(conn, cur)
        if not film:
            abort(404)
        return json.dumps(dict(film), ensure_ascii=False), 200, {'Content-Type': 'application/json'}
    

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    film = request.get_json()
    errors, validated_film = validate_film(film)
    if errors:
        return json.dumps(errors, ensure_ascii=False), 400, {'Content-Type': 'application/json'}

    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM movies WHERE id = %s", (id,))
    else:
        cur.execute("SELECT id FROM movies WHERE id = ?", (id,))
    
    if not cur.fetchone():
        db_close(conn, cur)
        abort(404)
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            UPDATE movies 
            SET title = %s, title_ru = %s, year = %s, description = %s 
            WHERE id = %s
        """, (validated_film['title'], validated_film['title_ru'],
              validated_film['year'], validated_film['description'], id))
    else:
        cur.execute("""
            UPDATE movies 
            SET title = ?, title_ru = ?, year = ?, description = ? 
            WHERE id = ?
        """, (validated_film['title'], validated_film['title_ru'],
              validated_film['year'], validated_film['description'], id))
    db_close(conn, cur)
    
    validated_film['id'] = id
    return json.dumps(validated_film, ensure_ascii=False), 200, {'Content-Type': 'application/json'}


@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()
    errors, validated_film = validate_film(film)
    if errors:
        return json.dumps(errors, ensure_ascii=False), 400, {'Content-Type': 'application/json'}

    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            INSERT INTO movies (title, title_ru, year, description)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (validated_film['title'], validated_film['title_ru'],
              validated_film['year'], validated_film['description']))
        new_id = cur.fetchone()['id']
    else:
        cur.execute("""
            INSERT INTO movies (title, title_ru, year, description)
            VALUES (?, ?, ?, ?)
        """, (validated_film['title'], validated_film['title_ru'],
              validated_film['year'], validated_film['description']))
        new_id = cur.lastrowid

    db_close(conn, cur)
    return json.dumps({"id": new_id}, ensure_ascii=False), 201, {'Content-Type': 'application/json'}


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM movies WHERE id = %s", (id,))
    else:
        cur.execute("DELETE FROM movies WHERE id = ?", (id,))
    db_close(conn, cur)
    return '', 204