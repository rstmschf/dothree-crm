from decimal import Decimal
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from sales.models import Stage, Lead, Deal
from clients.models import Company, Contact
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = "Fully seeds dev env"

    def handle(self, *args, **kwargs):
        email = settings.SUPERUSER_EMAIL
        password = settings.SUPERUSER_PASSWORD
        username = settings.SUPERUSER_USERNAME

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

        self.stdout.write("Starting to seed CRM data...")

        # 1. Setup Users
        test_user, _ = User.objects.get_or_create(
            username="test_sales_rep", defaults={"email": "sales@example.com"}
        )
        if _:
            test_user.set_password("password")
            test_user.save()

        test_user2, _ = User.objects.get_or_create(
            username="test_sales_rep2", defaults={"email": "sales2@example.com"}
        )
        if _:
            test_user2.set_password("password")
            test_user2.save()

        # 3. Companies
        company_testco, _ = Company.objects.get_or_create(
            name="TestCo",
            defaults={
                "industry": "IT",
                "website": "https://testco.com",
                "address": "Austin, Texas, USA",
                "owner": test_user,
            },
        )

        company_ttsol, _ = Company.objects.get_or_create(
            name="TestTest Solutions",
            defaults={
                "industry": "IT",
                "website": "https://tt.solutions",
                "address": "Philadelphia, Pennsylvania, USA",
                "owner": test_user,
            },
        )

        company_mainone, _ = Company.objects.get_or_create(
            name="Main One Industries",
            defaults={
                "industry": "IT",
                "website": "https://main.one",
                "address": "New York, New York, USA",
                "owner": test_user2,
            },
        )

        # 4. Contacts
        contact_max, _ = Contact.objects.get_or_create(
            email="maxtax@testco.com",
            company=company_testco,
            defaults={
                "first_name": "Max",
                "last_name": "Tax",
                "position": "Financial Director",
                "phone": "+1-222-333-4444",
                "is_primary": True,
                "owner": test_user,
            },
        )

        contact_karl, _ = Contact.objects.get_or_create(
            email="karlsarx@testest.sol",
            company=company_ttsol,
            defaults={
                "first_name": "Karl",
                "last_name": "Sarx",
                "position": "CEO",
                "is_primary": True,
                "owner": test_user,
            },
        )

        contact_hannah, _ = Contact.objects.get_or_create(
            email="montana@main.one",
            company=company_mainone,
            defaults={
                "first_name": "Hannah",
                "last_name": "Montana",
                "position": "CEO",
                "is_primary": True,
                "owner": test_user2,
            },
        )

        contact_josephine, _ = Contact.objects.get_or_create(
            email="jose@main.one",
            company=company_mainone,
            defaults={
                "first_name": "Josephine",
                "last_name": "de Beauharnais",
                "position": "CEO",
                "is_primary": False,
                "owner": test_user2,
            },
        )

        # 5. Leads
        lead_inbound, _ = Lead.objects.get_or_create(
            title="TestCo Inbound Inquiry - Software Upgrades",
            defaults={
                "source": "Website Contact Form",
                "contact": contact_max,
                "company": company_testco,
                "status": "contacted",
                "created_by": test_user,
                "owner": test_user,
            },
        )

        lead_inbound2, _ = Lead.objects.get_or_create(
            title="MainOne Inbound Inquiry - Software Upgrades",
            defaults={
                "source": "Website Contact Form",
                "contact": contact_josephine,
                "company": company_mainone,
                "status": "contacted",
                "created_by": test_user2,
                "owner": test_user2,
            },
        )

        # 6. Deals
        deal_testco, _ = Deal.objects.get_or_create(
            title="SaaS - CRM system",
            defaults={
                "value": Decimal("45500.00"),
                "currency": "USD",
                "stage": Stage.objects.get_or_create(order = 10)[0],
                "owner": test_user,
                "lead": lead_inbound,
                "company": company_testco,
                "close_date": timezone.now().date() + timezone.timedelta(days=30),
                "created_by": test_user,
            },
        )

        deal_mainone, _ = Deal.objects.get_or_create(
            title="SaaS - VoIP system",
            defaults={
                "value": Decimal("15800.00"),
                "currency": "USD",
                "stage": Stage.objects.get_or_create(order = 10)[0],
                "owner": test_user2,
                "lead": lead_inbound2,
                "company": company_mainone,
                "close_date": timezone.now().date() + timezone.timedelta(days=30),
                "created_by": test_user2,
            },
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded the CRM database."))