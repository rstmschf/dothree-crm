from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import call_command


User = get_user_model()

class Command(BaseCommand):
    help = "Fully seeds test env"

    def handle(self, *args, **kwargs):
        call_command("setup_admin")
        call_command("seed_stages")
        call_command("seed_crm_data")
        call_command("set_wh")
        