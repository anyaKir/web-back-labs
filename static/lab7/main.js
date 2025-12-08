async function fillFilmList() {
    try {
        const response = await fetch('/lab7/rest-api/films/', {
            headers: { 'Accept': 'application/json; charset=utf-8' }
        });

        let films = [];
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('charset=utf-8')) {
            films = await response.json();
        } else {
            const text = await response.text();
            try {
                films = JSON.parse(text);
            } catch(e) {
                console.error('Ошибка парсинга JSON:', e);
            }
        }

        const tbody = document.getElementById('film-list');
        tbody.innerHTML = '';

        films.forEach(film => {
            const tr = document.createElement('tr');

            const tdTitleRus = document.createElement('td');
            tdTitleRus.textContent = film.title_ru;
            tdTitleRus.style.fontWeight = 'bold';
            tdTitleRus.style.color = '#2c3e50';

            const tdTitle = document.createElement('td');
            if (film.title && film.title.trim()) {
                tdTitle.innerHTML = (film.title !== film.title_ru) 
                    ? `<span class="original-title"><i>${film.title}</i></span>` 
                    : `<span class="original-title" style="opacity:0.6;"><i>${film.title_ru}</i></span>`;
            } else {
                tdTitle.innerHTML = `<span class="original-title" style="opacity:0.6;"><i>— то же —</i></span>`;
            }

            const tdYear = document.createElement('td');
            tdYear.innerHTML = `<span class="film-year">${film.year}</span>`;

            const tdActions = document.createElement('td');
            tdActions.append(createButton('редактировать', 'edit-btn', () => editFilm(film.id)));
            tdActions.append(createButton('удалить', 'delete-btn', () => deleteFilm(film.id, film.title_ru)));

            tr.append(tdTitleRus, tdTitle, tdYear, tdActions);
            tbody.append(tr);
        });

    } catch (error) {
        console.error('Ошибка при загрузке фильмов:', error);
        alert('Не удалось загрузить список фильмов. Пожалуйста, обновите страницу.');
    }
}

function createButton(text, className, onClick) {
    const btn = document.createElement('button');
    btn.innerText = text;
    btn.className = className;
    btn.onclick = onClick;
    return btn;
}

async function deleteFilm(id, title) {
    if (!confirm(`Вы точно хотите удалить фильм "${title}"?`)) return;

    try {
        const response = await fetch(`/lab7/rest-api/films/${id}`, { method: 'DELETE' });
        if (response.ok) fillFilmList();
        else alert('Ошибка при удалении фильма');
    } catch (error) {
        console.error('Ошибка при удалении фильма:', error);
        alert('Не удалось удалить фильм');
    }
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

function cancel() { hideModal(); }

function clearErrors() {
    ['description', 'title-ru', 'title', 'year'].forEach(fieldId => {
        const elError = document.getElementById(fieldId + '-error');
        if (elError) elError.innerText = '';
        const elInput = document.getElementById(fieldId);
        if (elInput) elInput.classList.remove('error-field');
    });
}

function showError(fieldId, message) {
    const elError = document.getElementById(fieldId + '-error');
    const elInput = document.getElementById(fieldId);
    if (elError) elError.innerText = message;
    if (elInput) elInput.classList.add('error-field');
}

function addFilm() {
    ['film-id', 'title', 'title-ru', 'year', 'description'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('modal-title').textContent = 'Добавить фильм';
    document.getElementById('send-button').textContent = 'OK';
    clearErrors();
    showModal();
}

async function sendFilm() {
    clearErrors();
    const id = document.getElementById('film-id').value;
    const titleInput = document.getElementById('title');
    const titleRuInput = document.getElementById('title-ru');

    const film = {
        title: titleInput.value.trim() || titleRuInput.value.trim(),
        title_ru: titleRuInput.value.trim(),
        year: parseInt(document.getElementById('year').value) || 0,
        description: document.getElementById('description').value.trim()
    };
    titleInput.value = film.title;

    const url = id ? `/lab7/rest-api/films/${id}` : '/lab7/rest-api/films/';
    const method = id ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json; charset=utf-8' },
            body: JSON.stringify(film)
        });

        if (response.ok) {
            fillFilmList();
            hideModal();
        } else {
            const errorData = await response.json();
            Object.entries(errorData).forEach(([field, msg]) => showError(field.replace('_', '-'), msg));
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при сохранении фильма');
    }
}

async function editFilm(id) {
    try {
        const response = await fetch(`/lab7/rest-api/films/${id}`, {
            headers: { 'Accept': 'application/json; charset=utf-8' }
        });
        if (!response.ok) throw new Error('Фильм не найден');
        const film = await response.json();

        document.getElementById('film-id').value = id;
        document.getElementById('title').value = film.title;
        document.getElementById('title-ru').value = film.title_ru;
        document.getElementById('year').value = film.year;
        document.getElementById('description').value = film.description;

        document.getElementById('modal-title').textContent = 'Редактировать фильм';
        document.getElementById('send-button').textContent = 'Сохранить';

        clearErrors();
        showModal();
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Не удалось загрузить данные фильма для редактирования');
    }
}
