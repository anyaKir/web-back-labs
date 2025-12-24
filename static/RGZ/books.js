let offset = 0;
let loading = false;
let isAdmin = false;

// Проверяем, является ли пользователь админом
function checkAdminStatus() {
    // Можно добавить проверку через API или использовать глобальную переменную
    // В этом примере предполагаем, что админ вошел в систему
    return document.body.classList.contains('admin-mode');
}

function loadBooks(reset = false) {
    if (loading) return;
    loading = true;
    
    if (reset) {
        offset = 0;
        document.getElementById("books").innerHTML = "";
    }
    
    // Показываем индикатор загрузки
    if (reset && offset === 0) {
        document.getElementById("books").innerHTML = 
            '<div class="message">⌛ Загрузка книг...</div>';
    }

    const params = new URLSearchParams({
        title: document.getElementById("title").value || '',
        author: document.getElementById("author").value || '',
        publisher: document.getElementById("publisher").value || '',
        pages_from: document.getElementById("pages_from").value || '',
        pages_to: document.getElementById("pages_to").value || '',
        sort: document.getElementById("sort").value || 'title',
        offset: offset
    });

    fetch(`/rgz/api/books?${params}`)
        .then(r => {
            if (!r.ok) throw new Error('Ошибка сети');
            return r.json();
        })
        .then(data => {
            const booksContainer = document.getElementById("books");
            
            if (reset && offset === 0) {
                booksContainer.innerHTML = "";
            }
            
            if (data.length === 0 && offset === 0) {
                booksContainer.innerHTML = 
                    '<div class="message">📚 Книги не найдены. Попробуйте изменить параметры поиска.</div>';
            } else if (data.length > 0) {
                data.forEach(b => {
                    const adminActions = isAdmin ? `
                        <div class="admin-actions">
                            <button class="admin-btn edit-btn" onclick="editBook(${b.id})">✏️ Редактировать</button>
                            <button class="admin-btn delete-btn" onclick="deleteBook(${b.id})">🗑️ Удалить</button>
                        </div>
                    ` : '';
                    
                    booksContainer.innerHTML += `
                    <div class="book-card" id="book-${b.id}">
                        <img src="${b.cover || '/static/RGZ/default-book.png'}" 
                             alt="${b.title}" 
                             onerror="this.src='/static/RGZ/default-book.png'">
                        <h3>${b.title}</h3>
                        <p><strong>👤 Автор:</strong> ${b.author}</p>
                        <p><strong>🏢 Издательство:</strong> ${b.publisher || 'Не указано'}</p>
                        <p><strong>📄 Страниц:</strong> ${b.pages}</p>
                        ${adminActions}
                    </div>`;
                });
                offset += 20;
            }
            
            loading = false;
            
            // Обновляем видимость кнопки "Показать ещё"
            const loadMoreBtn = document.querySelector('.load-more-btn');
            if (loadMoreBtn) {
                if (data.length < 20) {
                    loadMoreBtn.style.display = 'none';
                    if (offset > 20 && data.length === 0) {
                        booksContainer.innerHTML += '<div class="message">🎉 Это все книги по вашему запросу!</div>';
                    }
                } else {
                    loadMoreBtn.style.display = 'block';
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById("books").innerHTML = 
                '<div class="message" style="color: #e74c3c;">❌ Ошибка загрузки данных. Пожалуйста, обновите страницу.</div>';
            loading = false;
        });
}

function resetFilters() {
    document.getElementById("title").value = "";
    document.getElementById("author").value = "";
    document.getElementById("publisher").value = "";
    document.getElementById("pages_from").value = "";
    document.getElementById("pages_to").value = "";
    document.getElementById("sort").value = "title";
    loadBooks(true);
}

// Функции для админа
function addBook() {
    if (!isAdmin) {
        alert('Только администратор может добавлять книги');
        return;
    }
    
    const title = prompt('Введите название книги:');
    if (!title) return;
    
    const author = prompt('Введите автора:');
    if (!author) return;
    
    const pages = parseInt(prompt('Введите количество страниц:'));
    if (isNaN(pages) || pages <= 0) {
        alert('Некорректное количество страниц');
        return;
    }
    
    const publisher = prompt('Введите издательство (необязательно):') || '';
    const cover = prompt('Введите URL обложки (необязательно):') || '/static/RGZ/default-book.png';
    
    fetch('/rgz/api/admin/books', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({title, author, pages, publisher, cover})
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert('Книга успешно добавлена!');
            loadBooks(true);
        } else {
            alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    });
}

function editBook(bookId) {
    if (!isAdmin) {
        alert('Только администратор может редактировать книги');
        return;
    }
    
    const bookElement = document.getElementById(`book-${bookId}`);
    const title = prompt('Новое название:', bookElement.querySelector('h3').textContent);
    if (title === null) return;
    
    const author = prompt('Новый автор:', bookElement.querySelector('p:nth-child(3)').textContent.replace('👤 Автор: ', ''));
    if (author === null) return;
    
    const pages = parseInt(prompt('Новое количество страниц:', bookElement.querySelector('p:nth-child(5)').textContent.replace('📄 Страниц: ', '')));
    if (isNaN(pages) || pages <= 0) {
        alert('Некорректное количество страниц');
        return;
    }
    
    const publisher = prompt('Новое издательство:', bookElement.querySelector('p:nth-child(4)').textContent.replace('🏢 Издательство: ', '')) || '';
    const cover = prompt('Новый URL обложки:', bookElement.querySelector('img').src) || '/static/RGZ/default-book.png';
    
    fetch(`/rgz/api/admin/books/${bookId}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({title, author, pages, publisher, cover})
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert('Книга успешно обновлена!');
            loadBooks(true);
        } else {
            alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    });
}

function deleteBook(bookId) {
    if (!isAdmin) {
        alert('Только администратор может удалять книги');
        return;
    }
    
    if (!confirm('Вы уверены, что хотите удалить эту книгу?')) return;
    
    fetch(`/rgz/api/admin/books/${bookId}`, {
        method: 'DELETE'
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert('Книга успешно удалена!');
            loadBooks(true);
        } else {
            alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    });
}

// Загружаем книги при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем статус админа
    isAdmin = document.body.classList.contains('admin-mode');
    
    // Добавляем кнопку добавления книги для админа
    if (isAdmin) {
        const filters = document.querySelector('.filters');
        const addButton = document.createElement('button');
        addButton.innerHTML = '➕ Добавить книгу';
        addButton.onclick = addBook;
        addButton.style.background = 'linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%)';
        addButton.style.boxShadow = '0 4px 6px rgba(155, 89, 182, 0.3)';
        filters.appendChild(addButton);
    }
    
    loadBooks(true);
    
    // Добавляем обработчики Enter для фильтров
    ['title', 'author', 'publisher', 'pages_from', 'pages_to'].forEach(id => {
        document.getElementById(id).addEventListener('keypress', function(e) {
            if (e.key === 'Enter') loadBooks(true);
        });
    });
});