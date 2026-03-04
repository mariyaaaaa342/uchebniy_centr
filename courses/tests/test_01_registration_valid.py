# courses/tests/test_01_registration_valid.py
# ТЕСТ-КЕЙС №1: Регистрация с валидными данными
# Ожидаемый результат: пользователь создаётся в БД, редирект на страницу входа

from django.urls import reverse
from courses.models import Users
from .base_test import ManagedModelTestCase

class RegistrationValidTest(ManagedModelTestCase):

    def test_registration_creates_user(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Иван Петров',
            'phone': '+79991112233',
            'email': 'ivan@example.com',
            'password': 'secret123',
            'password_confirm': 'secret123'
        })
        # 1. Проверка редиректа на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        
        # 2. Проверка, что пользователь появился в базе данных
        user_exists = Users.objects.filter(email='ivan@example.com').exists()
        self.assertTrue(user_exists)