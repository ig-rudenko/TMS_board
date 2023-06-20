import textwrap

from django.contrib import admin
from django import forms
from django.db.models import Count
from django.utils.html import format_html
from django.shortcuts import reverse
from django.contrib.sessions.models import Session

from .models import Post, Tag


@admin.register(Post)  # Модель
class PostAdmin(admin.ModelAdmin):  # Класс админки
    list_display = [
        "short_title",
        "created",
        "user",
        "has_comments",
        "tags_list",
        "link_to",
    ]
    search_fields = ["title", "content"]
    list_filter = ["user", "tags"]
    filter_horizontal = ["tags"]
    list_per_page = 20
    date_hierarchy = "created"
    ordering = ['-comments__count']

    actions = ["add_tag_python"]

    def get_queryset(self, request):
        return (
            Post.objects.all()
            .select_related("user")
            .annotate(Count("comments"))
            .order_by("-comments__count")
        )

    @admin.action(description="Добавить тег `python`")
    def add_tag_python(self, form, queryset):
        tag, created = Tag.objects.get_or_create(name="python")
        for obj in queryset:
            obj.tags.add(tag)

    @admin.display(description="Заголовок")
    def short_title(self, obj: Post) -> str:
        return textwrap.wrap(obj.title, 45)[0] + " ..."

    @admin.display(description="Есть комментарии", boolean=True)
    def has_comments(self, obj: Post):
        return obj.comments__count > 0

    @admin.display(description="Теги")
    def tags_list(self, obj: Post) -> str:
        tags_qs = obj.tags.all()

        res_list = [
            f'<li style="color: {tag.color}">{tag.name}</li>' for tag in tags_qs
        ]
        return format_html("".join(res_list))

    @admin.display(description="Посмотреть")
    def link_to(self, obj: Post):
        link = reverse("posts:show", kwargs={"post_id": obj.id})
        return format_html(f'<a href="{link}">***</a>')


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"
        widgets = {"color": forms.TextInput(attrs={"type": "color"})}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    form = TagForm
    list_display = ["name", "tag_color"]

    @admin.display(description="")
    def tag_color(self, obj: Tag):
        return format_html(
            f"""
        <svg xmlns="http://www.w3.org/2000/svg" style="height: 25px; width: 25px;" version="1.1">
           <circle cx="10" cy="10" r="10" stroke="black" stroke-width="2" fill="{obj.color}" />
        </svg>"""
        )


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ["session_key", "_session_data", "expire_date"]

    def _session_data(self, obj: Session):
        return obj.get_decoded()

