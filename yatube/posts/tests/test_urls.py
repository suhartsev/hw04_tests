from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.tests import const


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(
            username=const.USERNAME
        )
        cls.other_user = User.objects.create_user(
            username=const.OTHER_USER
        )
        cls.group = Group.objects.create(
            title=const.GROUP1_TITLE,
            slug=const.GROUP1_SLUG,
            description=const.GROUP1_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=const.TEXT,
            author=cls.author_post,
            group=cls.group
        )
        cls.POST_DETAIL = reverse(
            const.POST_DETAIL,
            kwargs={'post_id': cls.post.id}
        )
        cls.POST_EDIT = reverse(
            const.POST_EDIT,
            kwargs={'post_id': cls.post.id}
        )
        cls.PROFILE = reverse(
            const.PROFILE,
            kwargs={'username': cls.author_post.username}
        )
        cls.GROUP_LIST = reverse(
            const.GROUP_LIST,
            kwargs={'slug': cls.group.slug}
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_post_client = Client()
        self.author_post_client.force_login(self.author_post)
        self.other_authorized_client = Client()
        self.other_authorized_client.force_login(self.other_user)

    def test_urls_exists_at_desired_location_client(self):
        """Проверка: доступа страниц для Автор, Гость, Пользователь"""
        url_code = (
            (self.other_authorized_client and self.guest_client,
                const.INDEX_HOME, HTTPStatus.OK),
            (self.other_authorized_client and self.guest_client,
                self.GROUP_LIST, HTTPStatus.OK),
            (self.other_authorized_client and self.guest_client,
                self.PROFILE, HTTPStatus.OK),
            (self.other_authorized_client and self.guest_client,
                self.POST_DETAIL, HTTPStatus.OK),
            (self.other_authorized_client and self.guest_client,
                const.UNEXISTRING, HTTPStatus.NOT_FOUND),
            (self.other_authorized_client and self.author_post_client,
                const.POST_CREATE, HTTPStatus.OK),
            (self.author_post_client, self.POST_EDIT, HTTPStatus.OK),
            (self.guest_client, const.POST_CREATE and self.POST_EDIT,
                HTTPStatus.FOUND),
        )
        for client, url, code in url_code:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, code)

# Я знаю, что тут нельзя писать. Но Вы не отвечаете в пачке с черверга
#  19 января.
# Я написал десяток сообщений, покажите как надо сделать,
#  мне тяжело догадываться без обратной связи
# Получилось сделать так все проверки в одном тесте,
# от гостя, авторезированного пользователя и авторезированного автора,
# проверил страници которые нужно, по другому? я не пойму,
# с Вами нет обратной связи
# Выручайте
