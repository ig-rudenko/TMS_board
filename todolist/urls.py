from django.urls import path

from . import views

app_name = "todolist"

# /posts/
urlpatterns = [
    # ДЛЯ CBV нужно вызвать `.as_view()`
    path("", views.PostsList.as_view(), name="home"),
    path("create/", views.CreatePost.as_view(), name="create"),
    path("<int:post_id>/", views.ShowPost.as_view(), name="show"),
    path("<int:post_id>/edit/", views.EditPost.as_view(), name="edit"),
    path("<int:post_id>/delete/", views.DeletePost.as_view(), name="delete"),
    path("<int:post_id>/comment/add/", views.CommentAdd.as_view(), name="comment_add"),
]
