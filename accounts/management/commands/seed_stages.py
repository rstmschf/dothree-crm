from django.core.management.base import BaseCommand
from sales.models import Stage

class Command(BaseCommand):
    help = 'Seeds the database with default deal stages on first run'

    def handle(self, *args, **kwargs):
        if Stage.objects.exists():
            self.stdout.write(self.style.SUCCESS('Stages already exist. Skipping initialization.'))
            return

        stages = [
            {"name": "New", "order": 10, "is_system": True},
            {"name": "Qualification", "order": 20, "is_system": True},
            {"name": "Negotiation", "order": 30, "is_system": True},
            {"name": "Closed Won", "order": 40, "is_system": True, "is_won": True},
            {"name": "Closed Lost", "order": 50, "is_system": True, "is_lost": True},
        ]
        
        for data in stages:
            Stage.objects.create(**data)
            
        self.stdout.write(self.style.SUCCESS('Successfully initialized default stages!'))