from django.utils import timezone
from courses.models import Users, Courses, Teachers, CourseProgress
from .base_test import ManagedModelTestCase

class MarkModuleInProgressTest(ManagedModelTestCase):

    def setUp(self):
        # Создаём пользователя
        self.user = Users.objects.create(
            full_name='Тестовый Пользователь',
            phone='+79991112233',
            email='test@example.com'
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
        
        # Создаём прогресс
        self.progress = CourseProgress.objects.create(
            user=self.user,
            course=self.course,
            format='онлайн',
            status='not_started',
            modules_progress={}
        )

    def test_mark_module_in_progress(self):
        # Отмечаем module_1 как "в процессе"
        self.progress.modules_progress['module_1'] = 'in_progress'
        self.progress.save()
        
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.modules_progress.get('module_1'), 'in_progress')
        self.assertEqual(self.progress.status, 'in_progress')