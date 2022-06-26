import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from test_utils import get_test_image

from ..models import Group, Post

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Тестовый текст поста №1 пользователя 1',
            author=cls.user,
            group=None,
            image=None,
        )
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="testGroup",
            description="Описание тестовой группы"
        )
        cls.test_image = get_test_image()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись Post."""
        post_text = 'Тестовый заголовок399'
        posts_count = Post.objects.count()
        form_data = {
            'text': post_text,
            'group': self.group.id,
            'image': self.test_image,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={
                'username': self.user.username,
            })
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)

        # Проверяем, что создалась запись с заданным текстом
        post = Post.objects.get(text=post_text)
        self.assertEqual(
            post.text,
            post_text,
            'Не удалось найти созданный пост'
        )

        # Если пост создался корректно, то
        # проверяем его группу
        if post is not None:
            self.assertEqual(
                post.group.id,
                self.group.id,
                'Группа поста сохранилась некорректно'
            )

        # проверяем картинку
        self.assertTrue(
            post.image.name,
            'Синьор, с картиночкой что-то не так!'
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        post_text = 'Тестовый заголовок399'
        posts_count = Post.objects.count()
        form_data = {
            'text': post_text,
            'group': self.group.id,
        }

        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id
            }),
            data=form_data,
            follow=True
        )

        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={
                'post_id': self.post.id,
            },
        ))

        # Проверяем, что число постов не изменилось
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            text=post_text,
            group=self.group.id
        ))

    def test_authorized_client_add_comment(self):
        '''Авторизованный пользователь добавил комментарий.'''
        comment_text = 'Комментарий к посту № 1'
        comments_count = len(self.post.comments.all())
        form_data = {
            'text': comment_text
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )

        # проверяем, что была переадресация
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id,
            })
        )

        # добавился комментарий
        self.assertEqual(
            self.post.comments.count(),
            comments_count + 1,
            'Количество комментариев не увеличилось'
        )

        # проверяем текст комментария
        comment = self.post.comments.last()
        self.assertEqual(
            comment.text,
            comment_text,
            'Текст комментария не совпадает',
        )

    def test_guest_does_not_add_comment(self):
        '''Неавторизованный пользователь НЕ добавил комментарий.'''
        comment_text = 'Комментарий к посту № 1'
        comments_count = len(self.post.comments.all())
        form_data = {
            'text': comment_text
        }
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )

        # проверяем, что была переадресация
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )

        # кол-во комментариев не изменилось
        self.assertEqual(
            self.post.comments.count(),
            comments_count,
            'Количество комментариев увеличилось'
        )
