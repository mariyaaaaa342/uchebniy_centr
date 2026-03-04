from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from courses.models import Users, Profile
from .base_test import ManagedModelTestCase

class ProfileAccessAuthenticatedTest(ManagedModelTestCase):

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
        # Создаём профиль
        Profile.objects.get_or_create(user=self.user)
        
        # Пытаемся авторизоваться
        login_response = self.client.post(reverse('login'), {
            'login_input': '+79991112233',
            'password': 'correctpass'
        })
        
       
    def test_authenticated_user_can_access_profile(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Тестовый Пользователь', content)