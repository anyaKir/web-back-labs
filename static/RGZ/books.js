let offset = 0;

function loadBooks(reset=false) {
    if (reset) {
        offset = 0;
        document.getElementById("books").innerHTML = "";
    }

    const params = new URLSearchParams({
        title: document.getElementById("title").value,
        author: document.getElementById("author").value,
        publisher: document.getElementById("publisher").value,
        pages_from: document.getElementById("pages_from").value,
        pages_to: document.getElementById("pages_to").value,
        sort: document.getElementById("sort").value,
        offset: offset
    });

    fetch(`/rgz/api/books?${params}`)
        .then(r => r.json())
        .then(data => {
            data.forEach(b => {
                document.getElementById("books").innerHTML += `
                <div class="book">
                    <img src="${b.cover}">
                    <div>
                        <b>${b.title}</b><br>
                        ${b.author}<br>
                        ${b.publisher}<br>
                        ${b.pages} стр.
                    </div>
                </div>`;
            });
            offset += 20;
        });
}

loadBooks(true);
