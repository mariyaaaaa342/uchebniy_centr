from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from courses.models import Users, Courses, Teachers, CourseProgress
from .base_test import ManagedModelTestCase

class AutoUpdateCourseStatusTest(ManagedModelTestCase):

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

    def test_auto_update_status_to_completed_when_all_modules_done(self):
        # Создаём прогресс с двумя пройденными модулями
        progress = CourseProgress.objects.create(
            user=self.user,
            course=self.course,
            format='онлайн',
            status='in_progress',
            modules_progress={
                'module_1': 'completed',
                'module_2': 'completed',
                'module_3': 'not_started'
            }
        )
        
        # Проверяем, что статус "В процессе"
        self.assertEqual(progress.status, 'in_progress')
        
        # Отмечаем последний модуль как пройденный
        progress.modules_progress['module_3'] = 'completed'
        progress.save()
        
        # Обновляем объект из БД
        progress.refresh_from_db()
        
        # Проверяем, что статус изменился на "Завершён"
        self.assertEqual(progress.status, 'completed')
        
        # Проверяем, что все модули пройдены
        for i in range(1, 4):
            self.assertEqual(progress.modules_progress.get(f'module_{i}'), 'completed')