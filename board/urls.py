"""
URL configuration for board project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from todolist.views import PostsList
from user.views import Register

# /

urlpatterns = [
    path("", PostsList.as_view()),
    path("admin/", admin.site.urls),
    path("api/posts/", include("todolist.api.urls")),
    path("posts/", include("todolist.urls", namespace="posts")),
    path("user/", include("user.urls", namespace="user")),
    path("accounts/register", Register.as_view(), name="register"),
    path(
        "accounts/",
        include(
            ("django.contrib.auth.urls", "django.contrib.auth"), namespace="accounts"
        ),
    ),
    path("captcha/", include("captcha.urls")),
    path("api/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/", include("djoser.urls.authtoken")),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
