from django_filters import rest_framework as rest_filters
from django.db.models import QuerySet, Q

from todolist.models import Post


class APIPostFilter(rest_filters.FilterSet):
    search = rest_filters.CharFilter(method="search_filter", label="Поиск")

    class Meta:
        model = Post
        fields = ["title"]

    @staticmethod
    def search_filter(queryset: QuerySet, name, value):
        """
        :param queryset: queryset модели.
        :param name: Название поля поиска.
        :param value: Значение от пользователя.
        """
        if value:
            return queryset.filter(
                Q(title__icontains=value) | Q(content__icontains=value)
            )
        return queryset
