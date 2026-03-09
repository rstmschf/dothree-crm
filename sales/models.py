from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
from clients.models import Company, Contact
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Index, Q
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE


class Stage(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    is_won = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return self.name


class Lead(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=100, blank=True, null=True)
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads"
    )
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads"
    )
    status = models.CharField(max_length=50, default="new")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_leads",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class Deal(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    title = models.CharField(max_length=255)
    value = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    currency = models.CharField(max_length=12, default="USD")
    stage = models.ForeignKey(Stage, on_delete=models.PROTECT, related_name="deals")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deals",
    )
    lead = models.ForeignKey(
        Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals"
    )
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals"
    )
    close_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_deals",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.title} ({self.value} {self.currency})"


class ActivityLog(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )
    verb = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-created_at",)


class Note(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name="notes")
    text = models.TextField(blank=True)
    original_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notes",
    )
    attachment = models.FileField(upload_to="deal_notes/", blank=True, null=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Note on {self.deal.title}: {self.text[:50]}..."


class Reminder(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    text = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name="reminders")
    date = models.DateTimeField(blank=False)
    reminded_1h = models.BooleanField(default=False)
    reminded_5m = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reminders",
    )
    is_done = models.BooleanField(default=False)
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        related_name="reminders",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("date",)
        indexes = [
            Index(
                fields=["date"],
                condition=Q(is_done=False, reminded_1h=False),
                name="idx_active_reminders_1h",
            ),
            Index(
                fields=["date"],
                condition=Q(is_done=False, reminded_5m=False),
                name="idx_active_reminders_5m",
            ),
            Index(fields=["owner", "is_done"]),
        ]

    def __str__(self):
        status = "✅" if self.is_done else "🕒"
        text_preview = f" {self.text[:20]}..." if self.text else ""
        return f"Reminder for {self.deal.title}: {status} {text_preview}"
