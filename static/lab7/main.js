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
                
                editButton.onclick = function() {
                    editFilm(i);
                };

                let delButton = document.createElement('button');
                delButton.innerText = 'удалить';
                
                delButton.onclick = function() {
                    deleteFilm(i, films[i].title_ru);
                };

                tdActions.append(editButton);
                tdActions.append(document.createTextNode(' '));
                tdActions.append(delButton);

                tr.append(tdTitle);
                tr.append(tdTitleRus);
                tr.append(tdYear);
                tr.append(tdActions);

                tbody.append(tr);
            }
        });
}

function deleteFilm(id, title) {
    if(!confirm(`Вы точно хотите удалить фильм "${title}"?`)) {
        return;
    }
    
    fetch(`/lab7/rest-api/films/${id}`, {
        method: 'DELETE'
    })
    .then(function() {
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
    // Очищаем ошибки при закрытии окна
    clearErrors();
}

function cancel() {
    hideModal();
}

// Функция очистки ошибок
function clearErrors() {
    document.getElementById('description-error').innerText = '';
    document.getElementById('description').classList.remove('error-field');
}

// Функция показа ошибки
function showError(fieldId, message) {
    const errorElement = document.getElementById(fieldId + '-error');
    const inputElement = document.getElementById(fieldId);
    
    if (errorElement) {
        errorElement.innerText = message;
    }
    if (inputElement) {
        inputElement.classList.add('error-field');
    }
}

function addFilm() {
    document.getElementById('film-id').value = '';
    document.getElementById('title').value = '';
    document.getElementById('title-ru').value = '';
    document.getElementById('year').value = '';
    document.getElementById('description').value = '';
    
    clearErrors(); // Очищаем ошибки
    
    const okButton = document.querySelector('#film-modal button[onclick="sendFilm()"]');
    okButton.innerText = 'OK';
    
    showModal();
}

function sendFilm() {
    // Очищаем предыдущие ошибки
    clearErrors();
    
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
        url = '/lab7/rest-api/films/';
        method = 'POST';
    } else {
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
        // Обработка ошибок валидации (как в методичке)
        if (data && data.error) {
            alert('Ошибка: ' + data.error);
        } else if (data && data.description) {
            // Выводим ошибку для поля description
            showError('description', data.description);
        }
    })
    .catch(function(error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при сохранении фильма');
    });
}

function editFilm(id) {
    fetch(`/lab7/rest-api/films/${id}`)
        .then(function(response) {
            if (!response.ok) {
                throw new Error('Фильм не найден');
            }
            return response.json();
        })
        .then(function(film) {
            document.getElementById('film-id').value = id;
            document.getElementById('title').value = film.title;
            document.getElementById('title-ru').value = film.title_ru;
            document.getElementById('year').value = film.year;
            document.getElementById('description').value = film.description;
            
            // Очищаем ошибки при открытии формы редактирования
            clearErrors();
            
            const okButton = document.querySelector('#film-modal button[onclick="sendFilm()"]');
            okButton.innerText = 'Сохранить изменения';
            
            showModal();
        })
        .catch(function(error) {
            console.error('Ошибка:', error);
            alert('Не удалось загрузить данные фильма для редактирования');
        });
}