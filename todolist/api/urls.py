from django.urls import path

from . import views


# /api/posts/

urlpatterns = [
    path("", views.PostsListAPIView.as_view()),
    path("<int:post_id>", views.OnePostAPIView.as_view()),
]
