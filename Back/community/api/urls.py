# Back/community/api/urls.py
from rest_framework_nested import routers
from .views import PostViewSet, CommentViewSet

router = routers.SimpleRouter()
router.register("posts", PostViewSet, basename="community-post")

post_router = routers.NestedSimpleRouter(router, "posts", lookup="post")
post_router.register(
    "comments", CommentViewSet, basename="community-post-comments"
)

urlpatterns = [
    *router.urls,
    *post_router.urls,
]
