from unittest import TestCase

from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

USERNAME = 'User_test'
TEXT = 'text_test'
GROUP_SLUG = 'slug_test'
GROUP_TITLE = "Title"
GROUP_DESCRIPTION = "descr_test"
GROUP2_TITLE = "Title2"
GROUP2_SLUG = "slug_test2"
GROUP2_DESCRIPTION = "descr_test2"
PROFILE = reverse('posts:profile',
                  kwargs={'username': USERNAME})


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.post = Post.objects.create(
            text=TEXT,
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.group2 = Group.objects.create(
            title=GROUP2_TITLE,
            slug=GROUP2_SLUG,
            description=GROUP2_DESCRIPTION,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_form(self):
        """Проверка: Создаётся ли новая запись в базе данных, создавая пост"""
        post_count = Post.objects.count()
        form_data = {
            'text': TEXT,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(
            response, PROFILE
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.user)

    def test_edit_post_form(self):
        """Проверка: происходит ли изменение поста с post_id в базе данных"""
        post_count = Post.objects.count()
        form_data = {
            'text': TEXT,
            'group': self.group2.id
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(self.post.text, form_data['text'])
