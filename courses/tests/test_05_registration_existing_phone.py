from django.contrib.auth.hashers import make_password
from django.urls import reverse
from courses.models import Users
from .base_test import ManagedModelTestCase

class RegistrationExistingPhoneTest(ManagedModelTestCase):

    def setUp(self):
        # Создаём пользователя с существующим телефоном
        Users.objects.create(
            full_name='Существующий Пользователь',
            phone='+79990001122',
            email='some@example.com',
            password_hash=make_password('somepass')
        )

    def test_registration_fails_with_existing_phone(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Новый Пользователь',
            'phone': '+79990001122',  # телефон уже занят
            'email': 'new@example.com',
            'password': 'secret123',
            'password_confirm': 'secret123'
        })
        # 1. Нет редиректа (статус 200)
        self.assertEqual(response.status_code, 200)
        
        # 2. Проверка сообщения об ошибке
        self.assertContains(response, 'Пользователь с таким номером телефона уже существует')