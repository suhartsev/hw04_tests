from django.test import TestCase

from posts.models import Group, Post, User
from posts.tests import const


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=const.STR_USERNAME)
        cls.group = Group.objects.create(
            title=const.STR_GROUP1_TITLE,
            slug=const.STR_GROUP1_SLUG,
            description=const.STR_GROUP1_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=const.STR_TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверка: что у моделей корректно работает __str__, title"""
        fields_posts_group = {
            self.post.text[:15]: str(self.post),
            self.group.title: str(self.group)
        }
        for key, value in fields_posts_group.items():
            with self.subTest():
                self.assertEqual(key, value)
