from unittest import TestCase

from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='User_test')
        cls.post = Post.objects.create(
            text='text_test',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Title',
            slug='slug_test',
            description='descr_test'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_form(self):
        """Проверка: Создаётся ли новая запись в базе данных, создавая пост"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'text',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={
                'username': self.user
            }
        ))
        self.assertEqual(Post.objects.count(), (post_count) + 1)
        self.assertTrue(Post.objects.filter(
            author=self.user,
            text=form_data['text'],
            id=2).exists()
        )

    def test_edit_post_form(self):
        """Проверка: происходит ли изменение поста с post_id в базе данных"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'text_test',
            'group': self.group.id
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(self.post.text, form_data['text'])
