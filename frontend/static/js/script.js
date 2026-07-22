function flipCard() {
    const card = document.getElementById('flipCard');
    if (card) {
        card.classList.toggle('flipped');
    }
}

function flipHero() {
    const hero = document.getElementById('heroCard');
    if (hero) {
        hero.classList.toggle('flipped');
    }
}

// Auto-hide toast notification after a few seconds
document.addEventListener('DOMContentLoaded', function () {
    const toast = document.getElementById('appToast');
    if (toast) {
        setTimeout(() => toast.classList.add('show'), 50);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 400);
        }, 3000);
    }

    // Confirm before deleting a card
    document.querySelectorAll('.delete-form').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!confirm('Delete this card? This cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
});
