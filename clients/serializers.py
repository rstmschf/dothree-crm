from rest_framework import serializers
from .models import Company, Contact


class ContactSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    owner_name = serializers.ReadOnlyField(source="owner.get_full_name")

    class Meta:
        model = Contact
        fields = (
            "id",
            "company",
            "company_name",
            "first_name",
            "last_name",
            "position",
            "email",
            "phone",
            "is_primary",
            "owner",
            "created_at",
            "updated_at",
            "owner_name",
        )
        read_only_fields = (
            "owner",
            "created_at",
            "updated_at",
        )


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
