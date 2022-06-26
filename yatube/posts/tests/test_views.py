import shutil
import tempfile

from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache

from test_utils import (
    assert_is_instanse_fields,
    assert_in, get_test_image,
    search_post_by_text
)
from ..models import Follow, Group, Post

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # три пользюка
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.user3 = User.objects.create_user(username='auth3')

        # одна группа
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="testGroup",
            description="Описание тестовой группы"
        )

        cls.upload_image = get_test_image()

        # четыре поста
        # два поста для user
        cls.user_post1 = Post.objects.create(
            text='Тестовый текст поста №1 пользователя 1',
            author=cls.user,
            group=cls.group,
            image=cls.upload_image,
        )
        cls.user_post2 = Post.objects.create(
            text='Тестовый текст поста №2 пользователя 1',
            author=cls.user,
        )
        # два поста для user2
        cls.user2_post1 = Post.objects.create(
            text='Тестовый текст поста №1 пользователя 2',
            author=cls.user2,
            group=cls.group,
            image=cls.upload_image,
        )
        cls.user2_post2 = Post.objects.create(
            text='Тестовый текст поста №2 пользователя 2',
            author=cls.user2,
            group=cls.group,
            image=cls.upload_image,
        )
        cls.templates_pages_names = [
            {
                'template': 'posts/index.html',
                'reverse_name': reverse('posts:index'),
            },
            {
                'template': 'posts/group_list.html',
                'reverse_name': reverse('posts:group_list', kwargs={
                    'slug': cls.group.slug
                }),
            },
            {
                'template': 'posts/post_detail.html',
                'reverse_name': (reverse(
                    'posts:post_detail', kwargs={
                        'post_id': cls.user_post1.id
                    })
                ),
            },
            {
                'template': 'posts/profile.html',
                'reverse_name': reverse(
                    'posts:profile', kwargs={'username': cls.user.username}
                ),
            },
            {
                'template': 'posts/post_create.html',
                'reverse_name': reverse('posts:post_create'),
            },
            {
                'template': 'posts/post_create.html',
                'reverse_name': reverse('posts:post_edit', kwargs={
                    'post_id': cls.user_post1.id
                }),
            }
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

        self.authorized_client3 = Client()
        self.authorized_client3.force_login(PostPagesTests.user3)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        for item in self.templates_pages_names:
            template = item["template"]
            reverse_name = item["reverse_name"]
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_index_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))

        assert_in(self, 'page_obj', response.context)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_author_0 = first_object.author
        post_image_0 = first_object.image
        # берём самый первый пост
        first_of_all = Post.objects.first()

        self.assertEqual(post_text_0, first_of_all.text)
        self.assertEqual(post_author_0.username, first_of_all.author.username)
        # у поста есть изображение?
        self.assertEqual(
            post_image_0,
            first_object.image,
            'У поста нет переданного изображения'
        )
        # пробуем проверить группу поста
        if first_of_all.group is not None:
            self.assertEqual(
                post_group_0.title,
                first_of_all.group.title
            )

    def test_posts_group_list_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={
                'slug': self.group.slug,
            }))

        # Проверяем название группы
        assert_in(self, 'group', response.context)
        self.assertEqual(response.context.get('group').title, self.group.title)
        # Проверяем первый пост
        assert_in(self, 'page_obj', response.context)
        self.assertEqual(
            response.context['page_obj'][0].text,
            self.group.posts.first().text
        )
        # прооверяем картинку
        self.assertEqual(
            response.context['page_obj'][0].image,
            self.group.posts.first().image
        )
        # Проверяем кол-во постов у группы
        self.assertEqual(
            len(response.context['page_obj']),
            self.group.posts.count()
        )

    def test_profile_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={
                'username': self.user.username,
            }
        ))
        # проверяем имя автора в профиле
        assert_in(self, 'author', response.context)
        self.assertEqual(
            response.context.get('author').username,
            self.user.username
        )
        # проверяем, что у в профиле показан первый пост автора
        assert_in(self, 'page_obj', response.context)
        self.assertEqual(
            response.context.get('page_obj')[0].id,
            self.user.posts.first().id
        )
        # проверяем картинку
        self.assertEqual(
            response.context.get('page_obj')[0].image,
            self.user.posts.first().image
        )
        # проверяем кол-во постов у автора
        self.assertEqual(
            len(response.context.get('page_obj')),
            self.user.posts.count()
        )

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail', kwargs={
                'post_id': self.user2_post1.id
            })
        ))
        assert_in(self, 'post', response.context)
        post = response.context.get('post')
        # смотрим на текст, дату публикации и автора
        self.assertEqual(post.id, self.user2_post1.id)
        self.assertEqual(post.text, self.user2_post1.text)
        self.assertEqual(post.pub_date, self.user2_post1.pub_date)
        self.assertEqual(
            post.author.username,
            self.user2.username
        )
        # проверяем, что создали картинку какую надо
        self.assertEqual(
            post.image,
            self.user2_post1.image
        )

    def test_post_edit_show_correct_context(self):
        """Шаблон post_create.html при редактировании поста
        сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_edit', kwargs={
                'post_id': self.user_post2.id
            })
        ))
        assert_is_instanse_fields(
            self,
            response,
            {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField
            }
        )

    def test_post_create_show_correct_context(self):
        """Шаблон post_create.html при создании поста
        сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_create')))
        assert_is_instanse_fields(
            self,
            response,
            {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
        )

    def test_post_cached_index(self):
        '''Проверяме кеширование главной страницы (posts:index).'''

        # Получаем и запоминаем исходную главную страницу
        response = self.authorized_client.get(reverse('posts:index'))
        origin_content = response.content.decode()

        # Создаем еще один пост
        self.post = Post.objects.create(
            text='-------Еще один пост!!!!!---------',
            author=self.user,
            group=self.group,
        )

        # Страница НЕ поменялась, т.е. выполнена выдача из кэша
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            origin_content,
            response.content.decode(),
            'index.html не совпадает с закешированной страницей'
        )

        # Чистим кэш
        cache.clear()

        # Проверяем, что выдача поменялась
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(
            origin_content,
            response.content.decode(),
            'index.html НЕ поменялся после удаления кэша'
        )

    def test_authorized_client_can_follow_and_unfollow(self):
        '''Авторизованный пользователь может подписываться и отписываться.'''
        # подписываемся
        response = self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={
                'username': self.user2.username
            })
        )

        # ждем перенапавления
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user2.username
        }))

        # проверяем наличие подписки
        self.assertTrue(Follow.objects.filter(
            user=self.user,
            author=self.user2
        ))

        # отписываемся
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={
                'username': self.user2.username
            })
        )

        # ждем перенапавления
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user2.username
        }))

        # проверяем, что подписки больше нет
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=self.user2
        ))

    def test_follower_get_new_author_post(self):
        '''Подписчик видит новую запись автора.'''

        # user1 подписывается на user2
        self.authorized_client.get(reverse('posts:profile_follow', kwargs={
            'username': self.user2.username
        }))

        # user2 создает новую запись
        post = Post.objects.create(
            text='Новая запись автора 2. Юху!',
            author=self.user2,
        )

        # user1 смотрит, шо там у него в избранном
        response = self.authorized_client.get(reverse('posts:follow_index'))

        # ищем новый пост в ответе
        self.assertIsNotNone(search_post_by_text(
            response.context['page_obj'],
            post.text
        ))

    def test_other_user_doesnt_see_author_new_post(self):
        '''Подписчик видит новую запись автора.'''

        # user3 подписывается на user1
        self.authorized_client3.get(reverse('posts:profile_follow', kwargs={
            'username': self.user.username
        }))

        # user2 создает новую запись
        post = Post.objects.create(
            text='Новая запись автора 2. Юху!',
            author=self.user2,
        )

        # user3 смотрит, шо там у него в избранном
        response = self.authorized_client3.get(reverse('posts:follow_index'))

        # поста user2 не должно быть в ответе
        self.assertIsNone(search_post_by_text(
            response.context['page_obj'],
            post.text
        ))


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # два пользюка
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='auth2')
        # одна группа
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="testGroup",
            description="Описание тестовой группы"
        )

        # создаем 13 постов
        objs = []
        for i in range(13):
            author = cls.user if i % 2 == 0 else cls.user2
            group = cls.group if i % 2 == 0 else None
            objs.append(Post(
                text='Тестовый текст поста №{} пользователя 1'.format(i),
                author=author,
                group=group,
            ))

        Post.objects.bulk_create(objs)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_index_first_page_contains_ten_records(self):
        '''Проверка: количество постов на первой странице равно 10.'''
        response = self.client.get(reverse('posts:index'))
        assert_in(self, 'page_obj', response.context)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        '''Проверка: на второй странице должно быть три поста.'''
        response = self.client.get(reverse('posts:index') + '?page=2')
        assert_in(self, 'page_obj', response.context)
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_has_correct_posts_count(self):
        '''Проверка: количество постов в группе корректно.'''
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        ))
        assert_in(self, 'page_obj', response.context)
        self.assertEqual(
            len(response.context['page_obj']),
            self.group.posts.count()
        )

    def test_profile_has_correct_posts_count(self):
        '''Проверка: количество постов в профиле корректно.'''
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user2.username}
        ))
        assert_in(self, 'page_obj', response.context)
        self.assertEqual(
            len(response.context['page_obj']),
            self.user2.posts.count()
        )
