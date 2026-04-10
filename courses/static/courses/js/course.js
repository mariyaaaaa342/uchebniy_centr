let currentCourseId = null;
let selectedFormat = null;

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.course-card').forEach(card => {
        const courseId = parseInt(card.dataset.courseId);
        const offlineAvailable = card.dataset.offlineAvailable === 'true';
        const onlineAvailable = card.dataset.onlineAvailable === 'true';
        const priceOffline = card.dataset.priceOffline;
        const priceOnline = card.dataset.priceOnline;
        
        const onlineBtn = card.querySelector('.format-online');
        const offlineBtn = card.querySelector('.format-offline');
        const courseBtn = card.querySelector('.course-btn');
        const priceElement = card.querySelector('.price');
        const unavailableMsg = card.querySelector('.format-unavailable');
        
        if (!onlineAvailable) {
            onlineBtn.classList.add('disabled');
            onlineBtn.setAttribute('data-tooltip', 'Онлайн формат недоступен');
        }
        if (!offlineAvailable) {
            offlineBtn.classList.add('disabled');
            offlineBtn.setAttribute('data-tooltip', 'Оффлайн формат недоступен');
        }
        
        // Обработчик для онлайн кнопки
        onlineBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (onlineBtn.classList.contains('disabled')) {
                if (unavailableMsg) {
                    unavailableMsg.style.display = 'block';
                    setTimeout(() => {
                        unavailableMsg.style.display = 'none';
                    }, 3000);
                }
                return;
            }
            
            onlineBtn.classList.add('active');
            offlineBtn.classList.remove('active');
            selectedFormat = 'онлайн';
            currentCourseId = courseId;
            
            if (priceElement) {
                priceElement.textContent = priceOnline + ' ₽';
            }
            
            courseBtn.disabled = false;
            courseBtn.textContent = 'Записаться';
        });
        
        offlineBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (offlineBtn.classList.contains('disabled')) {
                if (unavailableMsg) {
                    unavailableMsg.style.display = 'block';
                    setTimeout(() => {
                        unavailableMsg.style.display = 'none';
                    }, 3000);
                }
                return;
            }
            
            offlineBtn.classList.add('active');
            onlineBtn.classList.remove('active');
            selectedFormat = 'оффлайн';
            currentCourseId = courseId;
            
            if (priceElement) {
                priceElement.textContent = priceOffline + ' ₽';
            }
            
            courseBtn.disabled = false;
            courseBtn.textContent = 'Записаться';
        });
        
        courseBtn.addEventListener('click', function() {
            if (!selectedFormat) {
                showFormatError(card);
                return;
            }
            
            const courseName = card.querySelector('.course-title').textContent;
            
            document.getElementById('modalCourseTitle').textContent = `Запись на курс "${courseName}"`;
            document.getElementById('courseFormat').value = selectedFormat;
            document.getElementById('courseId').value = currentCourseId;
            
            document.getElementById('applicationForm').reset();
            
            document.getElementById('modalOverlay').classList.add('active');
            document.body.style.overflow = 'hidden';
        });
        
        function showFormatError(card) {
            let errorMsg = card.querySelector('.format-error');
            
            if (!errorMsg) {
                errorMsg = document.createElement('div');
                errorMsg.className = 'format-error';
                errorMsg.innerHTML = '⚠️ Выберите формат обучения';
                
                const formatBtns = card.querySelector('.course-format');
                formatBtns.parentNode.insertBefore(errorMsg, formatBtns.nextSibling);
            }
            
            errorMsg.style.display = 'block';
            errorMsg.style.animation = 'shake 0.5s ease';
            
            const formatBtns = card.querySelectorAll('.format-btn');
            formatBtns.forEach(btn => {
                btn.style.animation = 'pulse 1s ease';
            });
            
            setTimeout(() => {
                if (errorMsg) {
                    errorMsg.style.display = 'none';
                }
                formatBtns.forEach(btn => {
                    btn.style.animation = '';
                });
            }, 3000);
        }
    });
    
    // Функция получения CSRF-токена
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
    
    function closeModal() {
        document.getElementById('modalOverlay').classList.remove('active');
        document.body.style.overflow = '';
        document.getElementById('applicationForm').reset();
    }
    
    document.getElementById('modalClose').addEventListener('click', closeModal);
    document.getElementById('cancelBtn').addEventListener('click', closeModal);
    
    document.getElementById('modalOverlay').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
    
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 10) value = value.slice(0, 10);
            
            let formatted = '';
            for (let i = 0; i < value.length; i++) {
                if (i === 0) formatted += '(';
                if (i === 3) formatted += ') ';
                if (i === 6) formatted += '-';
                if (i === 8) formatted += '-';
                formatted += value[i];
            }
            e.target.value = formatted;
        });
    }
    
    const birthdateInput = document.getElementById('birthdate');
    if (birthdateInput) {
        birthdateInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 8) value = value.slice(0, 8);
            
            let formatted = '';
            for (let i = 0; i < value.length; i++) {
                if (i === 2 || i === 4) formatted += '.';
                formatted += value[i];
            }
            e.target.value = formatted;
        });
    }
    
    const form = document.getElementById('applicationForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Проверка авторизован ли пользователь 
            const isLoggedIn = document.body.dataset.userId && document.body.dataset.userId !== '';
            
            if (!isLoggedIn) {
                alert('Для отправки заявки необходимо войти в систему');
                window.location.href = '/login/';
                return;
            }
            
            // Собираем данные
            const formData = new FormData();
            formData.append('name', document.getElementById('name').value);
            formData.append('surname', document.getElementById('surname').value);
            formData.append('phone', document.getElementById('phone').value);
            formData.append('birthdate', document.getElementById('birthdate').value);
            formData.append('course_id', document.getElementById('courseId').value);
            formData.append('format', document.getElementById('courseFormat').value);
            
            // Отправляем на сервер
            try {
                const response = await fetch('/submit-application/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    alert('Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время.');
                    closeModal();
                } else if (response.status === 401) {
                    // Не авторизован
                    alert(data.error || 'Необходимо войти в систему');
                    window.location.href = '/login/';
                } else {
                    alert(data.error || 'Ошибка при отправке заявки. Попробуйте позже.');
                }
            } catch (error) {
                console.error('Ошибка:', error);
                alert('Ошибка при отправке заявки. Проверьте подключение к интернету.');
            }
        });
    }
});