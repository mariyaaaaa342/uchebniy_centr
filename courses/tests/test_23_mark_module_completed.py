from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from courses.models import Users, Courses, Teachers, CourseProgress
from .base_test import ManagedModelTestCase

class MarkModuleCompletedTest(ManagedModelTestCase):

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
        
        # Создаём курс с программой
        self.course = Courses.objects.create(
            title='Тестовый курс',
            course_program='Модуль 1\nМодуль 2\nМодуль 3',
            price_offline=10000,
            price_online=7000,
            offline_available=True,
            online_available=True,
            status='active',
            teacher=self.teacher,
            max_students=20
        )
        
        # Создаём прогресс с одним пройденным модулем
        self.progress = CourseProgress.objects.create(
            user=self.user,
            course=self.course,
            format='онлайн',
            status='in_progress',
            modules_progress={'module_1': 'completed'}
        )

    def test_mark_module_completed(self):
        # Отмечаем module_2 как "Пройден"
        self.progress.modules_progress['module_2'] = 'completed'
        self.progress.save()
        
        # Обновляем объект из БД
        self.progress.refresh_from_db()
        
        # Проверяем, что статус модуля изменился
        self.assertEqual(self.progress.modules_progress.get('module_2'), 'completed')
        
        # Проверяем, что общий статус остался "В процессе"
        self.assertEqual(self.progress.status, 'in_progress')