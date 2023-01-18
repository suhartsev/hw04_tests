from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()

USERNAME = 'User_test'
TEXT = 'text_test'
GROUP_SLUG = 'slug_test'
GROUP_TITLE = "Title"
GROUP_DESCRIPTION = "descr_test"


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=USERNAME
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=TEXT,
            author=cls.user,
            group=cls.group
        )
        cls.POST_DETAIL = f'/posts/{cls.post.id}/'
        cls.POST_EDIT = f'/posts/{cls.post.id}/edit/'

    def setUp(self):
        self.INDEX = '/'
        self.POST_CREATE = '/create/'
        self.PROFILE = f'/profile/{self.user.username}/'
        self.GROUP_LIST = f'/group/{self.group.slug}/'
        self.UNEXISTRING = '/unexisting_page/'
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """Проверка: URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            f'{self.INDEX}': 'posts/index.html',
            f'{self.POST_CREATE}': 'posts/create_post.html',
            f'{self.GROUP_LIST}': 'posts/group_list.html',
            f'{self.PROFILE}': 'posts/profile.html',
            f'{self.POST_DETAIL}': 'posts/post_detail.html',
            f'{self.POST_EDIT}': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_desired_location(self):
        """Проверка страниц на доступность авторизованному пользователю."""
        static_urls = {
            f'{self.INDEX}': HTTPStatus.OK,
            f'{self.POST_CREATE}': HTTPStatus.OK,
            f'{self.GROUP_LIST}': HTTPStatus.OK,
            f'{self.PROFILE}': HTTPStatus.OK,
            f'{self.POST_DETAIL}': HTTPStatus.OK,
            f'{self.POST_EDIT}': HTTPStatus.OK,
        }
        for address, response_on_url in static_urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, response_on_url)

    def test_urls_exists_at_desired_location_all_users(self):
        """Проверка страниц на доступность госям (всем пользователям)."""
        static_urls = {
            f'{self.INDEX}': HTTPStatus.OK,
            f'{self.GROUP_LIST}': HTTPStatus.OK,
            f'{self.PROFILE}': HTTPStatus.OK,
            f'{self.POST_DETAIL}': HTTPStatus.OK,
        }
        for address, response_on_url in static_urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, response_on_url)

    def test_unexisting_page(self):
        """Проверка: Страница /unexisting_page/ не существует 404"""
        response = self.guest_client.get(f'{self.UNEXISTRING}')
        self.assertEqual(response.status_code, 404)

    def test_post_create_url_exists_at_desired_location(self):
        """Проверка: Страница /create/ доступна авторизованному пользователю"""
        response = self.authorized_client.get(f'{self.POST_CREATE}')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_at_desired_location(self):
        """Проверка: Страница /posts/<post_id>/edit/ доступна автору."""
        response = self.authorized_client.get(f'{self.POST_EDIT}')
        self.assertEqual(response.status_code, HTTPStatus.OK)
