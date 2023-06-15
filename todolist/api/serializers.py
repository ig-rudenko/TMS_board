from rest_framework import serializers
from django.contrib.auth import get_user_model

from todolist.models import Post, Tag, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["username", "email"]


class TagSerializer(serializers.ModelSerializer):
    color = serializers.CharField(max_length=8)

    class Meta:
        model = Tag
        fields = ["id", "name", "color"]
        read_only_fields = ["id"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["username", "email", "content", "created"]


class PostListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Post
        fields = ["id", "title", "content", "created", "user", "tags"]
        read_only_fields = ["id", "created", "user"]


class ManyPosts(serializers.ModelSerializer):
    posts = serializers.ListSerializer(child=PostListSerializer())


class OnePostSerializer(PostListSerializer):
    comments = serializers.ListSerializer(child=CommentSerializer(), read_only=True)

    class Meta:
        model = Post
        fields = ["id", "title", "content", "created", "user", "tags", "comments"]
        read_only_fields = ["id", "created", "user", "tags", "comments"]
