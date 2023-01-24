from django.urls import reverse

NUM_ONE_PAGE = 1
NUM_TWO_PAGE = 2
NUM_COUNT_POST_THREE = 3
NUM_COUNT_POST_TEN = 10
NUM_TOTAL_POSTS = 13

STR_USERNAME = 'User_test'
STR_OTHER_USER = 'other_user'
STR_TEXT = 'text_test'
STR_GROUP1_SLUG = 'slug_test'
STR_GROUP1_TITLE = "Title"
STR_GROUP1_DESCRIPTION = "descr_test"
STR_GROUP2_TITLE = "Title2"
STR_GROUP2_SLUG = "slug_test2"
STR_GROUP2_DESCRIPTION = "descr_test2"

TEMPLATE_INDEX = 'posts/index.html'
TEMPLATE_POST_CREATE = 'posts/create_post.html'
TEMPLATE_GROUP_LIST = 'posts/group_list.html'
TEMPLATE_PROFILE_REV = 'posts/profile.html'
TEMPLATE_POST_DETAIL = 'posts/post_detail.html'
TEMPLATE_POST_EDIT = 'posts/create_post.html'
URL_INDEX_HOME = '/'
URL_INDEX = 'posts:index'
URL_POST_CREATE = '/create/'
URL_PROFILE = 'posts:profile'
URL_POST_EDIT = 'posts:post_edit'
URL_UNEXISTRING = '/unexisting_page/'
URL_POST_DETAIL = 'posts:post_detail'
URL_GROUP_LIST = 'posts:group_list'
URL_INDEX_REV = reverse(URL_INDEX)
URL_PROFILE_REV = reverse(URL_PROFILE, kwargs={'username': STR_USERNAME})
URL_POST_CREATE_REV = reverse('posts:post_create')
