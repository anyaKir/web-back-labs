# lab8.py
from flask import Blueprint, render_template, request, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from db import db
from db.models import users, articles

lab8 = Blueprint('lab8', __name__, template_folder='templates')

@lab8.route('/lab8/')
def main():
    username = current_user.login if current_user.is_authenticated else 'anonymous'
    return render_template('lab8/lab8.html', username=username)

@lab8.route('/lab8/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    
    # Проверка на пустые значения
    if not login_form or not password_form:
        return render_template('lab8/register.html', 
                             error='Логин и пароль не могут быть пустыми')
    
    # Проверяем, существует ли пользователь
    user_exists = users.query.filter_by(login=login_form).first()
    if user_exists:
        return render_template('lab8/register.html',
                             error='Такой пользователь уже существует')
    
    # Хешируем пароль и создаем нового пользователя
    password_hash = generate_password_hash(password_form)
    new_user = users(login=login_form, password=password_hash)
    
    # Добавляем в БД
    db.session.add(new_user)
    db.session.commit()
    
    # Автоматически логиним пользователя после регистрации
    login_user(new_user)
    return redirect('/lab8/')

@lab8.route('/lab8/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    
    # Проверка на пустые значения
    if not login_form or not password_form:
        return render_template('lab8/login.html',
                             error='Логин и пароль не могут быть пустыми')
    
    # Ищем пользователя в БД
    user = users.query.filter_by(login=login_form).first()
    
    if user and check_password_hash(user.password, password_form):
        # Успешная авторизация
        login_user(user, remember=False)
        return redirect('/lab8/')
    else:
        # Неверные данные
        return render_template('lab8/login.html',
                             error='Неверный логин или пароль')

@lab8.route('/lab8/logout')
@login_required
def logout():
    logout_user()
    return redirect('/lab8/')

@lab8.route('/lab8/articles')
@login_required
def articles_list():
    # Пока просто заглушка - позже добавим вывод статей
    return render_template('lab8/articles.html')

@lab8.route('/lab8/create')
@login_required
def create_article():
    return render_template('lab8/create.html')