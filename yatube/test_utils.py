from dataclasses import Field
from typing import Dict

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import QuerySet
from django.forms import Field
from django.http import HttpResponse
from django.test import TestCase

from posts.models import Post


def assert_is_instanse_fields(
    self: TestCase,
    response: HttpResponse,
    form_fields: Dict[str, Field]
):
    '''Проверяем, что поля в форме соответствуют типам.'''
    for value, expected in form_fields.items():
        with self.subTest(value=value):
            form_field = response.context.get('form').fields.get(value)
            # Проверяет, что поле формы является экземпляром
            # указанного класса
            self.assertIsInstance(form_field, expected)


def pages_uses_correct_template(
    test_case: TestCase,
    templates_pages_names: Dict[str, str]
) -> None:
    """URL-адрес использует соответствующий шаблон."""

    for template, reverse_name in templates_pages_names.items():
        with test_case.subTest(reverse_name=reverse_name):
            response = test_case.guest_client.get(reverse_name)
            test_case.assertTemplateUsed(response, template)


def assert_in(cls, key: str, obj):
    '''Проверяем наличие значения по ключу'''
    cls.assertIn(
        key,
        obj,
        'Не найдено значение по ключу {}'.format(key)
    )


def get_test_image() -> SimpleUploadedFile:
    '''Отдаем тестовую картинку.'''

    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x02\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        b'\x0A\x00\x3B')

    return SimpleUploadedFile(
        name='small.gif',
        content=small_gif,
        content_type='image/gif'
    )


def search_post_by_text(page_obj: QuerySet, text: str) -> Post:
    '''Ищем пост в ответе по тексту.'''

    return next(
        (
            p for p in page_obj
            if p.text == text
        ),
        None
    )
