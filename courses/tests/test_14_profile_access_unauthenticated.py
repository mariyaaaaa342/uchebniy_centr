from django.urls import reverse
from .base_test import ManagedModelTestCase

class ProfileAccessUnauthenticatedTest(ManagedModelTestCase):

    def test_unauthenticated_user_redirected_to_login(self):
        # Не авторизуемся — просто пытаемся открыть профиль
        response = self.client.get(reverse('profile'))
        
        # Проверяем, что произошёл редирект на страницу входа
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что URL редиректа содержит '/login/'
        self.assertTrue(response.url.startswith(reverse('login')))
        
        # Проверяем, что сессия не содержит user_id
        self.assertNotIn('user_id', self.client.session)