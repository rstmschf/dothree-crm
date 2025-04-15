from django.contrib import admin
from .models import Stage, Lead, Deal, ActivityLog, Note, Reminder


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "order", "is_won", "is_lost")
    ordering = ("order",)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "company",
        "contact",
        "status",
        "owner",
        "created_at",
    )
    search_fields = ("title", "company__name", "contact__email")


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "value",
        "currency",
        "stage",
        "owner",
        "created_at",
        "is_active",
    )
    list_filter = ("stage", "owner", "is_active")
    search_fields = ("title", "company__name", "owner__username")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("id", "actor", "verb", "created_at")
    search_fields = ("verb", "message", "actor__username")
    readonly_fields = (
        "actor",
        "verb",
        "message",
        "content_type",
        "object_id",
        "created_at",
    )


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "deal",
        "created_by",
        "short_text",
        "created_at",
    )
    list_filter = ("deal", "created_by", "created_at")
    search_fields = ("deal__title", "created_by__username")

    def short_text(self, obj):
        if len(obj.text) > 50:
            return f"{obj.text[:50]}..."
        return obj.text

    short_text.short_description = "Title"


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "deal", "owner", "date", "text")
    search_fields = ("deal", "owner", "text")
    list_filter = ("created_at", "owner", "deal")
