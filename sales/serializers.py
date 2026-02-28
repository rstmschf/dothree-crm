from rest_framework import serializers
from .models import Stage, Lead, Deal, ActivityLog, Note, Reminder
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ("id", "name", "order", "is_won", "is_lost", "is_system")
        read_only_fields = ("is_system",)

    def validate(self, data):
        if self.instance and self.instance.is_system:
            forbidden_fields = ["name", "is_won", "is_lost"]

            for field in forbidden_fields:
                if field in data and data[field] != getattr(self.instance, field):
                    raise serializers.ValidationError(
                        {field: "This field is uneditable for system stage."}
                    )
        return data


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            "id",
            "title",
            "source",
            "contact",
            "company",
            "status",
            "owner",
            "created_by",
            "created_at",
            "updated_at",
        )
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


class NoteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = (
            "id",
            "deal",
            "created_by",
            "text",
            "created_at",
            "updated_at",
            "created_by_name",
            "attachment",
        )
        read_only_fields = ("created_by", "created_at", "updated_at")

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return "Deleted User"

class ReminderSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    deal_title = serializers.ReadOnlyField(source="deal.title")
    
    class Meta:
        model = Reminder
        fields = (
            "id",
            "text",
            "created_at",
            "updated_at",
            "deal",
            "owner",
            "date",
            "is_done",
            "contact",
            "owner_name",
            "deal_title"
        )
        read_only_fields = ("created_at", "updated_at", "owner",)

    def validate_date(self, value):
        now = timezone.now()
        if value < now:
            raise serializers.ValidationError("Reminder can not be created for Past.")
        
        return value
    
    def get_owner_name(self, obj):
        if obj.owner:
            return obj.owner.get_full_name() or obj.owner.username
        return "Deleted User"