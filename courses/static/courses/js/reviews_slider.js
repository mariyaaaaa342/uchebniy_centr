// Слайдер для третьей секции (отзывы)
function initThirdSlider() {
    const sliderContainer = document.querySelector('.third_slider');
    if (!sliderContainer) return;
    
    const track = sliderContainer.querySelector('.third_track');
    const slides = sliderContainer.querySelectorAll('.third_slide');
    const prevBtn = sliderContainer.querySelector('.third_btn-prev');
    const nextBtn = sliderContainer.querySelector('.third_btn-next');
    const dotsContainer = sliderContainer.querySelector('.third_dots');
    
    let currentIndex = 0;
    const slideCount = slides.length;
    
    slides.forEach((_, index) => {
        const dot = document.createElement('span');
        dot.classList.add('third_dot');
        if (index === 0) dot.classList.add('active');
        dot.addEventListener('click', () => goToSlide(index));
        dotsContainer.appendChild(dot);
    });
    
    const dots = dotsContainer.querySelectorAll('.third_dot');
    
    function goToSlide(index) {
        if (index < 0) index = slideCount - 1;
        if (index >= slideCount) index = 0;
        
        currentIndex = index;
        track.style.transform = `translateX(-${currentIndex * 100}%)`;
        
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === currentIndex);
        });
    }
    
    if (prevBtn) {
        prevBtn.addEventListener('click', () => goToSlide(currentIndex - 1));
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => goToSlide(currentIndex + 1));
    }
    
    let touchStartX = 0;
    let touchEndX = 0;
    
    sliderContainer.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    sliderContainer.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        const diff = touchEndX - touchStartX;
        
        if (Math.abs(diff) > 50) {
            if (diff > 0) {
                goToSlide(currentIndex - 1);
            } else {
                goToSlide(currentIndex + 1);
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initThirdSlider();
});