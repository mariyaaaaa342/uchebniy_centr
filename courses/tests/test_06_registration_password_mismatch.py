from django.urls import reverse
from courses.models import Users
from .base_test import ManagedModelTestCase

class RegistrationPasswordMismatchTest(ManagedModelTestCase):

    def test_registration_fails_when_passwords_differ(self):
        old_count = Users.objects.count()
        
        response = self.client.post(reverse('register'), {
            'full_name': 'Илья Морозов',
            'phone': '+79995556677',
            'email': 'ilya@example.com',
            'password': 'secret123',
            'password_confirm': 'different456'
        })
        
        new_count = Users.objects.count()
        self.assertEqual(old_count, new_count)
        
        # Выводим содержимое ответа для отладки
        #print("\n=== СОДЕРЖИМОЕ ОТВЕТА ===")
       # print(response.content.decode('utf-8'))
       # print("=== КОНЕЦ ОТВЕТА ===\n")
        
        # Проверяем наличие сообщения
        content = response.content.decode('utf-8')
        self.assertIn('пароли не совпадают', content.lower())