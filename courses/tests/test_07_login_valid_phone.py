from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from courses.models import Users
from .base_test import ManagedModelTestCase

class LoginValidPhoneTest(ManagedModelTestCase):

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

    def test_login_with_valid_phone_success(self):
        response = self.client.post(reverse('login'), {
            'login_input': '+79991112233',
            'password': 'correctpass'
        })
        
        # Проверяем редирект на главную страницу
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        
        # Проверяем, что сессия создалась
        self.assertIn('user_id', self.client.session)
        self.assertEqual(self.client.session['user_id'], self.user.user_id)