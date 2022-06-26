from django.core.paginator import Page, Paginator
from django.db.models import QuerySet


def get_page_object(
    posts: QuerySet,
    page_number: int,
    per_page: int = 10
) -> Page:
    '''Получаем объект страницы.'''

    paginator = Paginator(posts, per_page)
    return paginator.get_page(page_number)
