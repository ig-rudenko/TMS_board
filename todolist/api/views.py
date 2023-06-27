from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters import rest_framework as rest_filters

from .filters import APIPostFilter
from .permisiion import IsOwnerOrCanUpdateDeletePost
from .serializers import PostListSerializer, OnePostSerializer
from ..models import Post


class PostsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PostListSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [rest_filters.DjangoFilterBackend]
    filterset_class = APIPostFilter

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OnePostAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    lookup_url_kwarg = "post_id"
    lookup_field = "pk"
    serializer_class = OnePostSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOwnerOrCanUpdateDeletePost,
    ]
