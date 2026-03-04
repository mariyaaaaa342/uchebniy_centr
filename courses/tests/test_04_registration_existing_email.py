from django.contrib.auth.hashers import make_password
from django.urls import reverse
from courses.models import Users
from .base_test import ManagedModelTestCase

class RegistrationExistingEmailTest(ManagedModelTestCase):

    def setUp(self):
        # Этот метод выполняется ПЕРЕД КАЖДЫМ тестом
        Users.objects.create(
            full_name='Существующий Пользователь',
            phone='+79990001122',
            email='existing@example.com',
            password_hash=make_password('somepass')
        )

    def test_registration_fails_with_existing_email(self):
        # Подсчитываем количество пользователей до запроса
        old_count = Users.objects.count()
        
        response = self.client.post(reverse('register'), {
            'full_name': 'Новый Пользователь',
            'phone': '+79994445566',
            'email': 'existing@example.com',  # существующий email
            'password': 'secret123',
            'password_confirm': 'secret123'
        })
        
        # Проверяем, что количество пользователей не увеличилось
        new_count = Users.objects.count()
        self.assertEqual(old_count, new_count)
        
        # Проверяем, что есть сообщение об ошибке
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'существует')