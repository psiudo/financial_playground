# community/api/views.py
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from community.models import Post, Comment, Reaction
from .serializers import (
    PostSerializer, CommentSerializer, ReactionSerializer
)


class PostViewSet(viewsets.ModelViewSet):
    queryset           = Post.objects.select_related("author")
    serializer_class   = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # POST /posts/<pk>/toggle-reaction/?type=like
    @action(detail=True, methods=["post"], url_path="toggle-reaction")
    def toggle_reaction(self, request, pk=None):
        reaction_type = request.query_params.get("type")
        allowed       = {c[0] for c in Reaction.REACTION_CHOICES}

        if reaction_type not in allowed:
            return Response(
                {"detail": f"type 파라미터는 {allowed} 중 하나여야 합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        post, user = self.get_object(), request.user
        existing = Reaction.objects.filter(
            post=post, user=user, reaction_type=reaction_type
        ).first()

        # 이미 있으면 삭제(=토글 OFF)
        if existing:
            existing.delete()
            return Response(
                {"toggled_on": False, "reaction_type": reaction_type},
                status=status.HTTP_200_OK,
            )

        # 없으면 생성(=토글 ON)
        obj  = Reaction.objects.create(post=post, user=user, reaction_type=reaction_type)
        data = ReactionSerializer(obj).data | {"toggled_on": True}
        return Response(data, status=status.HTTP_200_OK)


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class   = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    # /posts/<post_pk>/comments/ 쿼리셋
    def get_queryset(self):
        return Comment.objects.filter(
            post_id=self.kwargs["post_pk"]
        ).select_related("author").order_by("created_at")

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs["post_pk"])
        serializer.save(author=self.request.user, post=post)
