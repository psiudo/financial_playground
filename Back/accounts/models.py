# Back/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    GOOGLE = "google"
    KAKAO  = "kakao"
    NAVER  = "naver"
    SOCIAL_CHOICES = [(GOOGLE, "구글"), (KAKAO, "카카오"), (NAVER, "네이버")]

    birth_date      = models.DateField(null=True, blank=True)
    job             = models.CharField(max_length=100, blank=True)
    annual_income   = models.PositiveIntegerField(null=True, blank=True)
    risk_grade      = models.CharField(max_length=20, blank=True)          # low / middle / high
    preferred_bank  = models.CharField(max_length=100, blank=True)
    profile_image   = models.ImageField(upload_to="profiles/", null=True, blank=True)
    bio             = models.TextField(blank=True)
    point_balance   = models.IntegerField(default=0)
    signup_date     = models.DateTimeField(auto_now_add=True)
    social_login_type = models.CharField(
        max_length=20,
        blank=True,
        choices=SOCIAL_CHOICES,
        help_text="OAuth 공급자 타입"
    )
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class PointTransaction(models.Model):
    INCREASE = "in"
    DECREASE = "out"
    KIND_CHOICES = [(INCREASE, "적립"), (DECREASE, "차감")]

    user         = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="transactions")
    delta_point  = models.IntegerField()
    kind         = models.CharField(max_length=3, choices=KIND_CHOICES)
    reason       = models.CharField(max_length=100)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.delta_point > 0 else "-"
        return f"{self.user.username} {sign}{abs(self.delta_point)}"
