import pytest
from django.urls import reverse
from rest_framework import status
from clients.models import Company
from sales.models import Stage, Deal


@pytest.mark.django_db
class TestCompanyAPI:
    def test_create_company_authenticated(self, auth_api_client, user):
        """Test that an authenticated user can create a Company."""
        url = reverse("company-list")
        payload = {
            "name": "API Test Corp",
            "industry": "FinTech",
            "website": "https://apitestcorp.com",
        }

        response = auth_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "API Test Corp"
        assert Company.objects.filter(name="API Test Corp").exists()

    def test_create_company_unauthenticated(self, api_client):
        """Test that an anonymous user CANNOT create a Company."""
        url = reverse("company-list")
        payload = {"name": "UNA Co"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]
        assert not Company.objects.filter(name="UNA Co").exists()

    def test_list_companies(self, auth_api_client, user):
        """Test retrieving a list of companies."""
        Company.objects.create(name="ListCo", owner=user)

        url = reverse("company-list")
        response = auth_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]["name"] == "ListCo"


@pytest.mark.django_db
class TestDealAPI:
    def test_create_deal(self, auth_api_client, user):
        """Test creating a Deal, which requires existing ForeignKey relationships."""
        stage = Stage.objects.create(name="Negotiation", order=2)
        company = Company.objects.create(name="DealMaker Inc", owner=user)

        url = reverse("deal-list")
        payload = {
            "title": "Enterprise Licensing 2026",
            "value": "125000.00",
            "currency": "USD",
            "stage": stage.id,
            "company": company.id,
        }

        response = auth_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Enterprise Licensing 2026"

        deal = Deal.objects.get(title="Enterprise Licensing 2026")
        assert deal.value == 125000.00
        assert deal.stage == stage
        assert deal.company == company
