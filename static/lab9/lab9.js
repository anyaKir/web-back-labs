function openGift(giftId) {
    const giftBox = document.querySelector(`.gift-box[data-id="${giftId}"]`);

    if (giftBox.classList.contains('opened')) {
        showMessage('Этот подарок уже открыт', 'warning');
        return;
    }

    if (giftBox.classList.contains('locked')) {
        showMessage('🔒 Доступно только авторизованным', 'warning');
        return;
    }

    fetch('/lab9/open_gift', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ gift_id: giftId })
    })
    .then(r => r.json())
    .then(data => {
        if (!data.success) {
            showMessage(data.message, 'error');
            return;
        }

        document.getElementById('opened-count').textContent = data.opened_count;
        document.getElementById('remaining-count').textContent = data.remaining;

        giftBox.innerHTML = `
            <div class="opened-gift">
                <p>${data.message}</p>
                <img src="/static/lab9/${data.image}">
            </div>
        `;
        giftBox.classList.add('opened');

        showMessage('🎉 Подарок открыт!', 'success');
    });
}

function resetGifts() {
    if (!confirm('Сбросить подарки?')) return;

    fetch('/lab9/santa', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            alert(data.message);
            location.reload();
        });
}

function showMessage(text, type) {
    const area = document.getElementById('message-area');
    area.textContent = text;
    area.style.display = 'block';
    setTimeout(() => area.style.display = 'none', 4000);
}
