from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from courses.models import Users, Courses, Teachers, Applications, CourseProgress
from .base_test import ManagedModelTestCase

class ProgressCreatedOnConfirmTest(ManagedModelTestCase):

    def setUp(self):
        # Создаём пользователя
        self.user = Users.objects.create(
            full_name='Тестовый Пользователь',
            phone='+79991112233',
            email='test@example.com',
            password_hash=make_password('pass'),
            registration_date=timezone.now(),
            is_verified=True
        )
        
        # Создаём преподавателя
        self.teacher = Teachers.objects.create(
            full_name='Тестовый Преподаватель',
            email='teacher@example.com'
        )
        
        # Создаём курс
        self.course = Courses.objects.create(
            title='Тестовый курс',
            price_offline=10000,
            price_online=7000,
            offline_available=True,
            online_available=True,
            status='active',
            teacher=self.teacher
        )

    def test_progress_created_when_application_confirmed(self):
        # Создаём заявку со статусом new
        application = Applications.objects.create(
            user=self.user,
            course=self.course,
            format='онлайн',
            status='new'
        )
        
        # Проверяем, что прогресса ещё нет
        self.assertFalse(CourseProgress.objects.filter(user=self.user, course=self.course).exists())
        
        # Меняем статус на confirmed (имитируем действие админа)
        application.status = 'confirmed'
        application.save()
        
        # Проверяем, что прогресс создался
        self.assertTrue(CourseProgress.objects.filter(user=self.user, course=self.course).exists())
        
        progress = CourseProgress.objects.get(user=self.user, course=self.course)
        self.assertEqual(progress.status, 'not_started')