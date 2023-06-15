from rest_framework import generics

from .serializers import PostListSerializer, OnePostSerializer
from ..models import Post


class PostsListAPIView(generics.ListCreateAPIView):
    serializer_class = PostListSerializer
    queryset = Post.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OnePostAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    lookup_url_kwarg = "post_id"
    lookup_field = "pk"
    serializer_class = OnePostSerializer
