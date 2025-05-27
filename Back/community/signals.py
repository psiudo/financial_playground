# community/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from community.models import Post, Comment
from notifications.models import Notification

# “글 작성” 알림
@receiver(post_save, sender=Post)
def post_notify(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user      = instance.author,
            noti_type = Notification.COMMUNITY,
            verb      = "새 글",
            target    = f"post:{instance.id}",
            message   = instance.title,
        )

# “내 글에 댓글” 알림
@receiver(post_save, sender=Comment)
def comment_notify(sender, instance, created, **kwargs):
    if created and instance.post.author != instance.author:
        Notification.objects.create(
            user      = instance.post.author,
            noti_type = Notification.COMMUNITY,
            verb      = "새 댓글",
            target    = f"post:{instance.post.id}",
            message   = instance.content[:30],
        )
