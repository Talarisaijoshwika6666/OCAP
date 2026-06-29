from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Post, Reply

def discuss_view(request):
    tag = request.GET.get('tag', '')
    posts = Post.objects.all().order_by('-created_at')
    if tag:
        posts = posts.filter(tag=tag)
    return render(request, 'discuss/discuss.html', {
        'posts': posts,
        'active_tag': tag,
    })

@login_required
def new_post_view(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        tag = request.POST.get('tag', 'General')
        if title and body:
            Post.objects.create(
                title=title, body=body,
                tag=tag, author=request.user
            )
            return redirect('/discuss/')
    return render(request, 'discuss/new_post.html')

def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    replies = post.replies.all().order_by('created_at')
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('/accounts/login/')
        body = request.POST.get('body', '').strip()
        if body:
            Reply.objects.create(post=post, body=body, author=request.user)
            return redirect(f'/discuss/{pk}/')
    return render(request, 'discuss/post_detail.html', {
        'post': post,
        'replies': replies,
    })

@login_required
def like_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': post.like_count()})