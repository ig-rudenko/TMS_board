from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views import generic
from django.urls import reverse_lazy
from django.http import Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count
from django.db import transaction

from .models import Post, Comment, Tag


class PostsList(generic.ListView):
    template_name = "todolist/home.html"
    context_object_name = "posts"
    paginate_by = 30

    def get_queryset(self):
        """
        Формирует `QuerySet` всех заметок и возвращает поля `id`, `title`, `created`,
        имя пользователя, создавшего заметку и кол-во комментариев к ней.

        :return Возвращает `QuerySet` словарей.
        """
        return (
            Post.objects.all()
            .select_related("user")
            .annotate(Count("comments"))
            .values("id", "title", "created", "user__username", "comments__count")
            .order_by("-comments__count")
        )


class NonNumbersPostsList(generic.ListView):
    template_name = "todolist/home.html"
    context_object_name = "posts"

    def validate(self) -> bool:
        s = self.request.GET.get(
            "search"
        )  # Пытаемся найти ключ `search`, если его нет, то вернется `None`
        return s is not None and len(s) <= 50

    def get_queryset(self):
        if not self.validate():
            return Post.objects.all()
        search = self.request.GET["search"]
        return Post.objects.filter(title__icontains=search)


class ShowPost(generic.DetailView):
    queryset = Post.objects.prefetch_related("tags")  # Откуда вытянуть
    pk_url_kwarg = "post_id"  # Где брать ID объекта в URL?  Из `urls.py`!
    template_name = "todolist/show_post.html"  # Шаблон, куда вернуть
    context_object_name = "post"  # Под каким именем вернуть в шаблон


@method_decorator(login_required, name="dispatch")
class DeletePost(generic.View):
    queryset = Post.objects
    model = Post
    pk_url_kwarg = "post_pk"  # Где брать ID объекта в URL?  Из `urls.py`!
    success_url = reverse_lazy("posts:home")

    def get_object_pk(self):
        # Мы берем из URL <int:post_id>/delete/
        # Вытягиваем значение `post_id`
        return self.kwargs[self.pk_url_kwarg]

    def get_queryset(self):
        return self.queryset

    def has_object_permission(self, post: Post) -> bool:
        """
        Проверяет, имеет ли данная заметка текущего пользователя как создателя.
        """
        return post.user.id == self.request.user.id

    def get_success_url(self):
        return self.success_url

    def post(self, request):
        qs = self.get_queryset()
        pk = self.get_object_pk()

        try:
            post = qs.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404()

        if self.has_object_permission(post):
            post.delete()
            return redirect(self.get_success_url())

        else:
            return HttpResponseForbidden()


class ValidationError(Exception):
    pass


class PostValidate:
    def __init__(self, title: str, content: str, tags: list[str | Tag]):
        self.title = {"value": title, "errors": [], "is_valid": True}
        self.content = {"value": content, "errors": [], "is_valid": True}
        self.tags = {"value": tags, "errors": [], "is_valid": True}

    def is_valid(self, raise_error=False) -> bool:
        if not self._validate_title():
            self.title["is_valid"] = False
        if not self._validate_content():
            self.content["is_valid"] = False
        if not self._validate_tags():
            self.tags["is_valid"] = False

        valid = (
            self.title["is_valid"]
            and self.content["is_valid"]
            and self.tags["is_valid"]
        )

        if raise_error and not valid:
            raise ValidationError("Данные пользователя неверны")

        return valid

    def _validate_tags(self):
        """Создаем теги, если их не было"""
        valid_tags_list = []
        for tag_name in self.tags["value"]:
            tag, created = Tag.objects.get_or_create(name=tag_name.lower())
            valid_tags_list.append(tag)
        self.tags["value"] = valid_tags_list
        return True

    def _validate_title(self) -> bool:
        self.title["value"] = self.title["value"].strip()

        if not self.title["value"]:
            self.title["errors"].append("Укажите заголовок")
            return False
        if len(self.title["value"]) > 50:
            self.title["errors"].append("Заголовок должен быть не более 10 символов")
            return False
        return True

    def _validate_content(self) -> bool:
        self.content["value"] = self.content["value"].strip()

        if not self.content["value"]:
            self.content["errors"].append("Укажите содержимое")
            return False
        if len(self.content["value"]) > 30_000:
            self.content["errors"].append(
                "Содержимое должно быть не более 30 000 символов"
            )
            return False
        return True


@method_decorator(login_required, name="dispatch")
class CreatePost(generic.View):
    model = Post
    validator = PostValidate

    def get(self, request):
        print(f'{Tag.objects.all().values("name")=}')
        print(f'{Tag.objects.all().values_list("name")=}')

        tags_list = Tag.objects.all().values_list("name", flat=True)
        print(f"{tags_list=}")
        return render(
            request, "todolist/create_edit_post.html", {"tags_list": tags_list}
        )

    def notification(self):
        pass

    def logging(self):
        pass

    def post(self, request):
        validator = self.validator(
            title=request.POST.get("title", ""),
            content=request.POST.get("content", ""),
            tags=request.POST.getlist("tags", []),
        )

        try:
            with transaction.atomic():
                validator.is_valid(raise_error=True)

                tags_obj_list: list[Tag] = validator.tags["value"]

                print(tags_obj_list)

                post = self.model.objects.create(
                    title=validator.title["value"],
                    content=validator.content["value"],
                    user=request.user,
                )
                post.tags.add(*tags_obj_list)
                post.save()

        except ValidationError:
            return render(
                request, "todolist/create_edit_post.html", {"validator": validator}
            )

        self.logging()
        self.notification()
        return redirect(reverse("posts:show", kwargs={"post_id": post.id}))


@method_decorator(login_required, name="dispatch")
class EditPost(generic.View):
    model = Post
    validator = PostValidate

    def has_object_permission(self, post: Post) -> bool:
        """
        Проверяет, имеет ли данная заметка текущего пользователя как создателя.
        """
        return post.user.id == self.request.user.id

    def get(self, request, post_id: int):
        post = get_object_or_404(self.model, id=post_id)

        if not self.has_object_permission(post):
            return HttpResponseForbidden()

        validator = self.validator(post.title, post.content)
        return render(
            request, "todolist/create_edit_post.html", {"validator": validator}
        )

    def post(self, request, post_id: int):
        post = get_object_or_404(self.model, id=post_id)

        if not self.has_object_permission(post):
            return HttpResponseForbidden()

        validator = self.validator(
            title=request.POST.get("title", ""), content=request.POST.get("content", "")
        )

        post.title = validator.title["value"]
        post.content = validator.content["value"]

        if not validator.is_valid():
            return render(
                request,
                "todolist/create_edit_post.html",
                {"validator": validator, "post": post},
            )

        post.save()
        return redirect(reverse("posts:show", kwargs={"post_id": post.id}))


class CommentAdd(generic.View):
    def post(self, request, post_id: int):
        post = get_object_or_404(Post, id=post_id)

        user = request.POST.get("user", "")
        email = request.POST.get("email", "")
        content = request.POST.get("content", "")

        Comment.objects.create(username=user, email=email, content=content, post=post)
        return redirect(reverse("posts:show", kwargs={"post_id": post.id}))
