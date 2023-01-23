from django.test import Client, TestCase
from django.urls import reverse

from posts.tests import const
from posts.models import Group, Post, User


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=const.USERNAME)

        cls.group = Group.objects.create(
            title=const.GROUP1_TITLE,
            slug=const.GROUP1_SLUG,
            description=const.GROUP1_DESCRIPTION
        )
        cls.group2 = Group.objects.create(
            title=const.GROUP2_TITLE,
            slug=const.GROUP2_SLUG,
            description=const.GROUP2_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=const.TEXT,
            author=cls.user,
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
        cls.GROUP_LIST = reverse(
            const.GROUP_LIST,
            kwargs={'slug': cls.group.slug}
        )
        cls.GROUP_LIST_GROUP_2 = reverse(
            const.GROUP_LIST,
            kwargs={'slug': cls.group2.slug}
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_contex(self, context_page):
        """Метод проверки контекста текста поста, автора"""
        context_page = {
            context_page.text: const.TEXT,
            context_page.author: self.user,
        }
        for context, expected in context_page.items():
            self.assertEqual(context, expected)

    def test_pages_uses_correct_template(self):
        """Проверка: view-функциях используются правильные html-шаблоны"""
        templates_pages_names = {
            const.INDEX_REV: 'posts/index.html',
            const.POST_CREATE_REV: 'posts/create_post.html',
            self.GROUP_LIST: 'posts/group_list.html',
            const.PROFILE_REV: 'posts/profile.html',
            self.POST_DETAIL: 'posts/post_detail.html',
            self.POST_EDIT: 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_profile_page_shows_correct_context(self):
        """Проверка: Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(const.PROFILE_REV)
        post = response.context['page_obj'][0]
        self.check_contex(post)
        self.assertEqual(post, self.post)
        self.assertIn('author', response.context)
        self.assertIn('page_obj', response.context)

    def test_index_page_show_correct_context(self):
        """Проверка: Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(const.INDEX_REV)
        post = response.context['page_obj'][0]
        self.check_contex(post)
        self.assertEqual(post.group, self.group)
        self.assertIn('page_obj', response.context)

    def test_group_list_page_show_correct_context(self):
        """Проверка: Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.GROUP_LIST)
        group = response.context['page_obj'][0].group
        self.assertEqual(group.title, const.GROUP1_TITLE)
        self.assertEqual(group.description, const.GROUP1_DESCRIPTION)
        self.assertEqual(group.slug, const.GROUP1_SLUG)
        self.assertIn('page_obj', response.context)

    def test_post_detail_list_page_show_correct_context(self):
        """Проверка: Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_DETAIL,)
        post_detail = response.context['post']
        self.check_contex(post_detail)

    def test_post_not_in_other_group(self):
        """Проверка: Созданный пост не появился в другой группе"""
        post = self.post
        response = self.authorized_client.get(self.GROUP_LIST_GROUP_2)
        self.assertNotIn(post, response.context.get('page_obj'))
        group2 = response.context.get('group')
        self.assertNotEqual(group2, self.group)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=const.USERNAME)
        cls.author = User.objects.get(username=const.USERNAME)
        cls.group = Group.objects.create(
            title=const.GROUP1_TITLE,
            slug=const.GROUP1_SLUG,
            description=const.GROUP1_DESCRIPTION,
        )
        cls.GROUP_LIST = reverse(
            const.GROUP_LIST,
            kwargs={'slug': cls.group.slug}
        )
        cls.posts = [
            Post(
                text=f'{const.TEXT} {number_post}',
                author=cls.user,
                group=cls.group,
            )
            for number_post in range(const.TOTAL_POSTS)
        ]
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.authorized = Client()

    def test_page_paginator_obj(self):
        """Проверка: пагинатор на 1, 2 странице index, group_list, profile"""
        templates = (
            const.INDEX_HOME,
            self.GROUP_LIST,
            const.PROFILE_REV,
        )
        for address in templates:
            with self.subTest(address=address):
                response_1 = self.authorized.get(address)
                response_2 = self.authorized.get(
                    address, {'page': const.TWO_PAGE}
                )
                count_posts_1 = len(response_1.context['page_obj'])
                self.assertEqual(count_posts_1, const.LIMIT_POSTS_TEN)
                count_posts_2 = len(response_2.context['page_obj'])
                self.assertEqual(count_posts_2, const.LIMIT_POSTS_THREE)
