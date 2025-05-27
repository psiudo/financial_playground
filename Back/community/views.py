# community/views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Post, Reaction, Comment, CommentReaction
from .forms import PostForm
from rest_framework import generics, permissions
from .serializers import CommentSerializer
from django.views.decorators.http import require_POST


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        parent_id = self.request.data.get('parent')

        post = Post.objects.get(id=post_id)
        parent_comment = None
        if parent_id:
            parent_comment = Comment.objects.filter(id=parent_id, post=post).first()

        serializer.save(author=self.request.user, post=post, parent=parent_comment)


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@login_required
def toggle_reaction(request, post_id, reaction_type):
    post = get_object_or_404(Post, id=post_id)
    existing_reaction = Reaction.objects.filter(user=request.user, post=post, reaction_type=reaction_type).first()

    if existing_reaction:
        existing_reaction.delete()
    else:
        Reaction.objects.create(user=request.user, post=post, reaction_type=reaction_type)

    return redirect('community:post_detail', post_id=post.id)


def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'community/post_list.html', {'posts': posts})


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('community:post_detail', post.id)
    else:
        form = PostForm()
    return render(request, 'community/post_form.html', {'form': form})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    reaction_counts = {
        'like': post.reactions.filter(reaction_type='like').count(),
        'useful': post.reactions.filter(reaction_type='useful').count(),
        'hard': post.reactions.filter(reaction_type='hard').count(),
        'sad': post.reactions.filter(reaction_type='sad').count(),
    }

    if request.user.is_authenticated:
        my_reactions = post.reactions.filter(user=request.user).values_list('reaction_type', flat=True)
    else:
        my_reactions = []

    top_level_comments = post.comments.filter(parent__isnull=True)

    edit_comment_id = request.GET.get('edit_comment_id')
    if edit_comment_id:
        edit_comment_id = int(edit_comment_id)
    else:
        edit_comment_id = None

    return render(request, 'community/post_detail.html', {
        'post': post,
        'reaction_counts': reaction_counts,
        'user_reaction_types': my_reactions,
        'top_level_comments': top_level_comments,
        'edit_comment_id': edit_comment_id,
    })


@require_POST
@login_required
def comment_create(request):
    post_id = request.POST.get('post')
    content = request.POST.get('content')
    parent_id = request.POST.get('parent')

    post = get_object_or_404(Post, id=post_id)
    parent_comment = None
    if parent_id:
        parent_comment = Comment.objects.filter(id=parent_id, post=post).first()

    Comment.objects.create(
        post=post,
        author=request.user,
        content=content,
        parent=parent_comment
    )

    return redirect('community:post_detail', post_id=post.id)


@login_required
@require_POST
def comment_update(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return redirect('community:post_detail', post_id=comment.post.id)

    new_content = request.POST.get('content')
    if new_content:
        comment.content = new_content
        comment.save()

    return redirect('community:post_detail', post_id=comment.post.id)


@login_required
@require_POST
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id

    if comment.author == request.user:
        comment.delete()

    return redirect('community:post_detail', post_id=post_id)


@login_required
@require_POST
def comment_toggle_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    reaction = CommentReaction.objects.filter(user=request.user, comment=comment).first()

    if reaction:
        reaction.delete()
    else:
        CommentReaction.objects.create(user=request.user, comment=comment)

    return redirect(request.META.get('HTTP_REFERER', 'community:post_list'))
