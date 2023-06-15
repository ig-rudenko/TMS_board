from django.shortcuts import redirect, get_object_or_404, reverse
from django.views import generic
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count

from .forms import PostForm
from .models import Post, Comment
from .filters import PostFilter


class PostsList(generic.ListView):
    template_name = "todolist/home.html"
    context_object_name = "posts"
    paginate_by = 30
    page_kwarg = "p"

    def get_queryset(self):
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
