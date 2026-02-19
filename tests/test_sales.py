from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from sales.models import Stage, Deal, ActivityLog
from clients.models import Company

User = get_user_model()

class DealWorkflowTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="pw", email="u@example.com", role="admin")
        self.client.force_authenticate(user=self.user)
        self.s1 = Stage.objects.create(name="New", order=0)
        self.s2 = Stage.objects.create(name="Negotiation", order=1)
        self.company = Company.objects.create(name="C")
        self.deal = Deal.objects.create(title="D", value="100", currency="USD", stage=self.s1, company=self.company, created_by=self.user, owner=self.user)

    def test_move_stage_creates_log(self):
        url = reverse("deal-move-stage", kwargs={"pk": self.deal.pk})
        r = self.client.post(url, {"stage_id": self.s2.pk}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.stage.pk, self.s2.pk)
        self.assertTrue(ActivityLog.objects.filter(object_id=self.deal.pk, verb="moved_stage").exists())
