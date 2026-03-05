// Кнопки "Написать отзыв"
    document.querySelectorAll('.btn-write-review').forEach(btn => {
        btn.addEventListener('click', () => {
            const courseId = btn.dataset.courseId;
            const form = document.querySelector(`.review-form[data-course-id="${courseId}"]`);
            form.classList.toggle('active');
            btn.textContent = form.classList.contains('active') ? 'Скрыть форму' : 'Написать отзыв';
        });
    });
    
    // Звёзды
    document.querySelectorAll('.stars').forEach(starsContainer => {
        const stars = starsContainer.querySelectorAll('.star');
        const ratingInput = starsContainer.parentElement.querySelector('#rating');
        
        stars.forEach(star => {
            star.addEventListener('click', () => {
                const value = parseInt(star.dataset.value);
                ratingInput.value = value;
                
                stars.forEach((s, index) => {
                    if (index < value) {
                        s.classList.add('active');
                    } else {
                        s.classList.remove('active');
                    }
                });
            });
        });
    });