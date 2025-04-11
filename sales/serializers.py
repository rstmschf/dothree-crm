from rest_framework import serializers
from .models import Stage, Lead, Deal, ActivityLog
from django.contrib.auth import get_user_model

User = get_user_model()


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ("id", "name", "order", "is_won", "is_lost")


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ("id", "title", "source", "contact", "company", "status", "owner", "created_by", "created_at", "updated_at")
        read_only_fields = ("created_by", "created_at", "updated_at")


class DealSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    class Meta:
        model = Deal
        fields = (
            "id",
            "title",
            "value",
            "currency",
            "stage",
            "owner",
            "lead",
            "company",
            "close_date",
            "created_by",
            "created_at",
            "updated_at",
            "company_name",
        )
        read_only_fields = ("created_by", "created_at", "updated_at")


class DealMoveStageSerializer(serializers.Serializer):
    stage_id = serializers.IntegerField()


class ActivityLogSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField()
    target = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = ("id", "actor", "verb", "message", "created_at", "target")

    def get_target(self, obj):
        return str(obj.target)
