from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from courses.models import Users, Profile
from .base_test import ManagedModelTestCase

class EditInvalidEmailTest(ManagedModelTestCase):

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
        
        # Авторизуем пользователя
        self.client.post(reverse('login'), {
            'login_input': '+79991112233',
            'password': 'correctpass'
        })

    def test_edit_invalid_email_shows_error(self):
        # Отправляем POST-запрос с некорректным email
        response = self.client.post(reverse('profile_edit'), {
            'full_name': 'Тестовый Пользователь',
            'email': 'not-an-email',
            'phone': '+79991112233'
        })
        
        # Проверяем, что нет редиректа (остаёмся на странице редактирования)
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что на странице есть сообщение об ошибке (на английском)
        content = response.content.decode('utf-8')
        self.assertIn('Enter a valid email address', content)
        
        # Проверяем, что email в БД не изменился
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'test@example.com')