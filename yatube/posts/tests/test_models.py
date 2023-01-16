from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверка: что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_object = post.text[:15]
        self.assertEqual(expected_object, str(post))

    def test_model_group_have_correct_names_title(self):
        """Проверка: что у модели Group корректно название группы."""
        group = PostModelTest.group
        expected_object = group.title
        self.assertEqual(expected_object, str(group))
