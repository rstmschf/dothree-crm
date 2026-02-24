from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ("id", "username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")

    fieldsets = UserAdmin.fieldsets + (("CRM fields", {"fields": ("role",)}),)

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("CRM fields", {"fields": ("role", "email")}),
    )

    def delete_model(self, request, obj):
        obj.is_active = False
        obj.save(update_fields=["is_active"])

    def delete_queryset(self, request, queryset):
        queryset.update(is_active = False)