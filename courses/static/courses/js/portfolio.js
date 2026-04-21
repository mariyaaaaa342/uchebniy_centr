document.addEventListener('DOMContentLoaded', function() {
    const filterToggleBtn = document.getElementById('filterToggleBtn');
    const filterPanel = document.getElementById('filterPanel');
    
    if (filterToggleBtn && filterPanel) {
        filterToggleBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            filterPanel.classList.toggle('active');
            
            // Для мобильных: добавляем затемнение
            if (window.innerWidth <= 768) {
                if (filterPanel.classList.contains('active')) {
                    document.body.classList.add('filter-open');
                } else {
                    document.body.classList.remove('filter-open');
                }
            }
        });
    }
    
    // Закрытие при клике вне панели
    document.addEventListener('click', function(event) {
        if (filterPanel && filterPanel.classList.contains('active')) {
            if (!filterPanel.contains(event.target) && !filterToggleBtn.contains(event.target)) {
                filterPanel.classList.remove('active');
                document.body.classList.remove('filter-open');
            }
        }
    });
    
    // Фильтрация
    const cards = document.querySelectorAll('.portfolio-card');
    const workTypeBtns = document.querySelectorAll('#workTypeFilters .filter-btn');
    const authorTypeBtns = document.querySelectorAll('#authorTypeFilters .filter-btn');
    
    let currentWorkType = 'all';
    let currentAuthorType = 'all';
    
    function filterCards() {
        cards.forEach(card => {
            // Получаем все типы работ из data-атрибута (сохраните их при рендере)
            const workTypes = card.dataset.workTypes ? card.dataset.workTypes.split(',') : [];
            const authorType = card.dataset.authorType;
            
            const workTypeMatch = currentWorkType === 'all' || workTypes.includes(currentWorkType);
            const authorTypeMatch = currentAuthorType === 'all' || authorType === currentAuthorType;
            
            if (workTypeMatch && authorTypeMatch) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    // Обработчики для фильтра по типу работ
    workTypeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            workTypeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentWorkType = btn.dataset.workType;
            filterCards();
        });
    });
    
    // Обработчики для фильтра по автору
    authorTypeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            authorTypeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentAuthorType = btn.dataset.authorType;
            filterCards();
        });
    });
    
    // Модальное окно
    const modal = document.getElementById('portfolioModal');
    const modalImage = document.getElementById('modalImage');
    const modalClose = document.querySelector('.modal-close');
    
    cards.forEach(card => {
        card.addEventListener('click', () => {
            const imageUrl = card.dataset.imageUrl;
            modalImage.src = imageUrl;
            modal.classList.add('active');
        });
    });
    
    function closeModal() {
        modal.classList.remove('active');
        modalImage.src = '';
    }
    
    if (modalClose) {
        modalClose.addEventListener('click', closeModal);
    }
    
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
            closeModal();
        }
    });
});