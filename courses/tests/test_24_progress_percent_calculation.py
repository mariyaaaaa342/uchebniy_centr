from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from courses.models import Users, Courses, Teachers, CourseProgress
from .base_test import ManagedModelTestCase

class ProgressPercentCalculationTest(ManagedModelTestCase):

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
            course_program='Модуль 1\nМодуль 2\nМодуль 3\nМодуль 4',
            price_offline=10000,
            price_online=7000,
            offline_available=True,
            online_available=True,
            status='active',
            teacher=self.teacher,
            max_students=20
        )

    def test_progress_percent_calculation(self):
        # Создаём прогресс с 2 пройденными модулями из 4
        progress = CourseProgress.objects.create(
            user=self.user,
            course=self.course,
            format='онлайн',
            status='in_progress',
            modules_progress={
                'module_1': 'completed',
                'module_2': 'completed',
                'module_3': 'not_started',
                'module_4': 'not_started'
            }
        )
        
        # Получаем все модули курса
        all_modules = [line.strip() for line in self.course.course_program.split('\n') if line.strip()]
        total_modules = len(all_modules)
        
        # Получаем прогресс
        modules_progress = progress.modules_progress or {}
        
        # Рассчитываем процент
        completed = 0
        for i in range(1, total_modules + 1):
            module_key = f'module_{i}'
            if modules_progress.get(module_key) == 'completed':
                completed += 1
        
        percent = int((completed / total_modules) * 100) if total_modules > 0 else 0
        
        # Проверяем, что процент = 50% (2 из 4)
        self.assertEqual(percent, 50)
        
        # Проверяем, что общий статус = "В процессе"
        self.assertEqual(progress.status, 'in_progress')
        