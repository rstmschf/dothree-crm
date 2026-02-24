from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import StageViewSet, LeadViewSet, DealViewSet, ActivityLogViewSet, AnalyticsView, NoteViewSet

router = DefaultRouter()
router.register(r"stages", StageViewSet, basename="stage")
router.register(r"leads", LeadViewSet, basename="lead")
router.register(r"deals", DealViewSet, basename="deal")
router.register(r"logs", ActivityLogViewSet, basename="log")
router.register(r"notes", NoteViewSet, basename="note")

urlpatterns = [
    path("", include(router.urls)),
    path("analytics/", AnalyticsView.as_view(), name="analytics"),
]