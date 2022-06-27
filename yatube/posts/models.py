from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    '''
    Класс представляет собой группу публикаций.
    Атрибуты:
    ----------
    title : str
        название группы;
    slug : str
        аббревиатура, используемая в url;
    description : str
        описание группы.
    '''

    title = models.CharField(
        verbose_name="Название",
        max_length=200,
    )
    slug = models.SlugField(
        verbose_name="Аббревиатура",
        help_text=(
            "Аббревиатура на английском, "
            "котороая будет использоваться в url."
        ),
        unique=True)
    description = models.TextField(
        verbose_name="Описание",
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    '''
    Класс представляет одну публикацию.
    Атрибуты:
    ----------
    text : str
        текст публикации
    pub_date : datetime
        дата публикации
    author : User
        автор
    группа : Group
        группа, в которой была выложена публикация.
    '''

    text = models.TextField(
        verbose_name="Текст",
        help_text="Текст поста"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор публикации",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
        verbose_name="Группа",
        help_text="Группа, к которой будет относится пост"
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text="Изображение, которое будет выводится над постом"
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    '''
    Класс представляет один комментарий к посту.
    Атрибуты:
    ----------
    text : str
        текст комментария
    create : datetime
        дата комментария
    author : User
        автор
    post : Post
        Пост, к которому был публиковам комментарий.
    '''
    text = models.TextField(
        verbose_name="Текст",
        help_text="Текст комментария"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Автор комментария",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост комментария",
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата"
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Автор",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='follow_user_author_unique_relationships'
            ),
        ]
