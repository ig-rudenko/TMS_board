from django.core.paginator import Paginator
from django.core.cache import cache


class CachedPaginator(Paginator):
    def __init__(
        self,
        object_list,
        per_page,
        orphans=0,
        allow_empty_first_page=True,
        cache_name=None,
        cache_timeout: int = 300,
    ):
        # pylint: disable=R0913
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
        self.cache_timeout = cache_timeout
        self.cache_name = cache_name
        self._count = None

    def validate_number(self, number):
        try:
            page_number = int(number)
        except ValueError:
            page_number = 1

        if page_number > self.num_pages:
            page_number = self.num_pages
        return page_number

    @property
    def count(self):  # pylint: disable=W0236
        if not self.cache_name:
            # Если имя кеша не было передано, то работаем, как с обычным пагинатором
            if not self._count:
                self._count = super().count
            return self._count

        # Работа с кешем
        count = cache.get(self.cache_name)  # Получаем из кеша запись
        if count is None:  # Если в кеше нет записи
            count = super().count
            cache.set(self.cache_name, count, self.cache_timeout)

        return count
