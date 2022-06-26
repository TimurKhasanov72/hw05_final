from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserCreateFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_create_new_user(self):
        """Валидная форма создает нового пользователя."""
        users_count = User.objects.count()
        username = 'test_auth_test'
        form_data = {
            'first_name': 'first_test',
            'last_name': 'last_test',
            'email': 'hagi-vagi@mail.ru',
            'username': username,
            'password1': 'Habaduba336',
            'password2': 'Habaduba336'
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:index')
        )
        # Проверяем, увеличилось ли число пользователей
        self.assertEqual(User.objects.count(), users_count + 1)
        # Проверяем, что создался пользователь
        self.assertTrue(
            User.objects.filter(
                username=username,
            ).exists()
        )
