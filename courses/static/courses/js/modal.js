// Модальные окна для входа и регистрации

document.addEventListener('DOMContentLoaded', function() {
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    
    if (!loginModal || !registerModal) return;
    
    function openLoginModal() {
        loginModal.classList.add('active');
    }
    
    function openRegisterModal() {
        registerModal.classList.add('active');
    }
    
    function closeModals() {
        loginModal.classList.remove('active');
        registerModal.classList.remove('active');
    }
    
    // Закрытие по крестику
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', closeModals);
    });
    
    // Закрытие по клику вне окна
    window.addEventListener('click', (e) => {
        if (e.target === loginModal) closeModals();
        if (e.target === registerModal) closeModals();
    });
    
    // Переключение между модалками
    const showRegisterModal = document.getElementById('showRegisterModal');
    const showLoginModal = document.getElementById('showLoginModal');
    
    if (showRegisterModal) {
        showRegisterModal.addEventListener('click', (e) => {
            e.preventDefault();
            loginModal.classList.remove('active');
            registerModal.classList.add('active');
        });
    }
    
    if (showLoginModal) {
        showLoginModal.addEventListener('click', (e) => {
            e.preventDefault();
            registerModal.classList.remove('active');
            loginModal.classList.add('active');
        });
    }
    
    // Кнопки входа/регистрации в шапке
    const loginBtn = document.querySelector('.header_login-btn');
    const registerBtn = document.querySelector('.header_register-btn');
    
    if (loginBtn) {
        loginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openLoginModal();
        });
    }
    
    if (registerBtn) {
        registerBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openRegisterModal();
        });
    }
    
    // ===== МАСКА ДЛЯ ТЕЛЕФОНА =====
    const phoneInput = document.querySelector('#registerForm input[name="phone"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) value = value.slice(0, 11);
            
            let formatted = '+7';
            if (value.length > 1) {
                formatted += ' (' + value.substring(1, 4);
            }
            if (value.length >= 5) {
                formatted += ') ' + value.substring(4, 7);
            }
            if (value.length >= 8) {
                formatted += '-' + value.substring(7, 9);
            }
            if (value.length >= 10) {
                formatted += '-' + value.substring(9, 11);
            }
            e.target.value = formatted;
        });
    }
});