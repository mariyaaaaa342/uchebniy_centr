// Слайдер сертификатов 
    const slider = document.querySelector('.certificates-slider');
    if (slider) {
        const track = slider.querySelector('.certificates-track');
        const slides = slider.querySelectorAll('.certificates-slide');
        const prevBtn = slider.querySelector('.certificates-btn-prev');
        const nextBtn = slider.querySelector('.certificates-btn-next');
        const dotsContainer = slider.querySelector('.certificates-dots');
        
        let currentIndex = 0;
        const slideCount = slides.length;
        
        if (slideCount > 1) {
            // Создаём точки
            slides.forEach((_, index) => {
                const dot = document.createElement('span');
                dot.classList.add('certificates-dot');
                if (index === 0) dot.classList.add('active');
                dot.addEventListener('click', () => goToSlide(index));
                dotsContainer.appendChild(dot);
            });
            
            const dots = document.querySelectorAll('.certificates-dot');
            
            function goToSlide(index) {
                if (index < 0) index = slideCount - 1;
                if (index >= slideCount) index = 0;
                currentIndex = index;
                track.style.transform = `translateX(-${currentIndex * 100}%)`;
                dots.forEach((dot, i) => dot.classList.toggle('active', i === currentIndex));
            }
            
            prevBtn.addEventListener('click', () => goToSlide(currentIndex - 1));
            nextBtn.addEventListener('click', () => goToSlide(currentIndex + 1));
        }
    }