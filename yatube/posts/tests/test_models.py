from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostTestModel(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая гурппа',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        '''Проверяем, что у моделей корректно работает __str__.'''

        fields = {
            self.group.title: str(self.group),
            self.post.text[:15]: str(self.post),
        }

        for value, expected in fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_post_fields_have_verbose_names(self):
        '''Проверяем, что verbose_name у полей модели Post не пустой'''

        field_verbose_name = [
            'text', 'pub_date', 'author', 'group'
        ]

        for value in field_verbose_name:
            with self.subTest(value=value):
                self.assertNotEqual(
                    self.post._meta.get_field(value).verbose_name,
                    ''
                )

    def test_post_fields_have_help_text(self):
        '''Проверяем, что help_text у модели Post задан должным образом'''

        need_has_help_text = {
            'text': True,
            'pub_date': False,
            'author': False,
            'group': True,
        }

        for value, has_help_text in need_has_help_text.items():
            with self.subTest(value=value):
                if has_help_text:
                    self.assertNotEqual(
                        self.post._meta.get_field(value).help_text,
                        ''
                    )
                else:
                    self.assertEqual(
                        self.post._meta.get_field(value).help_text,
                        ''
                    )
