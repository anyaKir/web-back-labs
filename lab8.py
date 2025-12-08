from flask import Blueprint, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from db import db
from db.models import users, articles
from sqlalchemy import or_, func

lab8 = Blueprint('lab8', __name__, template_folder='templates')


def get_username():
    return current_user.login if current_user.is_authenticated else 'anonymous'


def search_articles_query(search_pattern, user_id=None, only_public=False):
    query = articles.query
    conditions = or_(
        func.lower(articles.title).like(func.lower(search_pattern)),
        func.lower(articles.article_text).like(func.lower(search_pattern))
    )

    if user_id is not None:
        query = query.filter(articles.login_id == user_id, conditions)
    elif only_public:
        query = query.filter(articles.is_public == True, conditions)
    else:
        query = query.filter(conditions)

    return query.all()


@lab8.route('/lab8/')
def main():
    return render_template('lab8/lab8.html', username=get_username())


@lab8.route('/lab8/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')

    login_form = request.form.get('login')
    password_form = request.form.get('password')

    if not login_form or not password_form:
        return render_template('lab8/register.html', error='Логин и пароль не могут быть пустыми')

    if users.query.filter_by(login=login_form).first():
        return render_template('lab8/register.html', error='Такой пользователь уже существует')

    new_user = users(login=login_form, password=generate_password_hash(password_form))
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return redirect('/lab8/')


@lab8.route('/lab8/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')

    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember = request.form.get('remember') == 'on'

    if not login_form or not password_form:
        return render_template('lab8/login.html', error='Логин и пароль не могут быть пустыми')

    user = users.query.filter_by(login=login_form).first()
    if user and check_password_hash(user.password, password_form):
        login_user(user, remember=remember)
        return redirect('/lab8/')

    return render_template('lab8/login.html', error='Неверный логин или пароль')


@lab8.route('/lab8/logout')
@login_required
def logout():
    logout_user()
    return redirect('/lab8/')


@lab8.route('/lab8/articles')
@login_required
def articles_list():
    user_articles = articles.query.filter_by(login_id=current_user.id).all()
    public_articles = articles.query.filter(
        articles.is_public == True,
        articles.login_id != current_user.id
    ).all()
    return render_template('lab8/articles.html', articles=user_articles, public_articles=public_articles)


@lab8.route('/lab8/public')
def public_articles():
    all_public = articles.query.filter_by(is_public=True).all()
    return render_template('lab8/public.html', articles=all_public, username=get_username())


@lab8.route('/lab8/create', methods=['GET', 'POST'])
@login_required
def create_article():
    if request.method == 'GET':
        return render_template('lab8/create.html')

    title = request.form.get('title')
    article_text = request.form.get('article_text')
    if not title or not article_text:
        return render_template('lab8/create.html', error='Заголовок и текст статьи обязательны')

    new_article = articles(
        login_id=current_user.id,
        title=title,
        article_text=article_text,
        is_public=request.form.get('is_public') == 'on',
        is_favorite=request.form.get('is_favorite') == 'on',
        likes=0
    )

    db.session.add(new_article)
    db.session.commit()
    return redirect('/lab8/articles')


@lab8.route('/lab8/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = articles.query.get_or_404(article_id)
    if article.login_id != current_user.id:
        return redirect('/lab8/articles')

    if request.method == 'GET':
        return render_template('lab8/edit.html', article=article)

    article.title = request.form.get('title')
    article.article_text = request.form.get('article_text')
    article.is_public = request.form.get('is_public') == 'on'
    article.is_favorite = request.form.get('is_favorite') == 'on'
    db.session.commit()

    return redirect('/lab8/articles')


@lab8.route('/lab8/delete/<int:article_id>')
@login_required
def delete_article(article_id):
    article = articles.query.get_or_404(article_id)
    if article.login_id == current_user.id:
        db.session.delete(article)
        db.session.commit()
    return redirect('/lab8/articles')


@lab8.route('/lab8/search', methods=['GET', 'POST'])
def search_articles_view():
    if request.method == 'GET':
        return render_template('lab8/search.html', username=get_username())

    search_query = request.form.get('search_query', '').strip()
    if not search_query:
        return redirect('/lab8/search')

    search_pattern = f"%{search_query}%"

    if current_user.is_authenticated:
        my_results = search_articles_query(search_pattern, user_id=current_user.id)
        public_results = search_articles_query(search_pattern, only_public=True)
        results = my_results + [a for a in public_results if a.login_id != current_user.id]
    else:
        results = search_articles_query(search_pattern, only_public=True)

    return render_template('lab8/search_results.html',
                           results=results,
                           search_query=search_query,
                           username=get_username(),
                           count=len(results))
