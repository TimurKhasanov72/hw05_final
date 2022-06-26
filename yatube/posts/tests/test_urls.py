from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.user2 = User.objects.create_user(username='TestUser2')
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.user
        )
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="testGroup",
            description="Описание тестовой группы"
        )
        cls.templates_url_names = {
            '/': 'posts/index.html',
            '/group/{}/'.format(cls.group.slug): 'posts/group_list.html',
            '/profile/{}/'.format(cls.user.username): 'posts/profile.html',
            '/posts/{}/'.format(cls.post.id): 'posts/post_detail.html',
            '/create/': 'posts/post_create.html',
            '/posts/{}/edit/'.format(cls.post.id): 'posts/post_create.html',
        }

    def setUp(self) -> None:
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.authorized_client.force_login(PostURLTests.user)
        self.authorized_client2.force_login(PostURLTests.user2)

    def test_home_url_exists_at_desired_location(self):
        '''Страница / доступна любому пользователю.'''
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_slug_url_exists_at_desired_location(self):
        """Страница /group/<slug>/ доступна любому пользователю."""
        response = self.guest_client.get(
            '/group/{}/'.format(self.group.slug)
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_username_url_exists_at_desired_location(self):
        """Страница /profile/<username>/ доступна любому пользователю."""
        response = self.guest_client.get(
            '/profile/{}/'.format(self.user.username)
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_url_exists_at_desired_location(self):
        """Страница /post/<post_id>/ доступна любому пользователю."""
        response = self.guest_client.get(
            '/posts/{}/'.format(self.post.id)
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_edit_url_exists_at_desired_location_authorized(self):
        """Страница /post/<post_id>/edit
        доступна авторизованному пользователю."""
        response = self.authorized_client.get(
            '/posts/{}/edit/'.format(self.post.id)
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_edit_url_redirect_anonymous(self):
        """Страница /post/<post_id>/edit
        перенаправляет анонимного пользователя."""

        response = self.guest_client.get(
            '/posts/{}/edit/'.format(self.post.id),
            follow=True
        )
        self.assertRedirects(
            response,
            (
                '/auth/login/?next=/posts/{}/edit/'
                .format(self.post.id)
            )
        )

    def test_post_id_edit_url_redirect_other_user(self):
        """Страница /post/<post_id>/edit
        перенаправляет НЕ автора."""

        response = self.authorized_client2.get(
            '/posts/{}/edit/'.format(self.post.id),
            follow=True
        )
        self.assertRedirects(
            response,
            ('/posts/{}/'.format(self.post.id))
        )

    def test_post_id_edit_url_exists_at_desired_location_author(self):
        """Страница /post/<post_id>/edit/ доступна автору."""

        response = self.authorized_client.get(
            '/posts/{}/edit/'.format(self.post.id)
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/
        доступна авторизованному пользователю."""

        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_to_login_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""

        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response,
            ('/auth/login/?next=/create/')
        )

    def test_unexisting_page_not_found(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)


class UsersURLTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.templates_url_names = {
            'users/logged_out.html': '/auth/logout/',
            'users/signup.html': '/auth/signup/',
            'users/login.html': '/auth/login/',
            'users/password_reset_form.html': '/auth/password_reset/',
            'users/password_reset_done.html': '/auth/password_reset/done/',
        }

    def setUp(cls) -> None:
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_all_urls_exists_at_desired_location(self):
        '''Все страницы доступны любому пользователю.'''

        for url in self.templates_url_names.values():
            with self.subTest(address=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, address in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
