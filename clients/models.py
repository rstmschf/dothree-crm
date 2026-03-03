from django.db import models
from django.conf import settings
from django.utils import timezone
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE


class Company(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=128, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companies",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["name"]), models.Index(fields=["owner"])]

    def __str__(self):
        return self.name


class Contact(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="contacts"
    )
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120, blank=True)
    position = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    is_primary = models.BooleanField(default=False)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contacts",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["email"]), models.Index(fields=["phone"])]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "email"],
                name="unique_contact_email_per_company",
                condition=~models.Q(email=None),
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()
