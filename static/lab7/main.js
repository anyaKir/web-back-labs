function fillFilmList() {
    fetch('/lab7/rest-api/films/')
        .then(function(data) {
            return data.json();
        })
        .then(function(films) {
            let tbody = document.getElementById('film-list');
            tbody.innerHTML = '';

            for(let i = 0; i < films.length; i++) {
                let tr = document.createElement('tr');

                let tdTitle = document.createElement('td');
                let tdTitleRus = document.createElement('td');
                let tdYear = document.createElement('td');
                let tdActions = document.createElement('td');

                // Оригинальное название выводим, только если оно отличается от русского
                tdTitle.innerText = films[i].title === films[i].title_ru ? '' : films[i].title;
                tdTitleRus.innerText = films[i].title_ru;
                tdYear.innerText = films[i].year;

                // Кнопки действий
                let editButton = document.createElement('button');
                editButton.innerText = 'редактировать';

                let delButton = document.createElement('button');
                delButton.innerText = 'удалить';
                
                delButton.onclick = function() {
                    deleteFilm(i, films[i].title_ru);
                };

                tdActions.append(editButton);
                tdActions.append(document.createTextNode(' ')); // пробел между кнопками
                tdActions.append(delButton);

                // Собираем строку
                tr.append(tdTitle);
                tr.append(tdTitleRus);
                tr.append(tdYear);
                tr.append(tdActions);

                // Добавляем строку в таблицу
                tbody.append(tr);
            }
        });
}

function deleteFilm(id, title) {
    // Добавляем подтверждение удаления с названием фильма
    if(!confirm(`Вы точно хотите удалить фильм "${title}"?`)) {
        return;
    }
    
    fetch(`/lab7/rest-api/films/${id}`, {
        method: 'DELETE'
    })
    .then(function() {
        // После успешного удаления обновляем таблицу
        fillFilmList();
    })
    .catch(function(error) {
        console.error('Ошибка при удалении фильма:', error);
        alert('Не удалось удалить фильм');
    });
}

function showModal() {
    document.getElementById('film-modal').style.display = 'block';
}

function hideModal() {
    document.getElementById('film-modal').style.display = 'none';
    // Очищаем сообщения об ошибках
    document.getElementById('description-error').innerText = '';
}

function cancel() {
    hideModal();
}

// ✅ ДОБАВЛЕНО: функция добавления фильма (открытие формы)
function addFilm() {
    // Очищаем все поля
    document.getElementById('film-id').value = '';
    document.getElementById('title').value = '';
    document.getElementById('title-ru').value = '';
    document.getElementById('year').value = '';
    document.getElementById('description').value = '';
    document.getElementById('description-error').innerText = '';
    
    showModal();
}

// ✅ ДОБАВЛЕНО: функция отправки фильма на сервер
function sendFilm() {
    const id = document.getElementById('film-id').value;
    const film = {
        title: document.getElementById('title').value,
        title_ru: document.getElementById('title-ru').value,
        year: parseInt(document.getElementById('year').value) || 0,
        description: document.getElementById('description').value
    };
    
    // Если оригинальное название пустое, копируем русское
    if (!film.title && film.title_ru) {
        film.title = film.title_ru;
    }
    
    // Определяем URL и метод
    let url, method;
    if (id === '') {
        // Добавление нового фильма
        url = '/lab7/rest-api/films/';
        method = 'POST';
    } else {
        // Редактирование существующего фильма
        url = `/lab7/rest-api/films/${id}`;
        method = 'PUT';
    }
    
    // Отправляем запрос
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(film)
    })
    .then(function(response) {
        if (response.ok) {
            // Успешно - обновляем таблицу и закрываем модальное окно
            fillFilmList();
            hideModal();
            return {};
        } else {
            // Ошибка - пытаемся получить JSON с ошибками
            return response.json();
        }
    })
    .then(function(data) {
        // Обработка ошибок валидации
        if (data && data.error) {
            alert('Ошибка: ' + data.error);
        } else if (data && data.description) {
            // Выводим ошибку для поля description
            document.getElementById('description-error').innerText = data.description;
        }
    })
    .catch(function(error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при сохранении фильма');
    });
}