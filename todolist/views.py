from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required

from .models import Post


def home(request):
    """
    Отображение всех заметок на главной странице
    :param request: Обязательный, всегда, первый, запрос от пользователя.
    :return:
    """

    posts = Post.objects.all()  # QuerySet все заметки
    return render(request, "todolist/home.html", {"posts": posts})


@login_required
def create_post(request):
    """
    Создание новых заметок
    """

    errors = []

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("text")

        if not title or not content and len(title) <= 300 and len(content) <= 30_000:
            errors.append("Укажите заголовок и содержимое заметки")

        else:

            post = Post(title=title, content=content, user=request.user)
            post.save()

            return redirect(reverse("post_show", kwargs={"post_id": post.id}))

    return render(request, "todolist/create_post.html", {"errors": errors})


def show_post(request, post_id: int):
    return render(request, "todolist/show_post.html", {"post": get_object_or_404(Post, id=post_id)})


@login_required
def edit_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    errors = []

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("text")

        post.title = title
        post.content = content

        if not title or not content:
            errors.append("Укажите заголовок и содержимое заметки")

        else:
            post.save()

            return redirect(reverse("post_show", kwargs={"post_id": post_id}))

    return render(request, "todolist/edit_post.html", {"errors": errors, "post": post})


@login_required
def delete_post(request, post_id: int):
    if request.method != "POST":
        return HttpResponseNotAllowed(permitted_methods=["POST"])

    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect(reverse("home"))
