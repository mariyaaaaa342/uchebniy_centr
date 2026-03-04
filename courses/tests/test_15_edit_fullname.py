from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from courses.models import Users, Profile
from .base_test import ManagedModelTestCase

class EditFullnameTest(ManagedModelTestCase):

    def setUp(self):
        # Создаём пользователя
        self.user = Users.objects.create(
            full_name='Старое Имя',
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

    def test_edit_fullname_saves_to_db(self):
        # Отправляем POST-запрос на редактирование профиля
        response = self.client.post(reverse('profile_edit'), {
            'full_name': 'Новое Имя',
            'email': 'test@example.com',
            'phone': '+79991112233'
        })
        
        # Проверяем редирект на страницу профиля после сохранения
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile'))
        
        # Обновляем данные пользователя из БД
        self.user.refresh_from_db()
        
        # Проверяем, что имя изменилось
        self.assertEqual(self.user.full_name, 'Новое Имя')