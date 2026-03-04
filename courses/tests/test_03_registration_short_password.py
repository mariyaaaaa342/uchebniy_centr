# courses/tests/test_02_registration_no_at.py
# ТЕСТ-КЕЙС №2: Регистрация с некорректным email (без @)
# Ожидаемый результат: форма не отправляется, сообщение об ошибке

from django.urls import reverse
from courses.models import Users
from .base_test import ManagedModelTestCase

class RegistrationValidTest(ManagedModelTestCase):

    def test_registration_fails_without_at_in_email(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Ольга Козлова',
            'phone': '+79993334455',
            'email': 'olga@example.com',
            'password': '12',        # короткий пароль
            'password_confirm': '12'
        })
        # 1. Нет редиректа (статус 200, форма перезагружена с ошибкой)
        self.assertEqual(response.status_code, 200)
        
        # 2. Проверка, что пользователь НЕ создался в БД
        user_exists = Users.objects.filter(email='olga@example.com').exists()
        self.assertFalse(user_exists)
        
        # 3. Проверка наличия сообщения о минимальной длине пароля
        self.assertContains(response, 'Ensure this value has at least 6 characters (it has 2).')