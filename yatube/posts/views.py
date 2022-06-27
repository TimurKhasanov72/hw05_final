from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post
from .utils import get_page_object

User = get_user_model()


@cache_page(20, key_prefix="index_page")
def index(request):

    posts = Post.objects.all()

    context = {
        'page_obj': get_page_object(
            posts,
            request.GET.get('page')
        )
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
        'page_obj': get_page_object(
            posts,
            request.GET.get('page')
        ),
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):

    user = get_object_or_404(User, username=username)

    following = (
        (request.user.is_authenticated)
        and (user != request.user)
    )

    if following:
        following = Follow.objects.filter(
            user=request.user,
            author=user,
        ).exists()

    context = {
        'author': user,
        'page_obj': get_page_object(
            user.posts.all(),
            request.GET.get('page')
        ),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):

    post = get_object_or_404(Post, pk=post_id)

    context = {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.all()
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)

    return render(
        request,
        'posts/post_create.html',
        {'form': form}
    )


@login_required
def post_edit(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    # Сразу перенаправляем на просмотр
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        # Перенаправляем на информацию о посте
        return redirect('posts:post_detail', post_id=post_id)

    # Отдаем форму на редактирование
    return render(request, 'posts/post_create.html', {
        'form': form,
        'post_id': post_id,
        'is_edit': True
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)

    context = {
        'page_obj': get_page_object(
            posts,
            request.GET.get('page')
        )
    }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)

    # проверяем, что не подписываемся на самого себя
    if (request.user.username != username):

        # проверяем, что еще нет такой подписки
        check_following = Follow.objects.filter(
            user=request.user,
            author=author,
        ).exists()

        if check_following is False:
            Follow.objects.create(
                user=request.user,
                author=author,
            )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)

    Follow.objects.filter(
        user=request.user,
        author=author,
    ).delete()

    return redirect('posts:profile', username)
