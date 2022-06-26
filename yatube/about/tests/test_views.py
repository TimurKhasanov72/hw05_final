from django.test import Client, TestCase
from django.urls import reverse

from test_utils import pages_uses_correct_template


class AboutPagesTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'about/tech.html': reverse('about:tech'),
            'about/author.html': reverse('about:author'),
        }

        pages_uses_correct_template(self, templates_pages_names)
