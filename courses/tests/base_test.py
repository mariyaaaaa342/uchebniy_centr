from django.test import TestCase
from django.db import connection
from django.core.management import call_command
from django.apps import apps

class ManagedModelTestCase(TestCase):
    """Базовый класс для тестов, который создаёт таблицы для managed=False моделей"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Получаем все модели приложения courses
        app_models = apps.get_app_config('courses').get_models()
        
        # Создаём таблицы для каждой модели (если они ещё не созданы)
        with connection.schema_editor() as schema_editor:
            for model in app_models:
                if not model._meta.managed:
                    # Для managed=False моделей создаём таблицы принудительно
                    if not model._meta.db_table in connection.introspection.table_names():
                        schema_editor.create_model(model)
        
        # Загружаем фикстуры или тестовые данные, если нужно
        call_command('flush', verbosity=0, interactive=False)
        # Здесь можно добавить загрузку начальных данных

    def login_user(self, user):
        """Принудительная авторизация пользователя в тестах"""
        session = self.client.session
        session['user_id'] = user.user_id
        session['user_name'] = user.full_name
        session.save()
        return self.client
    
    def force_login(self, user):
        """Принудительная установка сессии для тестов"""
        session = self.client.session
        session['user_id'] = user.user_id
        session['user_name'] = user.full_name
        session.save()
        return self.client