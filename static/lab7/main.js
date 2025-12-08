function fillFilmList() {
    fetch('/lab7/rest-api/films/', {
        headers: {
            'Accept': 'application/json; charset=utf-8'
        }
    })
        .then(function(response) {
            // Проверяем кодировку ответа
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('charset=utf-8')) {
                // Если сервер явно указал UTF-8
                return response.json();
            } else {
                // Иначе получаем как текст и парсим
                return response.text().then(function(text) {
                    try {
                        return JSON.parse(text);
                    } catch(e) {
                        console.error('Ошибка парсинга JSON:', e);
                        return [];
                    }
                });
            }
        })
        .then(function(films) {
            let tbody = document.getElementById('film-list');
            tbody.innerHTML = '';

            for(let i = 0; i < films.length; i++) {
                let tr = document.createElement('tr');

                let tdTitleRus = document.createElement('td');
                let tdTitle = document.createElement('td');
                let tdYear = document.createElement('td');
                let tdActions = document.createElement('td');

                // Безопасное отображение русского текста
                tdTitleRus.textContent = films[i].title_ru;
                tdTitleRus.style.fontWeight = 'bold';
                tdTitleRus.style.color = '#2c3e50';
               
                if (films[i].title && films[i].title.trim() !== '') {
                  if (films[i].title !== films[i].title_ru) {
                    tdTitle.innerHTML = `<span class="original-title"><i>${films[i].title}</i></span>`;
                } else {
                    tdTitle.innerHTML = `<span class="original-title" style="opacity: 0.6;"><i>${films[i].title_ru}</i></span>`;
                }

                } else {
                    tdTitle.innerHTML = '<span class="original-title" style="opacity: 0.6;"><i>— то же —</i></span>';
                }
                
                tdYear.innerHTML = `<span class="film-year">${films[i].year}</span>`;
                
                let editButton = document.createElement('button');
                editButton.innerText = 'редактировать';
                editButton.className = 'edit-btn';
                editButton.onclick = (function(id) {
                    return function() {
                        editFilm(id);
                    };
                })(films[i].id); // Замыкание для сохранения правильного id

                let delButton = document.createElement('button');
                delButton.innerText = 'удалить';
                delButton.className = 'delete-btn';
                delButton.onclick = (function(id, title) {
                    return function() {
                        deleteFilm(id, title);
                    };
                })(films[i].id, films[i].title_ru); // Замыкание для сохранения id и названия

                tdActions.append(editButton);
                tdActions.append(delButton);

                tr.append(tdTitleRus);  
                tr.append(tdTitle);     
                tr.append(tdYear);
                tr.append(tdActions);

                tbody.append(tr);
            }
        })
        .catch(function(error) {
            console.error('Ошибка при загрузке фильмов:', error);
            alert('Не удалось загрузить список фильмов. Пожалуйста, обновите страницу.');
        });
}

function deleteFilm(id, title) {
    if(!confirm(`Вы точно хотите удалить фильм "${title}"?`)) {
        return;
    }
    
    fetch(`/lab7/rest-api/films/${id}`, {
        method: 'DELETE'
    })
    .then(function(response) {
        if (response.ok) {
            fillFilmList();
        } else {
            alert('Ошибка при удалении фильма');
        }
    })
    .catch(function(error) {
        console.error('Ошибка при удалении фильма:', error);
        alert('Не удалось удалить фильм');
    });
}

function showModal() {
    document.getElementById('film-modal').style.display = 'block';
    document.getElementById('modal-overlay').style.display = 'block';
}

function hideModal() {
    document.getElementById('film-modal').style.display = 'none';
    document.getElementById('modal-overlay').style.display = 'none';
    clearErrors();
}

function cancel() {
    hideModal();
}

function clearErrors() {
    const errorFields = ['description', 'title-ru', 'title', 'year'];
    errorFields.forEach(fieldId => {
        const errorElement = document.getElementById(fieldId + '-error');
        if (errorElement) {
            errorElement.innerText = '';
        }
        const inputElement = document.getElementById(fieldId);
        if (inputElement) {
            inputElement.classList.remove('error-field');
        }
    });
}

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
    document.getElementById('modal-title').textContent = 'Добавить фильм';
    document.getElementById('send-button').textContent = 'OK';
    
    clearErrors();
    showModal();
}

function sendFilm() {
    clearErrors();
    
    const id = document.getElementById('film-id').value;
    const titleInput = document.getElementById('title');
    const titleRuInput = document.getElementById('title-ru');
    const titleRu = titleRuInput.value.trim();
    const title = titleInput.value.trim();
    const year = parseInt(document.getElementById('year').value) || 0;
    const description = document.getElementById('description').value.trim();
    
    const film = {
        title: title,
        title_ru: titleRu,
        year: year,
        description: description
    };
    
    if (!film.title && film.title_ru) {
        film.title = film.title_ru;
        titleInput.value = film.title_ru;
    }
    
    let url, method;
    if (id === '') {
        url = '/lab7/rest-api/films/';
        method = 'POST';
    } else {
        url = `/lab7/rest-api/films/${id}`;
        method = 'PUT';
    }
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json; charset=utf-8'  // Добавлено charset
        },
        body: JSON.stringify(film)
    })
    .then(function(response) {
        if (response.ok) {
            fillFilmList();
            hideModal();
            return {};
        } else {
            return response.json().then(function(data) {
                throw data; // Перебрасываем данные об ошибке
            });
        }
    })
    .then(function() {
        // Успешный случай уже обработан выше
    })
    .catch(function(errorData) {
        if (errorData && typeof errorData === 'object') {
            // Отображаем ошибки валидации
            if (errorData.description) {
                showError('description', errorData.description);
            }
            if (errorData.title_ru) {
                showError('title-ru', errorData.title_ru);
            }
            if (errorData.title) {
                showError('title', errorData.title);
            }
            if (errorData.year) {
                showError('year', errorData.year);
            }
            if (errorData.error && !errorData.description && !errorData.title_ru && !errorData.title && !errorData.year) {
                alert('Ошибка: ' + errorData.error);
            }
        } else {
            console.error('Ошибка:', errorData);
            alert('Произошла ошибка при сохранении фильма');
        }
    });
}

function editFilm(id) {
    fetch(`/lab7/rest-api/films/${id}`, {
        headers: {
            'Accept': 'application/json; charset=utf-8'
        }
    })
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
            
            document.getElementById('modal-title').textContent = 'Редактировать фильм';
            document.getElementById('send-button').textContent = 'Сохранить';
            
            clearErrors();
            showModal();
        })
        .catch(function(error) {
            console.error('Ошибка:', error);
            alert('Не удалось загрузить данные фильма для редактирования');
        });
}