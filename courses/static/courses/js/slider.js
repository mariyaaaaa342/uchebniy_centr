// Слайдер для второго блока (автоматический)
document.addEventListener('DOMContentLoaded', function() {
    const sliderContainer = document.querySelector('.slider-container');
    if (!sliderContainer) return;
    
    const track = sliderContainer.querySelector('.slider-track');
    const slides = sliderContainer.querySelectorAll('.slider-slide');
    const dotsContainer = sliderContainer.querySelector('.slider-dots');
    
    let currentIndex = 0;
    const slideCount = slides.length;
    let autoSlideInterval;
    
    if (slideCount <= 1) return;
    
    if (dotsContainer) {
        dotsContainer.innerHTML = '';
        slides.forEach((_, index) => {
            const dot = document.createElement('span');
            dot.classList.add('slider-dot');
            if (index === 0) dot.classList.add('active');
            dot.addEventListener('click', () => goToSlide(index));
            dotsContainer.appendChild(dot);
        });
    }
    
    const dots = dotsContainer.querySelectorAll('.slider-dot');
    
    function goToSlide(index) {
        if (index < 0) index = slideCount - 1;
        if (index >= slideCount) index = 0;
        currentIndex = index;
        track.style.transform = 'translateX(-' + (currentIndex * 100) + '%)';
        for (let i = 0; i < dots.length; i++) {
            if (i === currentIndex) {
                dots[i].classList.add('active');
            } else {
                dots[i].classList.remove('active');
            }
        }
    }
    
    function nextSlide() {
        goToSlide(currentIndex + 1);
    }
    
    function startAutoSlide() {
        if (autoSlideInterval) clearInterval(autoSlideInterval);
        autoSlideInterval = setInterval(nextSlide, 3000);
    }
    
    function stopAutoSlide() {
        if (autoSlideInterval) {
            clearInterval(autoSlideInterval);
            autoSlideInterval = null;
        }
    }
    
    startAutoSlide();
    sliderContainer.addEventListener('mouseenter', stopAutoSlide);
    sliderContainer.addEventListener('mouseleave', startAutoSlide);
    
    let touchStartX = 0;
    sliderContainer.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
        stopAutoSlide();
    });
    sliderContainer.addEventListener('touchend', function(e) {
        var diff = e.changedTouches[0].screenX - touchStartX;
        if (Math.abs(diff) > 50) {
            if (diff > 0) {
                goToSlide(currentIndex - 1);
            } else {
                goToSlide(currentIndex + 1);
            }
        }
        setTimeout(startAutoSlide, 5000);
    });
});