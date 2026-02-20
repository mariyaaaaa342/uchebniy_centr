// Бургер-меню
document.addEventListener('DOMContentLoaded', function() {
    const burger = document.getElementById('burger');
    const menu = document.getElementById('menu');
    const overlay = document.getElementById('overlay');
    
    function toggleMenu() {
        burger.classList.toggle('active');
        menu.classList.toggle('active');
        overlay.classList.toggle('active');
        document.body.style.overflow = menu.classList.contains('active') ? 'hidden' : '';
    }
    
    burger.addEventListener('click', toggleMenu);
    overlay.addEventListener('click', toggleMenu);
    
    // Закрытие меню при клике на ссылку
    const menuLinks = document.querySelectorAll('.header_menu-link');
    menuLinks.forEach(link => {
        link.addEventListener('click', toggleMenu);
    });
});