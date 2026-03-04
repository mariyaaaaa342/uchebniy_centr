from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from courses.models import Users
from .base_test import ManagedModelTestCase

class LoginWrongPasswordTest(ManagedModelTestCase):

    def setUp(self):
        # Создаём пользователя для теста
        self.user = Users.objects.create(
            full_name='Тестовый Пользователь',
            phone='+79991112233',
            email='test@example.com',
            password_hash=make_password('correctpass'),
            registration_date=timezone.now(),
            is_verified=True,
            theme_preference='light'
        )

    def test_login_fails_with_wrong_password(self):
        response = self.client.post(reverse('login'), {
            'login_input': '+79991112233',
            'password': 'wrongpassword'
        })
        
        # Проверяем, что нет редиректа (страница входа с ошибкой)
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что сессия не создалась
        self.assertNotIn('user_id', self.client.session)
        
        # Проверяем наличие сообщения об ошибке
        content = response.content.decode('utf-8')
        self.assertIn('Неверный телефон/email или пароль', content)