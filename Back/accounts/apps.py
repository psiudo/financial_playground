# back/accounts/apps.py
from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save
from django.db import transaction
from django.db.models import F


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from accounts.models import PointTransaction

        def create_point_log(sender, instance, created, **kwargs):
            if not created:
                return
            with transaction.atomic():
                instance.point_balance = F("point_balance") + 1_000
                instance.save(update_fields=["point_balance"])
                instance.refresh_from_db(fields=["point_balance"])
                PointTransaction.objects.create(
                    user=instance,
                    delta_point=1_000,
                    kind=PointTransaction.INCREASE,
                    reason="initial_signup",
                )

        post_save.connect(
            create_point_log,
            sender=settings.AUTH_USER_MODEL,
            weak=False,
            dispatch_uid="accounts_create_point_log",
        )
