# courses/tests/test_02_registration_no_at.py
# ТЕСТ-КЕЙС №2: Регистрация с некорректным email (без @)
# Ожидаемый результат: форма не отправляется, сообщение об ошибке

from django.urls import reverse
from courses.models import Users
from .base_test import ManagedModelTestCase

class RegistrationValidTest(ManagedModelTestCase):

    def test_registration_fails_without_at_in_email(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Анна Смирнова',
            'phone': '+79992223344',
            'email': 'annamail.ru',  # нет символа @
            'password': 'secret123',
            'password_confirm': 'secret123'
        })
        # 1. Нет редиректа (статус 200, форма перезагружена с ошибкой)
        self.assertEqual(response.status_code, 200)
        
        # 2. Проверка, что пользователь НЕ создался в БД
        user_exists = Users.objects.filter(email='annamail.ru').exists()
        self.assertFalse(user_exists)
        
        # 3. Проверка, что на странице есть сообщение об ошибке
        self.assertContains(response, 'Enter a valid email address')