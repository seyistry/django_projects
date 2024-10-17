from django.contrib.auth import get_user_model
from .serializers import PostSerializers, UserSerializer
from rest_framework import generics, viewsets
from .models import Post
from .permissions import IsAuthorOrReadOnly


class PostList(generics.ListCreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostSerializers


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthorOrReadOnly]
    queryset = Post.objects.all()
    serializer_class = PostSerializers

class UserList(generics.ListCreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthorOrReadOnly]
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class PostViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostSerializers

class UserViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer