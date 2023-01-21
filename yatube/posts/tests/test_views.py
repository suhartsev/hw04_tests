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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_contex(self, context_page):
        """Метод проверки контекста текста поста"""
        context_page = {
            context_page.text: const.TEXT,
        }
        for context, expected in context_page.items():
            self.assertEqual(context, expected)

    def test_pages_uses_correct_template(self):
        """Проверка: view-функциях используются правильные html-шаблоны"""
        templates_pages_names = {
            reverse(const.INDEX): 'posts/index.html',
            reverse(const.POST_CREATE_FORMS): 'posts/create_post.html',
            reverse(
                const.GROUP_LIST,
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                const.PROFILE,
                kwargs={'username': self.post.author}): 'posts/profile.html',
            reverse(
                const.POST_DETAIL,
                kwargs={'post_id': self.post.pk}): 'posts/post_detail.html',
            reverse(
                const.POST_EDIT,
                kwargs={'post_id': self.post.pk}): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_profile_page_shows_correct_context(self):
        """Проверка: Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(const.PROFILE, kwargs={'username': const.USERNAME})
        )
        post = response.context['page_obj'][0]
        self.check_contex(post)
        self.assertEqual(post, self.post)
        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], self.user)
        self.assertIn('page_obj', response.context)

    def test_index_page_show_correct_context(self):
        """Проверка: Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(const.INDEX))
        post = response.context['page_obj'][0]
        self.check_contex(post)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertIn('page_obj', response.context)

    def test_group_list_page_show_correct_context(self):
        """Проверка: Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse(const.GROUP_LIST,
                    kwargs={'slug': const.GROUP1_SLUG})))
        group = response.context['page_obj'][0].group
        self.assertEqual(group.title, const.GROUP1_TITLE)
        self.assertEqual(group.description, const.GROUP1_DESCRIPTION)
        self.assertEqual(group.slug, const.GROUP1_SLUG)
        self.assertIn('page_obj', response.context)

    def test_post_detail_list_page_show_correct_context(self):
        """Проверка: Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse(const.POST_DETAIL,
                    kwargs={'post_id': self.post.id})))
        post_detail = response.context['post']
        self.check_contex(post_detail)

    def test_post_not_in_other_group(self):
        """Проверка: Созданный пост не появился в другой группе"""
        post = self.post
        response = self.authorized_client.get(
            reverse(
                const.GROUP_LIST,
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
        cls.user = User.objects.create_user(username=const.USERNAME)
        cls.author = User.objects.get(username=const.USERNAME)
        cls.group = Group.objects.create(
            title=const.GROUP1_TITLE,
            slug=const.GROUP1_SLUG,
            description=const.GROUP1_DESCRIPTION,
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
        self.authorized_author = Client()

    def test_page_paginator_obj(self):
        """Проверка: пагинатор на 1, 2 странице index, group_list, profile"""
        slug = self.group.slug
        username = self.user.username
        num_page = {'page': const.TWO_PAGE}
        templates = (
            const.INDEX_HOME,
            (f'/group/{slug}/'),
            (f'/profile/{username}/'),
        )
        for address in templates:
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                response_second = self.authorized_author.get(address, num_page)
                count_posts = len(response.context['page_obj'])
                self.assertEqual(count_posts, const.LIMIT_POSTS_TEN)
                count_posts_second = len(response_second.context['page_obj'])
                self.assertEqual(count_posts_second, const.LIMIT_POSTS_THREE)

# Я знаю, что тут нельзя писать. Но Вы не отвечаете в пачке с черверга
#  19 января. Обратной связи нет
# Я написал десяток сообщений, покажите как надо это сделать,
# Это уже третий вид работающего теста, так как Вы просили
# Без + '?page=2'. Я не зная как сделать, то что вы просите,
#  покажите пожалуста.
# Это тоже я не понимаю как правильно сделать,
# (self.assertEqual(post.text, const.TEXT)) Сделал метод, вроде работает
# теперь в тестах вызываю self.check_contex(post) к примеру
# я спросил у многих ребят и про это и про пагинатор ни кто не знает.
# А Вы не отвечаете.
# Выручвйте если не так.
# Это уже 4й вариант.
