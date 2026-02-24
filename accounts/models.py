from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        SALES = "sales", "Sales"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SALES,
    )

    email = models.EmailField(unique=True)

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save(update_fields=["is_active"])

    def __str__(self):
        return f"{self.username} ({self.role})"