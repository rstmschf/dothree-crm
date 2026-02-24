from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Stage, Lead, Deal, ActivityLog
from .serializers import StageSerializer, LeadSerializer, DealSerializer, DealMoveStageSerializer, ActivityLogSerializer
from .services import move_deal_to_stage
from django.shortcuts import get_object_or_404
from accounts.permissions import IsOwnerOrManagerOrAdmin

class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrManagerOrAdmin)


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.select_related("company", "contact", "owner").all()
    serializer_class = LeadSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrManagerOrAdmin)


class DealViewSet(viewsets.ModelViewSet):
    serializer_class = DealSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrManagerOrAdmin)

    def get_queryset(self):
        qs = Deal.objects.select_related("stage", "company", "owner").all()
        user = self.request.user
        if getattr(user, "role", None) in ("admin", "manager"):
            return qs
        return qs.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, owner=self.request.user)

    @action(detail=True, methods=["post"], url_path="move-stage")
    def move_stage(self, request, pk=None):
        deal = self.get_object()
        serializer = DealMoveStageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stage_id = serializer.validated_data["stage_id"]
        stage = get_object_or_404(Stage, pk=stage_id)

        deal = move_deal_to_stage(deal=deal, stage=stage, actor=request.user, message=request.data.get("message", ""))
        return Response(DealSerializer(deal, context={"request": request}).data, status=status.HTTP_200_OK)


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.select_related("actor").all()
    serializer_class = ActivityLogSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ("actor",)
