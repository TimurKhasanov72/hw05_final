from django.test import Client, TestCase
from django.urls import reverse

from test_utils import pages_uses_correct_template


class UsersPagesTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'users/signup.html': reverse('users:signup'),
            'users/login.html': reverse('users:login'),
            'users/logged_out.html': reverse('users:logout'),
            'users/password_reset_form.html': reverse('users:password_reset'),
            'users/password_reset_done.html': reverse(
                'users:password_reset_done'
            ),

        }

        pages_uses_correct_template(self, templates_pages_names)
