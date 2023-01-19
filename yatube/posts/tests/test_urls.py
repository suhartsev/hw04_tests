from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.tests import const


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=const.USERNAME
        )
        cls.group = Group.objects.create(
            title=const.GROUP1_TITLE,
            slug=const.GROUP1_SLUG,
            description=const.GROUP1_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=const.TEXT,
            author=cls.user,
            group=cls.group
        )
        cls.POST_DETAIL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id}
        )
        cls.POST_EDIT = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.id}
        )

    def setUp(self):
        self.INDEX = '/'
        self.POST_CREATE = '/create/'
        self.PROFILE = reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        )
        self.GROUP_LIST = reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        )
        self.UNEXISTRING = '/unexisting_page/'
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location_all_users(self):
        """Проверка: страницы доступны всем пользователям."""
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
