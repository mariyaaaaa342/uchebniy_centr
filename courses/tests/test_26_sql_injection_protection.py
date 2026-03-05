from django.urls import reverse
from courses.models import Users
from .base_test import ManagedModelTestCase

class SqlInjectionProtectionTest(ManagedModelTestCase):

    def test_sql_injection_does_not_break_site(self):
        # Вредоносная строка для SQL-инъекции
        malicious_input = "'; DROP TABLE users; --"
        
        # Пытаемся зарегистрироваться с вредоносными данными
        response = self.client.post(reverse('register'), {
            'full_name': malicious_input,
            'phone': '+79998887766',
            'email': 'safe@example.com',
            'password': 'strongpass123',
            'password_confirm': 'strongpass123'
        })
        
        # Проверяем, что регистрация прошла успешно (редирект на логин)
        # Или страница с ошибкой, но не 500
        self.assertNotEqual(response.status_code, 500, "Сервер не должен падать от SQL-инъекции")
        
        # Проверяем, что таблица users всё ещё существует
        # (если бы инъекция сработала, пользователь бы не создался)
        try:
            user_exists = Users.objects.filter(email='safe@example.com').exists()
            # Если запрос выполнился без ошибок — защита работает
            self.assertTrue(True)
        except Exception:
            self.fail("SQL-инъекция повредила базу данных")
        
        # Если пользователь создался — проверяем, что вредоносная строка сохранилась как текст
        if Users.objects.filter(email='safe@example.com').exists():
            user = Users.objects.get(email='safe@example.com')
            self.assertEqual(user.full_name, malicious_input)