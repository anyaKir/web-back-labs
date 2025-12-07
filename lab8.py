from flask import Blueprint, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from db import db  
from db.models import users, articles
from sqlalchemy import or_, func

lab8 = Blueprint('lab8', __name__, template_folder='templates')

def get_db():
    from app import db
    return db

def get_models():
    from db.models import users, articles
    return users, articles


@lab8.route('/lab8/')
def main():
    username = current_user.login if current_user.is_authenticated else 'anonymous'
    return render_template('lab8/lab8.html', username=username)


@lab8.route('/lab8/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')
    
    users, articles = get_models()
    db = get_db()
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    
    if not login_form or not password_form:
        return render_template('lab8/register.html', 
                             error='Логин и пароль не могут быть пустыми')
    
    user_exists = users.query.filter_by(login=login_form).first()
    if user_exists:
        return render_template('lab8/register.html',
                             error='Такой пользователь уже существует')
    
    password_hash = generate_password_hash(password_form)
    new_user = users(login=login_form, password=password_hash)
    
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user)
    return redirect('/lab8/')


@lab8.route('/lab8/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')
    
    users, articles = get_models()
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember = request.form.get('remember') == 'on'
    
    if not login_form or not password_form:
        return render_template('lab8/login.html',
                             error='Логин и пароль не могут быть пустыми')
    
    user = users.query.filter_by(login=login_form).first()
    
    if user and check_password_hash(user.password, password_form):
        login_user(user, remember=remember)
        return redirect('/lab8/')
    else:
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
    users, articles = get_models()
    
    user_articles = articles.query.filter_by(login_id=current_user.id).all()
    
    public_articles = articles.query.filter(
        articles.is_public == True,
        articles.login_id != current_user.id
    ).all()
    
    return render_template('lab8/articles.html', 
                         articles=user_articles,
                         public_articles=public_articles)


@lab8.route('/lab8/public')
def public_articles():
    users, articles = get_models()
    
    all_public = articles.query.filter_by(is_public=True).all()
    
    username = current_user.login if current_user.is_authenticated else 'anonymous'
    
    return render_template('lab8/public.html',
                         articles=all_public,
                         username=username)


@lab8.route('/lab8/create', methods=['GET', 'POST'])
@login_required
def create_article():
    if request.method == 'GET':
        return render_template('lab8/create.html')
    
    users, articles = get_models()
    db = get_db()
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_public = request.form.get('is_public') == 'on'
    is_favorite = request.form.get('is_favorite') == 'on'
    
    if not title or not article_text:
        return render_template('lab8/create.html', 
                             error='Заголовок и текст статьи обязательны')
    
    new_article = articles(
        login_id=current_user.id,
        title=title,
        article_text=article_text,
        is_public=is_public,
        is_favorite=is_favorite,
        likes=0
    )
    
    db.session.add(new_article)
    db.session.commit()
    
    return redirect('/lab8/articles')


@lab8.route('/lab8/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    users, articles = get_models()
    db = get_db()
    
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
    users, articles = get_models()
    db = get_db()
    
    article = articles.query.get_or_404(article_id)
    
    if article.login_id != current_user.id:
        return redirect('/lab8/articles')
    
    db.session.delete(article)
    db.session.commit()
    
    return redirect('/lab8/articles')


@lab8.route('/lab8/search', methods=['GET', 'POST'])
def search_articles():
    if request.method == 'GET':
        username = current_user.login if current_user.is_authenticated else 'anonymous'
        return render_template('lab8/search.html', username=username)
    
    users, articles = get_models()
    search_query = request.form.get('search_query', '').strip()
    
    if not search_query:
        return redirect('/lab8/search')
    
    search_pattern = f"%{search_query}%"
  
    if current_user.is_authenticated:
        my_results = articles.query.filter(
            articles.login_id == current_user.id,
            or_(
                func.lower(articles.title).like(func.lower(search_pattern)),
                func.lower(articles.article_text).like(func.lower(search_pattern))
            )
        ).all()
        public_results = articles.query.filter(
            articles.login_id != current_user.id,
            articles.is_public == True,
            or_(
                func.lower(articles.title).like(func.lower(search_pattern)),
                func.lower(articles.article_text).like(func.lower(search_pattern))
            )
        ).all()
        
        results = my_results + public_results
        
    else:
        results = articles.query.filter(
            articles.is_public == True,
            or_(
                func.lower(articles.title).like(func.lower(search_pattern)),
                func.lower(articles.article_text).like(func.lower(search_pattern))
            )
        ).all()
    
    username = current_user.login if current_user.is_authenticated else 'anonymous'
    
    return render_template('lab8/search_results.html',
                         results=results,
                         search_query=search_query,
                         username=username,
                         count=len(results))