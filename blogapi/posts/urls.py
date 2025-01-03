from django.urls import path
from .views import PostList, PostDetail, UserDetail, UserList, UserViewSet, PostViewSet
from rest_framework import routers

# urlpatterns = [
#     path('<int:pk>/', PostDetail.as_view()),
#     path('', PostList.as_view()),
#     path('users/<int:pk>/', UserDetail.as_view()),
#     path('users/', UserList.as_view()),
# ]

router = routers.SimpleRouter()
router.register('users', UserViewSet, basename='users')
router.register('posts', PostViewSet, basename='posts')

urlpatterns = router.urls
