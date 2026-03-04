from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from courses.models import Users
from .base_test import ManagedModelTestCase

class LogoutTest(ManagedModelTestCase):

    def setUp(self):
        # Создаём пользователя
        self.user = Users.objects.create(
            full_name='Тестовый Пользователь',
            phone='+79991112233',
            email='test@example.com',
            password_hash=make_password('correctpass'),
            registration_date=timezone.now(),
            is_verified=True,
            theme_preference='light'
        )
        # Авторизуем пользователя
        self.client.post(reverse('login'), {
            'login_input': '+79991112233',
            'password': 'correctpass'
        })

    def test_logout_clears_session(self):
        # Проверяем, что сессия существует после входа
        self.assertIn('user_id', self.client.session)
        
        # Выполняем выход
        response = self.client.get(reverse('logout'))
        
        # Проверяем редирект на главную страницу
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        
        # Проверяем, что сессия очищена
        self.assertNotIn('user_id', self.client.session)