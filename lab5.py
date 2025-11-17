from flask import Blueprint, render_template

lab5 = Blueprint('lab5', __name__)

@lab5.route('/')
def main():
    return render_template('lab5/lab5.html')

@lab5.route('/login')
def login():
    return "Страница входа"

@lab5.route('/register')
def register():
    return "Страница регистрации"

@lab5.route('/list')
def list_articles():
    return "Список статей"

@lab5.route('/create')
def create_article():
    return "Создать статью"
