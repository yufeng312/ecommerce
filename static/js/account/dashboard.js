document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('#orderStatusTabs .nav-link');
    const cards = document.querySelectorAll('.order-card');
    const tabEmptyState = document.getElementById('tabEmptyState');
    const globalEmptyState = document.getElementById('globalEmptyState');

    if (globalEmptyState) return;

    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            const targetStatus = this.getAttribute('data-status');
            let visibleCount = 0;

            cards.forEach(card => {
                const cardStatus = card.getAttribute('data-status');
                if (targetStatus === 'all' || cardStatus === targetStatus) {
                    card.classList.remove('d-none');
                    visibleCount++;
                } else {
                    card.classList.add('d-none');
                }
            });

            if (visibleCount === 0) {
                tabEmptyState.classList.remove('d-none');
            } else {
                tabEmptyState.classList.add('d-none');
            }
        });
    });

    const unpaidCount = document.querySelectorAll('.order-card[data-status="unpaid"]').length;
    if (unpaidCount > 0) {
        const badge = document.getElementById('count-unpaid');
        badge.textContent = unpaidCount;
        badge.classList.remove('d-none');
    }
});