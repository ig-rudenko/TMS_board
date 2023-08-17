from django.shortcuts import reverse
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField()
    tags = models.ManyToManyField("todolist.Tag", related_name="posts")

    def get_absolute_url(self):
        return reverse("posts:show", kwargs={"post_id": self.id})

    class Meta:
        ordering = ["-created"]
        indexes = [models.Index(fields=["created"])]

    @property
    def comments_count(self) -> int:
        return self.comments.all().count()

    def __repr__(self):
        return f"Post: <{self.title}>"

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=256)
    color = models.CharField(max_length=8, default="000000FF")

    def __repr__(self):
        return f"Tag: <{self.name}>"

    def __str__(self):
        return self.name


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    username = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return self.content[:30]

    def __repr__(self):
        return f"Comment: <{self.username}> <{len(self.content)}>"
