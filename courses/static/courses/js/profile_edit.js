    // Маска для дополнительного телефона
    const phoneInput = document.querySelector('input[name="phone_alt"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 10) value = value.slice(0, 10);
            let formatted = '+7';
            if (value.length > 0) formatted += ' (' + value.substring(0, 3);
            if (value.length >= 4) formatted += ') ' + value.substring(3, 6);
            if (value.length >= 7) formatted += '-' + value.substring(6, 8);
            if (value.length >= 9) formatted += '-' + value.substring(8, 10);
            e.target.value = formatted;
        });
    }
