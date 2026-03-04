from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from courses.models import Users, Courses, Teachers, Applications
from .base_test import ManagedModelTestCase

class DuplicateApplicationTest(ManagedModelTestCase):

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
        
        # Создаём преподавателя
        self.teacher = Teachers.objects.create(
            full_name='Тестовый Преподаватель',
            email='teacher@example.com',
            experience=5
        )
        
        # Создаём курс
        self.course = Courses.objects.create(
            title='Тестовый курс',
            price_offline=10000,
            price_online=7000,
            offline_available=True,
            online_available=True,
            status='active',
            teacher=self.teacher,
            max_students=20
        )
        
        # Авторизуем пользователя
        self.client.post(reverse('login'), {
            'login_input': '+79991112233',
            'password': 'correctpass'
        })
        
        # Создаём первую заявку
        self.client.post(reverse('submit_application'), {
            'course_id': self.course.course_id,
            'format': 'онлайн'
        })

    def test_duplicate_application_fails(self):
        old_count = Applications.objects.count()
        
        response = self.client.post(reverse('submit_application'), {
            'course_id': self.course.course_id,
            'format': 'онлайн'
        })
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Вы уже записаны на этот курс')
        
        new_count = Applications.objects.count()
        self.assertEqual(new_count, old_count)