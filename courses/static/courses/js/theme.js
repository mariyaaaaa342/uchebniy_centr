// Получение CSRF-токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('themeToggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Применяем сохранённую тему
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-theme');
        if (toggle) toggle.checked = true;
    }
    
    // Обработчик переключения
    if (toggle) {
        toggle.addEventListener('change', function(e) {
            if (e.target.checked) {
                document.body.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
                saveThemePreference('dark');
            } else {
                document.body.classList.remove('dark-theme');
                localStorage.setItem('theme', 'light');
                saveThemePreference('light');
            }
        });
    }
    
    // Сохранение выбора на сервере (для авторизованных пользователей)
    function saveThemePreference(theme) {
        const userId = document.body.dataset.userId;
        if (userId && userId !== '') {
            fetch('/save-theme/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ theme: theme })
            }).catch(error => console.error('Ошибка сохранения темы:', error));
        }
    }
});