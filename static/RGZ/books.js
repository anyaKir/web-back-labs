let offset = 0;
let loading = false;
let isAdmin = false;

// Проверяем, является ли пользователь админом
function checkAdminStatus() {
    // Проверяем наличие админ-класса или элемента с админ-информацией
    if (document.body.classList.contains('admin-mode')) {
        return true;
    }
    
    // Или проверяем текст в user-info
    const userInfo = document.querySelector('.user-info');
    if (userInfo && userInfo.textContent.includes('Администратор')) {
        return true;
    }
    
    return false;
}

function loadBooks(reset = false) {
    console.log('loadBooks вызван, reset:', reset);
    
    if (loading) {
        console.log('Уже загружается, пропускаем');
        return;
    }
    
    loading = true;
    
    if (reset) {
        offset = 0;
        document.getElementById("books").innerHTML = "";
        console.log('Сброс, offset установлен в 0');
    }
    
    // Показываем индикатор загрузки
    if (reset && offset === 0) {
        document.getElementById("books").innerHTML = 
            '<div class="message">⌛ Загрузка книг...</div>';
    }

    // Получаем элементы фильтров
    const title = document.getElementById("title") ? document.getElementById("title").value : '';
    const author = document.getElementById("author") ? document.getElementById("author").value : '';
    const publisher = document.getElementById("publisher") ? document.getElementById("publisher").value : '';
    const pages_from = document.getElementById("pages_from") ? document.getElementById("pages_from").value : '';
    const pages_to = document.getElementById("pages_to") ? document.getElementById("pages_to").value : '';
    const sort = document.getElementById("sort") ? document.getElementById("sort").value : 'title';

    // Создаем параметры запроса
    const params = new URLSearchParams();
    if (title) params.append('title', title);
    if (author) params.append('author', author);
    if (publisher) params.append('publisher', publisher);
    if (pages_from) params.append('pages_from', pages_from);
    if (pages_to) params.append('pages_to', pages_to);
    params.append('sort', sort);
    params.append('offset', offset);

    console.log('Запрос к API с параметрами:', params.toString());
    console.log('URL запроса:', `/rgz/api/books?${params}`);
    
    fetch(`/rgz/api/books?${params}`)
        .then(r => {
            console.log('Статус ответа:', r.status);
            if (!r.ok) {
                throw new Error(`Ошибка сети: ${r.status} ${r.statusText}`);
            }
            return r.json();
        })
        .then(data => {
            console.log('Получены данные:', data);
            console.log('Количество книг:', data.length);
            
            const booksContainer = document.getElementById("books");
            
            if (reset && offset === 0) {
                booksContainer.innerHTML = "";
            }
            
            if (data.length === 0 && offset === 0) {
                booksContainer.innerHTML = 
                    '<div class="message">📚 Книги не найдены. <br>' +
                    '<small>Попробуйте <a href="/rgz/load_books">загрузить книги</a> или изменить параметры поиска</small></div>';
            } else if (data.length > 0) {
                data.forEach(b => {
                    console.log('Обрабатываем книгу:', b.title, 'cover:', b.cover);
                    
                    // Исправляем путь к картинке
                    let coverPath = b.cover || '/static/RGZ/default-book.png';
                    
                    // Если путь относительный (без /static/)
                    if (coverPath && !coverPath.startsWith('/static/') && !coverPath.startsWith('http')) {
                        if (coverPath.startsWith('covers/')) {
                            coverPath = '/static/RGZ/' + coverPath;
                        } else if (!coverPath.includes('/')) {
                            coverPath = '/static/RGZ/covers/' + coverPath;
                        } else {
                            coverPath = '/static/RGZ/' + coverPath;
                        }
                    }
                    
                    console.log('Исправленный путь к картинке:', coverPath);
                    
                    // Получаем данные для админских кнопок
                    const titleText = b.title || 'Без названия';
                    const authorText = b.author || 'Неизвестен';
                    const publisherText = b.publisher || 'Не указано';
                    const pagesText = b.pages || '0';
                    
                    // Формируем карточку книги
                    const bookCard = document.createElement('div');
                    bookCard.className = 'book-card';
                    bookCard.id = `book-${b.id}`;
                    
                    bookCard.innerHTML = `
                        <img src="${coverPath}" 
                             alt="${titleText}" 
                             onerror="this.src='/static/RGZ/default-book.png'">
                        <h3>${titleText}</h3>
                        <p><strong>👤 Автор:</strong> ${authorText}</p>
                        <p><strong>🏢 Издательство:</strong> ${publisherText}</p>
                        <p><strong>📄 Страниц:</strong> ${pagesText}</p>
                    `;
                    
                    booksContainer.appendChild(bookCard);
                });
                
                offset += data.length;
                console.log('Новый offset:', offset);
            }
            
            loading = false;
            
            // Обновляем видимость кнопки "Показать ещё"
            const loadMoreBtn = document.querySelector('.load-more-btn');
            if (loadMoreBtn) {
                if (data.length < 20) {
                    loadMoreBtn.style.display = 'none';
                    if (offset > 20 && data.length === 0) {
                        const message = document.createElement('div');
                        message.className = 'message';
                        message.innerHTML = '🎉 Это все книги по вашему запросу!';
                        booksContainer.appendChild(message);
                    }
                } else {
                    loadMoreBtn.style.display = 'block';
                }
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки книг:', error);
            const booksContainer = document.getElementById("books");
            booksContainer.innerHTML = 
                '<div class="message" style="color: #e74c3c;">' +
                '❌ Ошибка загрузки данных<br>' +
                '<small>' + error.message + '</small><br>' +
                '<button onclick="loadBooks(true)" style="margin-top: 10px; padding: 8px 16px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer;">Повторить</button>' +
                '</div>';
            loading = false;
        });
}

function resetFilters() {
    if (document.getElementById("title")) document.getElementById("title").value = "";
    if (document.getElementById("author")) document.getElementById("author").value = "";
    if (document.getElementById("publisher")) document.getElementById("publisher").value = "";
    if (document.getElementById("pages_from")) document.getElementById("pages_from").value = "";
    if (document.getElementById("pages_to")) document.getElementById("pages_to").value = "";
    if (document.getElementById("sort")) document.getElementById("sort").value = "title";
    loadBooks(true);
}

// Загружаем книги при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, инициализация...');
    
    // Проверяем статус админа
    isAdmin = checkAdminStatus();
    console.log('Статус админа:', isAdmin);
    
    // Загружаем книги с задержкой, чтобы DOM точно был готов
    setTimeout(() => {
        loadBooks(true);
    }, 100);
    
    // Добавляем обработчики Enter для фильтров
    ['title', 'author', 'publisher', 'pages_from', 'pages_to'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    loadBooks(true);
                }
            });
        }
    });
});

// Делаем функции глобальными для вызова из HTML
window.loadBooks = loadBooks;
window.resetFilters = resetFilters;