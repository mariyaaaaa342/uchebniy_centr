from django.contrib.auth.hashers import make_password, check_password
from courses.models import Users
from .base_test import ManagedModelTestCase

class PasswordHashingTest(ManagedModelTestCase):

    def test_password_is_hashed_not_stored_in_plain_text(self):
        raw_password = 'mysecretpassword'
        
        # Создаём пользователя с хэшированным паролем
        user = Users.objects.create(
            full_name='Тестовый Пользователь',
            phone='+79991112233',
            email='test_hash@example.com',
            password_hash=make_password(raw_password)
        )
        
        # 1. Пароль не должен храниться в открытом виде
        self.assertNotEqual(user.password_hash, raw_password,
                            "Пароль не должен храниться в открытом виде")
        
        # 2. Хэш должен отличаться от исходного пароля
        self.assertNotEqual(user.password_hash, raw_password)
        
        # 3. Проверка пароля должна работать
        self.assertTrue(check_password(raw_password, user.password_hash),
                        "Правильный пароль должен проходить проверку")
        
        # 4. Неправильный пароль не должен проходить проверку
        self.assertFalse(check_password('wrongpassword', user.password_hash),
                         "Неправильный пароль не должен проходить проверку")