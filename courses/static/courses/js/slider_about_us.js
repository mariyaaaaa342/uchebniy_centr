document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.slider-card');
    const dots = document.querySelectorAll('.dot');
    const leftArrow = document.querySelector('.arrow-left');
    const rightArrow = document.querySelector('.arrow-right');
    
    let currentIndex = 1; 
    let isMobile = window.innerWidth <= 767;
    
    
    function updateDesktopPositions() {
        cards.forEach(card => {
            card.classList.remove('card-left', 'card-center', 'card-right');
        });
        
        if (currentIndex === 0) {
            cards[0].classList.add('card-center');
            cards[1].classList.add('card-right');
            cards[2].classList.add('card-left');
        } else if (currentIndex === 1) {
            cards[0].classList.add('card-left');
            cards[1].classList.add('card-center');
            cards[2].classList.add('card-right');
        } else if (currentIndex === 2) {
            cards[0].classList.add('card-right');
            cards[1].classList.add('card-left');
            cards[2].classList.add('card-center');
        }
        
        dots.forEach((dot, index) => {
            if (index === currentIndex) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }
    
    function updateMobilePositions() {
        cards.forEach((card, index) => {
            if (index === currentIndex) {
                card.classList.add('active');
            } else {
                card.classList.remove('active');
            }
        });
        
        dots.forEach((dot, index) => {
            if (index === currentIndex) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }
    
    function updatePositions() {
        isMobile = window.innerWidth <= 767;
        
        if (isMobile) {
            updateMobilePositions();
        } else {
            updateDesktopPositions();
        }
    }
    
    leftArrow.addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + cards.length) % cards.length;
        updatePositions();
    });
    
    rightArrow.addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % cards.length;
        updatePositions();
    });
    
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            currentIndex = index;
            updatePositions();
        });
    });
    
    window.addEventListener('resize', () => {
        updatePositions();
    });
    
    updatePositions();
});