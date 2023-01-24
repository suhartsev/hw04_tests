from django.test import Client, TestCase
from django.urls import reverse

from posts.tests import const
from posts.models import Group, Post, User


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=const.STR_USERNAME)

        cls.group = Group.objects.create(
            title=const.STR_GROUP1_TITLE,
            slug=const.STR_GROUP1_SLUG,
            description=const.STR_GROUP1_DESCRIPTION
        )
        cls.group2 = Group.objects.create(
            title=const.STR_GROUP2_TITLE,
            slug=const.STR_GROUP2_SLUG,
            description=const.STR_GROUP2_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=const.STR_TEXT,
            author=cls.user,
            group=cls.group
        )
        cls.POST_DETAIL = reverse(
            const.URL_POST_DETAIL,
            kwargs={'post_id': cls.post.id}
        )
        cls.POST_EDIT = reverse(
            const.URL_POST_EDIT,
            kwargs={'post_id': cls.post.id}
        )
        cls.GROUP_LIST = reverse(
            const.URL_GROUP_LIST,
            kwargs={'slug': cls.group.slug}
        )
        cls.GROUP_LIST_GROUP_2 = reverse(
            const.URL_GROUP_LIST,
            kwargs={'slug': cls.group2.slug}
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_contex(self, context_page):
        """Метод проверки контекста текста поста, автора"""
        context_page = {
            context_page.text: const.STR_TEXT,
            context_page.author: self.user,
            context_page.group: self.group
        }
        for context, expected in context_page.items():
            self.assertEqual(context, expected)

    def test_pages_uses_correct_template(self):
        """Проверка: view-функциях используются правильные html-шаблоны"""
        templates_pages_names = {
            const.URL_INDEX_REV: const.TEMPLATE_INDEX,
            const.URL_POST_CREATE_REV: const.TEMPLATE_POST_CREATE,
            self.GROUP_LIST: const.TEMPLATE_GROUP_LIST,
            const.URL_PROFILE_REV: const.TEMPLATE_PROFILE_REV,
            self.POST_DETAIL: const.TEMPLATE_POST_DETAIL,
            self.POST_EDIT: const.TEMPLATE_POST_EDIT,
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_profile_page_shows_correct_context(self):
        """Проверка: Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(const.URL_PROFILE_REV)
        post = response.context['page_obj'][0]
        self.assertEqual(post, self.post)
        self.check_contex(post)

    def test_index_page_show_correct_context(self):
        """Проверка: Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(const.URL_INDEX_REV)
        post = response.context['page_obj'][0]
        self.assertIn('page_obj', response.context)
        self.check_contex(post)

    def test_group_list_page_show_correct_context(self):
        """Проверка: Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.GROUP_LIST)
        group = response.context['page_obj'][0]
        self.assertIn('page_obj', response.context)
        self.check_contex(group)

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
        cls.user = User.objects.create_user(username=const.STR_USERNAME)
        cls.author = User.objects.get(username=const.STR_USERNAME)
        cls.group = Group.objects.create(
            title=const.STR_GROUP1_TITLE,
            slug=const.STR_GROUP1_SLUG,
            description=const.STR_GROUP1_DESCRIPTION,
        )
        cls.GROUP_LIST = reverse(
            const.URL_GROUP_LIST,
            kwargs={'slug': cls.group.slug}
        )
        cls.posts = [
            Post(
                text=f'{const.STR_TEXT} {number_post}',
                author=cls.user,
                group=cls.group,
            )
            for number_post in range(const.NUM_TOTAL_POSTS)
        ]
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.authorized = Client()

    def test_page_paginator_obj(self):
        """Проверка: пагинатор на 1, 2 странице index, group_list, profile"""
        templates = [
            (const.URL_INDEX_HOME),
            (self.GROUP_LIST),
            (const.URL_PROFILE_REV)
        ]
        count_and_page = [
            (const.NUM_ONE_PAGE, const.NUM_COUNT_POST_TEN),
            (const.NUM_TWO_PAGE, const.NUM_COUNT_POST_THREE)
        ]
        for reverse_name in templates:
            for page, count_posts in count_and_page:
                with self.subTest(reverse_name=reverse_name):
                    response = self.authorized.get(
                        reverse_name, {'page': page}
                    )
                    posts = len(response.context['page_obj'])
                    self.assertEqual(posts, count_posts)
