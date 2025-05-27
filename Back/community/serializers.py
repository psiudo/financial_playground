# community/serializers.py
from rest_framework import serializers
from community.models import Post, Comment, Reaction


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model  = Post
        fields = ["id", "title", "content", "author",
                  "created_at", "updated_at"]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    depth  = serializers.ReadOnlyField()                # ← property 노출
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(),
                                                allow_null=True, required=False)

    class Meta:
        model  = Comment
        fields = ["id", "post", "parent", "depth", "content",
                  "author", "created_at"]

    # depth 1 초과 차단
    def validate(self, attrs):
        parent = attrs.get("parent")
        if parent and parent.depth >= 1:
            raise serializers.ValidationError("대댓글은 depth 1까지만 허용됩니다.")
        return attrs


class ReactionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model  = Reaction
        fields = ["id", "post", "user", "is_liked"]
