from django.urls import path

from . import views
from . import cb_views

app_name = "todolist"

# /posts/
urlpatterns = [
    # ДЛЯ CBV нужно вызвать `.as_view()`
    path("", cb_views.PostsList.as_view(), name="home"),
    path("nn/", cb_views.NonNumbersPostsList.as_view()),
    path("create/", cb_views.CreatePost.as_view(), name="create"),
    path("<int:post_id>/", cb_views.ShowPost.as_view(), name="show"),
    path("<int:post_id>/edit/", cb_views.EditPost.as_view(), name="edit"),
    path("<int:post_id>/delete/", views.delete_post, name="delete"),
    path("<int:post_id>/comment/add/", cb_views.CommentAdd.as_view(), name="comment_add")
]
