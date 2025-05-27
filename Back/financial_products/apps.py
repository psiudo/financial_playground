# financial_products/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver


class FinancialProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "financial_products"

    def ready(self):
        from financial_products.models import JoinedProduct
        from notifications.models import Notification

        @receiver(post_save, sender=JoinedProduct, dispatch_uid="product_join_notification")
        def create_join_notification(sender, instance, created, **kwargs):
            """
            상품 가입 성공 시 알림 생성
            """
            if not created:
                return
            Notification.objects.create(
                user=instance.user,
                noti_type=Notification.PRODUCT,
                message=f"{instance.product.name} 가입 완료",
            )
