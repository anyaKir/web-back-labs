let offset = 0;
let loading = false;

function loadBooks(reset = false) {
    if (loading) return;
    loading = true;

    if (reset) {
        offset = 0;
        document.getElementById("books").innerHTML = "";
    }

    const params = new URLSearchParams({
        title: document.getElementById("title")?.value || "",
        author: document.getElementById("author")?.value || "",
        publisher: document.getElementById("publisher")?.value || "",
        pages_from: document.getElementById("pages_from")?.value || "",
        pages_to: document.getElementById("pages_to")?.value || "",
        sort: document.getElementById("sort")?.value || "title",
        offset: offset
    });

    fetch(`/rgz/api/books?${params}`)
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById("books");

            if (data.length === 0 && offset === 0) {
                container.innerHTML =
                    `<div class="message">📚 Книги не найдены</div>`;
                return;
            }

            data.forEach(b => {
                let cover = b.cover || "/static/RGZ/default-book.png";
                if (!cover.startsWith("/static/")) {
                    cover = "/static/RGZ/" + cover;
                }

                const card = document.createElement("div");
                card.className = "book-card";
                card.innerHTML = `
                    <img src="${cover}" onerror="this.src='/static/RGZ/default-book.png'">
                    <h3>${b.title}</h3>
                    <p><strong>Автор:</strong> ${b.author}</p>
                    <p><strong>Издательство:</strong> ${b.publisher || "—"}</p>
                    <p><strong>Страниц:</strong> ${b.pages}</p>
                `;
                container.appendChild(card);
            });

            offset += data.length;
            loading = false;
        })
        .catch(err => {
            document.getElementById("books").innerHTML =
                `<div class="message">❌ Ошибка загрузки</div>`;
            loading = false;
        });
}

function resetFilters() {
    ["title", "author", "publisher", "pages_from", "pages_to"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
    document.getElementById("sort").value = "title";
    loadBooks(true);
}

document.addEventListener("DOMContentLoaded", () => {
    loadBooks(true);
});

window.loadBooks = loadBooks;
window.resetFilters = resetFilters;
