# lab8.py
from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from db.models import users, articles

lab8 = Blueprint('lab8', __name__, template_folder='templates')

@lab8.route('/lab8/')
def main():
    # Показываем 'anonymous' или имя залогиненного пользователя
    username = session.get('login', 'anonymous')
    return render_template('lab8/lab8.html', username=username)

@lab8.route('/lab8/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')
    
    # Получаем данные из формы
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    
    # Проверка на пустые значения
    if not login_form or not password_form:
        return render_template('lab8/register.html', 
                             error='Логин и пароль не могут быть пустыми')
    
    # Проверяем, существует ли пользователь
    login_exists = users.query.filter_by(login=login_form).first()
    if login_exists:
        return render_template('lab8/register.html',
                             error='Такой пользователь уже существует')
    
    # Хешируем пароль и создаем нового пользователя
    password_hash = generate_password_hash(password_form)
    new_user = users(login=login_form, password=password_hash)
    
    # Добавляем в БД
    db.session.add(new_user)
    db.session.commit()
    
    # Автоматически логиним пользователя после регистрации
    session['login'] = login_form
    return redirect('/lab8/')

# Остальные маршруты пока оставляем простыми
@lab8.route('/lab8/login')
def login():
    return render_template('lab8/login.html')

@lab8.route('/lab8/articles')
def articles_list():
    return render_template('lab8/articles.html')

@lab8.route('/lab8/create')
def create_article():
    return render_template('lab8/create.html')

@lab8.route('/lab8/logout')
def logout():
    session.pop('login', None)
    return redirect('/lab8/')