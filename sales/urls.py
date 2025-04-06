from rest_framework.routers import DefaultRouter
from .views import StageViewSet, LeadViewSet, DealViewSet, ActivityLogViewSet

router = DefaultRouter()
router.register(r"stages", StageViewSet, basename="stage")
router.register(r"leads", LeadViewSet, basename="lead")
router.register(r"deals", DealViewSet, basename="deal")
router.register(r"logs", ActivityLogViewSet, basename="log")

urlpatterns = router.urls
