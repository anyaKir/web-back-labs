from flask import Blueprint, url_for, request, redirect, render_template, abort
import datetime
import psycopg2

lab5 = Blueprint('lab5', __name__)


@lab5.route('/lab5/')
def main():
    return render_template('lab5/lab5.html')


@lab5.route('/lab5/login')
def login():
    return "Страница входа"


@lab5.route('/lab5/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')

    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return render_template('lab5/register.html', error='Заполните все поля')

    conn = psycopg2.connect(
        host='127.0.0.1',
        database='anna_kirdyachkina_knowledge_base',
        user='anna_kirdyachkina_knowledge_base', 
        password='123'
    )
    cur = conn.cursor()

   
    cur.execute("SELECT login FROM users WHERE login=%s;", (login,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return render_template('lab5/register.html',
                                error="Такой пользователь уже существует")


    cur.execute("INSERT INTO users (login, password) VALUES (%s, %s);", (login, password))
    conn.commit()
    cur.close()
    conn.close()
    return render_template('lab5/success.html', login=login)


@lab5.route('/lab5/list')
def list_articles():
    return render_template('lab5/list.html')


@lab5.route('/lab5/create')
def create_article():
    return render_template('lab5/create.html')
