from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from .models import Stage, Lead, Deal, ActivityLog, Note, Reminder
from .serializers import (
    StageSerializer,
    LeadSerializer,
    DealSerializer,
    DealMoveStageSerializer,
    ActivityLogSerializer,
    NoteSerializer,
    ReminderSerializer,
)
from .services import move_deal_to_stage
from .tasks import process_ai_note_task, broadcast_new_note_task, broadcast_reminder_update
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Q
from django.utils import timezone
from accounts.permissions import IsOwnerOrManagerOrAdmin, IsManagerOrAdmin


class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer
    
    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsManagerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_destroy(self, instance):
        if instance.is_system:
            raise PermissionDenied("System stages can not be deleted.")
        instance.delete()


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.select_related("company", "contact", "owner").all()
    serializer_class = LeadSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrManagerOrAdmin)


class DealViewSet(viewsets.ModelViewSet):
    serializer_class = DealSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrManagerOrAdmin)

    def get_queryset(self):
        user = self.request.user
        queryset = Deal.objects.select_related('company').all()

        is_management = getattr(user, "role", None) in ("admin", "manager")
        if not is_management:
            queryset = queryset.filter(owner=user)

        company_id = self.request.query_params.get("company")
        if company_id:
            queryset = queryset.filter(company_id=company_id)

        contact_id = self.request.query_params.get("contact")
        if contact_id:
            queryset = queryset.filter(contact_id=contact_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, owner=self.request.user)

    @action(detail=True, methods=["post"], url_path="move-stage")
    def move_stage(self, request, pk=None):
        deal = self.get_object()
        serializer = DealMoveStageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stage_id = serializer.validated_data["stage_id"]
        stage = get_object_or_404(Stage, pk=stage_id)

        deal = move_deal_to_stage(
            deal=deal,
            stage=stage,
            actor=request.user,
            message=request.data.get("message", ""),
        )
        return Response(
            DealSerializer(deal, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.select_related("actor").all()
    serializer_class = ActivityLogSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ("actor",)


class AnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrManagerOrAdmin]

    def get(self, request):
        user = request.user
        now = timezone.now()

        base_deals = Deal.objects.all()
        is_management = getattr(user, "role", None) in ("admin", "manager")

        if not is_management:
            base_deals = base_deals.filter(owner=user)

        open_deals = base_deals.filter(stage__is_won=False, stage__is_lost=False)
        pipeline_value = open_deals.aggregate(total=Sum("value"))["total"] or 0

        this_month_deals = open_deals.filter(
            close_date__month=now.month, close_date__year=now.year
        )
        expected_revenue = this_month_deals.aggregate(total=Sum("value"))["total"] or 0

        won_deals = base_deals.filter(stage__is_won=True).count()
        lost_deals = base_deals.filter(stage__is_lost=True).count()
        total_closed = won_deals + lost_deals
        win_rate = round((won_deals / total_closed * 100) if total_closed > 0 else 0, 1)

        deal_filter = Q()
        if not is_management:
            deal_filter = Q(deals__owner=user)

        stages = (
            Stage.objects.annotate(
                deal_count=Count("deals", filter=deal_filter),
                total_value=Sum("deals__value", filter=deal_filter),
            )
            .values("name", "deal_count", "total_value", "order", "is_won", "is_lost")
            .order_by("order")
        )

        return Response(
            {
                "pipeline_value": pipeline_value,
                "expected_revenue": expected_revenue,
                "win_rate": win_rate,
                "won_deals": won_deals,
                "stages": list(stages),
            }
        )


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrManagerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        queryset = Note.objects.select_related("created_by").all()

        is_management = getattr(user, "role", None) in ("admin", "manager")

        if not is_management:
            queryset = queryset.filter(deal__owner=user)

        deal_id = self.request.query_params.get("deal")
        if deal_id:
            queryset = queryset.filter(deal_id=deal_id)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        deal = serializer.validated_data["deal"]
        is_management = getattr(user, "role", None) in ("admin", "manager")
        
        if not is_management and deal.owner != user:
            raise PermissionDenied("You cannot add notes to a deal you do not own.")
        raw_text = serializer.validated_data.get("text", "")

        if '@bot' in raw_text.lower():
            prompt_text = raw_text.lower().replace('@bot', '', 1).strip()
            
            note = serializer.save(
                created_by=user, 
                original_text=raw_text,
                text="⏳ *AI is working on it...*" 
            )
            broadcast_new_note_task.delay(note.id)
            process_ai_note_task.delay(note.id, prompt_text)
            return
            
        note = serializer.save(created_by=user)
        broadcast_new_note_task.delay(note.id)

class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrManagerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        queryset = Reminder.objects.select_related("owner", "deal").all()

        is_management = getattr(user, "role", None) in ("admin", "manager")

        if not is_management:
            queryset = queryset.filter(owner=user)

        return queryset
    
    def perform_create(self, serializer):
        reminder = serializer.save(owner=self.request.user)
        broadcast_reminder_update.delay(reminder.id, reminder.owner.id, "created")

    def perform_update(self, serializer):
        reminder = serializer.save()
        if reminder.owner:
            broadcast_reminder_update.delay(reminder.id, reminder.owner.id, "updated")

    def perform_destroy(self, instance):
        reminder_id = instance.id
        owner_id = instance.owner.id if instance.owner else None
        instance.delete()
        if owner_id:
            broadcast_reminder_update.delay(reminder_id, owner_id, "deleted")

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        reminder = self.get_object()
        reminder.is_done = not reminder.is_done
        reminder.save(update_fields=["is_done", "updated_at"])
        
        if reminder.owner:
            broadcast_reminder_update.delay(reminder.id, reminder.owner.id, "updated")
            
        return Response({
            "id": reminder.id,
            "is_done": reminder.is_done,
            "status": "success"
        })

