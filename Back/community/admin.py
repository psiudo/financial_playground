# back/community/admin.py
from django.contrib import admin
from community.models import Post, Comment, Reaction, CommentReaction

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Reaction)
admin.site.register(CommentReaction)
