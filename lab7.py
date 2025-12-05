from flask import Blueprint, url_for, request, redirect, render_template, jsonify

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def main():
    return render_template('lab7/index.html')

films = [
     {
        "title": "The Matrix",
        "title_ru": "Матрица",
        "year": 1999,
        "description": "Хакер по кличке Нео узнаёт, что мир, в котором он живёт, всего лишь иллюзия,\
            созданная машинами для порабощения человечества. Он присоединяется к группе повстанцев,\
            чтобы сразиться с системой."
    },
     {
        "title": "Forrest Gump",
        "title_ru": "Форрест Гамп",
        "year": 1994,
        "description": "История простого парня с низким IQ, который неожиданно становится участником ключевых событий\
            американской истории второй половины XX века. Его жизнь полна невероятных приключений и встреч с известными личностями."
    },
    {
        "title": "Fight Club",
        "title_ru": "Бойцовский клуб",
        "year": 1999,
        "description": "Страдающий бессонницей офисный работник встречает загадочного продавца мыла Тайлера Дёрдена,\
            и вместе они создают подпольный бойцовский клуб, который превращается в нечто большее."
    },
     {
        "title": "The Holiday",
        "title_ru": "Отпуск по обмену",
        "year": 2006,
        "description": "Айрис, британская журналистка, и Аманда, успешный голливудский продюсер, переживают неудачи в личной жизни.\
            Через сайт по обмену домами они решают поменяться жильём на время рождественских праздников.\
            В новых странах обе женщины находят не только приятные сюрпризы, но и новую любовь, которая меняет их жизни."
    },
    {
        "title": "Harry Potter and the Prisoner of Azkaban",
        "title_ru": "Гарри Поттер и узник Азкабана",
        "year": 2004,
        "description": "На третьем курсе в Хогвартсе Гарри узнаёт, что из тюрьмы для волшебников Азкабан сбежал опасный преступник\
            Сириус Блэк, который, по слухам, предал его родителей и теперь охотится на самого Гарри.\
            В этом году Гарри также встречает нового учителя защиты от тёмных искусств и узнаёт правду о прошлом своих родителей."
    },
]


@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    return films


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    if id < 0 or id >= len(films):
        return {"error": "Film not found"}, 404
    return films[id]


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    if id < 0 or id >= len(films):
        return {"error": "Film not found"}, 404
    del films[id]
    return '', 204


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    if id < 0 or id >= len(films):
        return {"error": "Film not found"}, 404
    
    film = request.get_json()
    
    # ОСНОВНАЯ ЛОГИКА ПО ЗАДАНИЮ: 
    # если русское название есть, а оригинальное пустое - копируем русское
    if 'title_ru' in film and film['title_ru'].strip() and ('title' not in film or not film['title'].strip()):
        film['title'] = film['title_ru']
    
    errors = {}
    
    if 'title_ru' not in film or not film['title_ru'].strip():
        errors['title_ru'] = 'Заполните русское название'
    
    if 'description' not in film or not film['description'].strip():
        errors['description'] = 'Заполните описание'
    
    if errors:
        return errors, 400
    
    films[id] = film
    return films[id]


@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()
    
    # ОСНОВНАЯ ЛОГИКА ПО ЗАДАНИЮ:
    # если русское название есть, а оригинальное пустое - копируем русское
    if 'title_ru' in film and film['title_ru'].strip() and ('title' not in film or not film['title'].strip()):
        film['title'] = film['title_ru']
    
    errors = {}

    if 'title_ru' not in film or not film['title_ru'].strip():
        errors['title_ru'] = 'Заполните русское название'
    
    if 'description' not in film or not film['description'].strip():
        errors['description'] = 'Заполните описание'
    
    if errors:
        return errors, 400
    
    films.append(film)
    return {"id": len(films) - 1}