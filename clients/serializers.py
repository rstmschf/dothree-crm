from rest_framework import serializers
from .models import Company, Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = (
            "id",
            "company",
            "first_name",
            "last_name",
            "position",
            "email",
            "phone",
            "is_primary",
            "owner",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("owner", "created_at", "updated_at")


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "industry",
            "website",
            "address",
            "owner",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("owner", "created_at", "updated_at")


class CompanyDetailSerializer(CompanySerializer):
    contacts = ContactSerializer(many=True, read_only=True)

    class Meta(CompanySerializer.Meta):
        fields = CompanySerializer.Meta.fields + ("contacts",)
