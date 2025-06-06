# Back/notifications/migrations/0003_alter_notification_message_and_more.py
# Generated by Django 4.2.20 on 2025-05-26 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0002_notification_target_notification_verb_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="message",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="notification",
            name="noti_type",
            field=models.CharField(
                choices=[
                    ("trade", "거래"),
                    ("product", "금융상품"),
                    ("strategy", "전략"),
                    ("community", "커뮤니티"),
                    ("system", "시스템"),
                ],
                default="system",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="target",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="notification",
            name="verb",
            field=models.CharField(max_length=50),
        ),
    ]
