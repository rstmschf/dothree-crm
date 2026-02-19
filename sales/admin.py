from django.contrib import admin
from .models import Stage, Lead, Deal, ActivityLog

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "order", "is_won", "is_lost")
    ordering = ("order",)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "company", "contact", "status", "owner", "created_at")
    search_fields = ("title", "company__name", "contact__email")


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "value", "currency", "stage", "owner", "created_at", "is_active")
    list_filter = ("stage", "owner", "is_active")
    search_fields = ("title", "company__name", "owner__username")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("id", "actor", "verb", "created_at")
    search_fields = ("verb", "message", "actor__username")
    readonly_fields = ("actor", "verb", "message", "content_type", "object_id", "created_at")
