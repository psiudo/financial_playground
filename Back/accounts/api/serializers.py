# Back/accounts/api/serializers.py
from rest_framework import serializers
from accounts.models import CustomUser


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "birth_date",
            "job",
            "annual_income",
            "risk_grade",
            "preferred_bank",
            "profile_image",
            "bio",
            "point_balance",
            "signup_date",
            "social_login_type",
            "is_email_verified",
            "joined_financial_products",
            
        ]
        read_only_fields = ["username", "email", "point_balance", "signup_date"]
