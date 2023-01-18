from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()

USERNAME = 'User_test'
TEXT = 'text_test'
GROUP_SLUG = 'slug_test'
GROUP_TITLE = "Title"
GROUP_DESCRIPTION = "descr_test"


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEXT,
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

    # def test_models_have_correct_object_names1(self):
    #     """Проверка: что у моделей корректно работает __str__., title"""
    #     expected_object1 = self.post.text[:15]
    #     expected_object2 = self.group.title
    #     self.assertEqual(expected_object1, str(self.post))
    #     self.assertEqual(expected_object2, str(self.group))
