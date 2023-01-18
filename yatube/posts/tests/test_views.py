from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

TOTAL_POSTS = 13
LIMIT_POSTS_THREE = 3
LIMIT_POSTS_TEN = 10
USERNAME = 'User_test'
TEXT = 'text_test'
GROUP1_SLUG = 'slug_test'
GROUP1_TITLE = "Title"
GROUP1_DESCRIPTION = "descr_test"
GROUP2_TITLE = "Title2"
GROUP2_SLUG = "slug_test2"
GROUP2_DESCRIPTION = "descr_test2"


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title=GROUP1_TITLE,
            slug=GROUP1_SLUG,
            description=GROUP1_DESCRIPTION
        )
        cls.group2 = Group.objects.create(
            title=GROUP2_TITLE,
            slug=GROUP2_SLUG,
            description=GROUP2_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=TEXT,
            author=cls.user,
            group=cls.group
        )

    def test_pages_uses_correct_template(self):
        """Проверка: URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_profile_page_shows_correct_context(self):
        """Проверка: Шаблон profile сформирован с правильным контекстом."""
        profile_url = reverse('posts:profile', kwargs={'username': self.user})
        response = self.authorized_client.get(profile_url)
        current_context = response.context['author']
        expected_context = PostsViewsTests.user
        self.assertEqual(current_context, expected_context)

    def test_index_page_show_correct_context(self):
        """Проверка: Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0].text
        self.assertEqual(post, TEXT)

    def test_group_list_page_show_correct_context(self):
        """Проверка: Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': GROUP1_SLUG})))
        group = response.context['page_obj'][0].group.title
        self.assertEqual(group, GROUP1_TITLE)

    def test_post_detail_list_page_show_correct_context(self):
        """Проверка: Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': '1'})))
        post_detail = response.context['post'].text
        self.assertEqual(post_detail, TEXT)

    def test_post_create_page_show_correct_context(self):
        """Проверка: Форма создания поста - post_create."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_show_correct_context(self):
        """Проверка: форма редактирования поста, отфильтрованного по id."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_on_index_group_profile_create(self):
        """Проверка: Созданный пост появился на Главной, Группе, Профайле."""
        reverse_page_names_post = {
            reverse('posts:index'): self.group.slug,
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug}): self.group.slug,
            reverse('posts:profile', kwargs={
                'username': self.user}): self.group.slug
        }
        for value, expected in reverse_page_names_post.items():
            response = self.authorized_client.get(value)
            for object in response.context['page_obj']:
                post_group = object.group.slug
                with self.subTest(value=value):
                    self.assertEqual(post_group, expected)

    def test_post_not_in_other_group(self):
        """Проверка: Созданный пост не появился в другой группе"""
        post = self.post
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group2.slug}
            )
        )
        self.assertNotIn(post, response.context.get('page_obj'))
        group2 = response.context.get('group')
        self.assertNotEqual(group2, self.group)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.author = User.objects.get(username=USERNAME)
        cls.group = Group.objects.create(
            title=GROUP1_TITLE,
            slug=GROUP1_SLUG,
            description=GROUP1_DESCRIPTION,
        )
        cls.posts = [
            Post(
                text=f'{TEXT} {number_post}',
                author=cls.user,
                group=cls.group,
            )
            for number_post in range(TOTAL_POSTS)
        ]
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.authorized_author = Client()

    def test_page_contains_ten_records(self):
        """Проверка: пагинатор на 1, 2 странице index, group_list, profile"""
        pagin_urls = (
            ('posts:index', None),
            ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.user.username,))
        )
        pages_units = (
            ('?page=1', LIMIT_POSTS_TEN),
            ('?page=2', LIMIT_POSTS_THREE)
        )
        for address, args in pagin_urls:
            with self.subTest(address=address):
                for page, count_posts in pages_units:
                    with self.subTest(page=page):
                        response = self.authorized_author.get(
                            reverse(address, args=args) + page
                        )
        self.assertEqual(len(response.context['page_obj']), count_posts)

    # def test_page_one_contains_ten_records(self):
    #     """Проверка: пагинатор на 1 странице index, group_list, profile"""
    #     templates_names = [
    #         reverse('posts:index'),
    #         reverse(
    #             'posts:group_list',
    #             kwargs={'slug': self.group.slug}),
    #         reverse(
    #             'posts:profile',
    #             kwargs={'username': self.author}),
    #     ]
    #     for name in templates_names:
    #         with self.subTest(name=name):
    #             response = self.client.get(name)
    #             self.assertEqual(
    #                 len(response.context['page_obj']),
    #                 LIMIT_POSTS_TEN
    #             )

    # def test_page_two_contains_ten_records(self):
    #     """Проверка: пагинатор на 2 странице index, group_list, profile"""
    #     templates_names = [
    #         reverse('posts:index'),
    #         reverse(
    #             'posts:group_list',
    #             kwargs={'slug': self.group.slug}),
    #         reverse(
    #             'posts:profile',
    #             kwargs={'username': self.author}),
    #     ]
    #     for name in templates_names:
    #         with self.subTest(name=name):
    #             response = self.client.get(name + '?page=2')
    #             self.assertEqual(
    #                 len(response.context['page_obj']),
    #                 LIMIT_POSTS_THREE
    #             )
