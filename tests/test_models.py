import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from sales.models import Stage, Lead, Deal
from clients.models import Company, Contact

User = get_user_model()

@pytest.fixture
def test_user():
    return User.objects.create_user(username="test_sales_rep", email="sales@example.com", password="password123")

@pytest.fixture
def test_stage():
    return Stage.objects.create(name="1 - New", order=1)

@pytest.fixture
def test_company(test_user):
    return Company.objects.create(
        name="Testing Test Co",
        industry="Manufacturing",
        owner=test_user
    )

@pytest.fixture
def test_contact(test_company, test_user):
    return Contact.objects.create(
        company=test_company,
        first_name="Max",
        last_name="Tax",
        email="Maxtax@testexample.com",
        owner=test_user
    )

@pytest.mark.django_db
class TestCRMModels:

    def test_company_creation(self, test_company):
        assert test_company.name == "Testing Test Co"
        assert str(test_company) == "Testing Test Co"
        assert test_company.is_active is True

    def test_contact_creation(self, test_contact):
        assert test_contact.first_name == "Max"
        assert str(test_contact) == "Max Tax"
        assert test_contact.company.name == "Testing Test Co"

    def test_lead_creation(self, test_contact, test_company, test_user):
        lead = Lead.objects.create(
            title="Inbound Inquiry",
            contact=test_contact,
            company=test_company,
            created_by=test_user,
            owner=test_user
        )
        assert lead.title == "Inbound Inquiry"
        assert str(lead) == "Inbound Inquiry"
        assert lead.status == "new"

    def test_deal_creation(self, test_stage, test_company, test_user):
        deal = Deal.objects.create(
            title="Testing Test Co Factory Floor Retrofit",
            value=Decimal("45500.00"),
            stage=test_stage,
            owner=test_user,
            company=test_company,
        )
        assert deal.value == Decimal("45500.00")
        assert deal.currency == "USD"
        assert str(deal) == "Testing Test Co Factory Floor Retrofit (45500.00 USD)"