from django.shortcuts import redirect, get_object_or_404, reverse
from django.views import generic
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count
from django.db.models import QuerySet

from .forms import PostForm
from .models import Post, Comment
from .filters import PostFilter
from .paginator import CachedPaginator
from .tg_notifier import tg_notify


class PostsList(generic.ListView):
    template_name = "todolist/home.html"
    context_object_name = "posts"
    page_kwarg = "p"
    cache_timeout = 50
    paginate_by = 30
    paginator_class = CachedPaginator

    def paginate_queryset(self, queryset, page_size):
        key_prefix = settings.CACHES["default"]["KEY_PREFIX"]

        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
            cache_name=f"{key_prefix}.CachedPaginator.posts_count",
            cache_timeout=self.cache_timeout,
        )
        page_number = (
            self.kwargs.get(self.page_kwarg)
            or self.request.GET.get(self.page_kwarg)
            or 1
        )

        page = paginator.page(page_number)
        page_object_list = self.get_cached_page_object_list(page)

        return paginator, page, page_object_list, page.has_other_pages()

    def get_cached_page_object_list(self, page):
        # Названия ключа для кэша
        cache_key = f'{settings.CACHES["default"]["KEY_PREFIX"]}.PostsList.{self.request.get_full_path()}'

        page_object_list = cache.get(cache_key)
        if page_object_list is None:
            page_object_list = list(page.object_list)  # Обращение к БД
            cache.set(cache_key, page_object_list, timeout=self.cache_timeout)

        return page_object_list

    def get_queryset(self) -> QuerySet[dict]:
        """
        Формирует `QuerySet` всех заметок и возвращает поля `id`, `title`, `created`,
        имя пользователя, создавшего заметку и кол-во комментариев к ней.

        :return Возвращает `QuerySet` словарей.
        """
        return PostFilter(
            self.request.GET,
            queryset=Post.objects.all()
            .select_related("user")
            .annotate(Count("comments"))
            .values("id", "title", "created", "user__username", "comments__count")
            .order_by("-comments__count"),
        ).qs


class ShowPost(generic.DetailView):
    queryset = Post.objects.prefetch_related("tags")  # Откуда вытянуть
    pk_url_kwarg = "post_id"  # Где брать ID объекта в URL?  Из `urls.py`!
    template_name = "todolist/show_post.html"  # Шаблон, куда вернуть
    context_object_name = "post"  # Под каким именем вернуть в шаблон

    def get(self, request, *args, **kwargs):
        self.object: Post = self.get_object()

        tg_notify.send_message(
            message=f"Вашу заметку ({self.object.title}) сейчас смотрят!",
            to_user_tg_id=self.object.user.tg_id,
        )

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


@method_decorator(login_required, name="dispatch")
class DeletePost(generic.DeleteView):
    queryset = Post.objects
    model = Post
    pk_url_kwarg = "post_id"  # Где брать ID объекта в URL?  Из `urls.py`!
    success_url = reverse_lazy("posts:home")

    def form_valid(self, form):
        if self.object.user != self.request.user:
            return HttpResponseForbidden()
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class CreatePost(generic.CreateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = "post_id"
    template_name = "todolist/edit_post.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class EditPost(generic.UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = "post_id"
    template_name = "todolist/edit_post.html"


class CommentAdd(generic.View):
    def post(self, request, post_id: int):
        post = get_object_or_404(Post, id=post_id)

        user = request.POST.get("user", "")
        email = request.POST.get("email", "")
        content = request.POST.get("content", "")

        Comment.objects.create(username=user, email=email, content=content, post=post)
        return redirect(reverse("posts:show", kwargs={"post_id": post.id}))
