# community/models.py
from django.db import models
from django.conf import settings


class Post(models.Model):
    author      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title       = models.CharField(max_length=100)
    content     = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.author.username}"


class Reaction(models.Model):
    """게시글 4종 반응(좋아요·유용해요·어려워요·슬퍼요)"""
    REACTION_CHOICES = [
        ("like",   "좋아요"),
        ("useful", "유용해요"),
        ("hard",   "어려워요"),
        ("sad",    "슬퍼요"),
    ]

    user          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post          = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    reaction_type = models.CharField(max_length=15, choices=REACTION_CHOICES)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post", "reaction_type"],
                name="unique_reaction_per_type",
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} {self.reaction_type} {self.post.title}"


class Comment(models.Model):
    post        = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content     = models.TextField()
    parent      = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.CASCADE, related_name="replies"
    )
    is_deleted  = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    @property
    def depth(self) -> int:
        return 0 if self.parent is None else 1  # 1-depth 까지만 허용

    def __str__(self):
        preview = (self.content[:17] + "…") if len(self.content) > 20 else self.content
        return f"{self.author.username}: {preview}"


class CommentReaction(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment    = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reactions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "comment"], name="unique_comment_like")
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} likes comment {self.comment_id}"
