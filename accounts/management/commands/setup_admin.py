import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Автоматически создает суперюзера, если его еще нет в базе"

    def handle(self, *args, **kwargs):
        email = os.environ.get("SUPERUSER_EMAIL", "super@user.com")
        password = os.environ.get("SUPERUSER_PASSWORD", "password")
        username = os.environ.get("SUPERUSER_USERNAME", "superuser")

        if (
            User.objects.filter(username=username).exists()
            or User.objects.filter(email=email).exists()
        ):
            self.stdout.write(
                self.style.WARNING("Username already in use")
            )
            return

        try:
            user = User.objects.create_superuser(
                email=email,
                password=password,
                username=username,
            )

            if hasattr(user, "role"):
                user.role = "admin"
                user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfuly created: username: {username}, password: {password}."
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
