from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, ContactViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"contacts", ContactViewSet, basename="contact")

urlpatterns = router.urls
