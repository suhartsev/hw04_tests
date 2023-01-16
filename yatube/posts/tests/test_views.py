from django import forms
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='User_test')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title="Title",
            slug="slug_test",
            description="descr_test"
        )
        cls.group2 = Group.objects.create(
            title="Title2",
            slug="slug_test2",
            description="descr_test2",
        )
        cls.post = Post.objects.create(
            text='text_test',
            author=cls.user,
            group=cls.group,
            pk='1'
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
        self.assertEqual(post, 'text_test')

    def test_group_list_page_show_correct_context(self):
        """Проверка: Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'slug_test'})))
        group = response.context['page_obj'][0].group.title
        self.assertEqual(group, 'Title')

    def test_post_detail_list_page_show_correct_context(self):
        """Проверка: Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': '1'})))
        post_detail = response.context['post'].text
        self.assertEqual(post_detail, 'text_test')

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
        post = PostsViewsTests.post
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group2.slug})
        )
        self.assertNotIn(post, response.context.get('page_obj'))
        group2 = response.context.get('group')
        self.assertNotEqual(group2, self.group)


class PaginatorTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='User_test')
        cls.group = Group.objects.create(
            title='Title',
            slug='slug_test',
            description='descr_test'
        )
        for i in range(13):
            cls.post = Post.objects.create(
                text=f'post {i}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_first_page_contains_ten_records_index(self):
        """Проверка: Пагинатора для Первой странцы index - 10 постов"""
        response = self.auth_client.get(reverse('posts:index'))
        self.assertEqual(len(
            response.context['page_obj']),
            settings.LIMIT_POSTS_TEN
        )

    def test_second_page_contains_three_records_index(self):
        """Проверка: Пагинатора для Второй странцы index - 3 поста"""
        response = self.auth_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']),
            settings.LIMIT_POSTS_THREE
        )

    def test_first_page_contains_ten_records_group_list(self):
        """Проверка: Пагинатора для Первой странцы group_list - 10 постов"""
        response = self.auth_client.get(reverse('posts:group_list',
                                                kwargs={'slug': 'slug_test'}))
        self.assertEqual(len(
            response.context['page_obj']),
            settings.LIMIT_POSTS_TEN
        )

    def test_second_page_contains_three_records_group_list(self):
        """Проверка: Пагинатора для Второй странцы group_list - 3 поста"""
        response = self.auth_client.get(reverse(
                                        'posts:group_list',
                                        kwargs={'slug': 'slug_test'})
                                        + '?page=2'
                                        )
        self.assertEqual(len(
            response.context['page_obj']),
            settings.LIMIT_POSTS_THREE
        )

    def test_second_page_contains_ten_records_profile(self):
        """Проверка: Пагинатора для Первой странцы profile - 10 постов"""
        response = self.auth_client.get(reverse('posts:profile',
                                                kwargs={'username': self.user}
                                                ))
        self.assertEqual(len(
            response.context['page_obj']),
            settings.LIMIT_POSTS_TEN
        )

    def test_second_page_contains_three_records_profile(self):
        """Проверка: Пагинатора для Второй странцы profile - 3 поста"""
        response = self.auth_client.get(reverse(
                                        'posts:profile',
                                        kwargs={'username': self.user}
                                        ) + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']),
            settings.LIMIT_POSTS_THREE
        )
