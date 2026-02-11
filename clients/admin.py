from django.contrib import admin
from .models import Company, Contact


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "industry", "owner", "is_active", "created_at")
    search_fields = ("name", "website", "address")
    list_filter = ("industry", "is_active", "owner")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "company", "email", "phone", "is_primary", "owner")
    search_fields = ("first_name", "last_name", "email", "phone", "company__name")
    list_filter = ("is_primary", "company")