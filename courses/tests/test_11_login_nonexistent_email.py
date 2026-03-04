from django.urls import reverse
from .base_test import ManagedModelTestCase

class LoginNonexistentEmailTest(ManagedModelTestCase):

    def test_login_fails_with_unregistered_email(self):
        response = self.client.post(reverse('login'), {
            'login_input': 'nonexistent@example.com',
            'password': 'anypass'
        })
        
        # Проверяем, что нет редиректа (страница входа с ошибкой)
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что сессия не создалась
        self.assertNotIn('user_id', self.client.session)
        
        # Проверяем наличие сообщения об ошибке
        content = response.content.decode('utf-8')
        self.assertIn('Неверный телефон/email или пароль', content)