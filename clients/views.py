from django.db.models import Q
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from .models import Company, Contact
from .serializers import CompanySerializer, CompanyDetailSerializer, ContactSerializer
from accounts.permissions import IsOwnerOrManagerOrAdmin, IsManagerOrAdmin


class CompanyViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filterset_fields = ("owner", "industry", "is_active")
    search_fields = ("name", "website", "address")
    ordering_fields = ("created_at", "name")
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrManagerOrAdmin)

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsManagerOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        qs = Company.objects.filter(is_active=True)
        user = self.request.user
        if getattr(user, "role", None) in ("admin", "manager"):
            return qs
        return qs.filter(owner=user)

    def get_serializer_class(self):
        if self.action in ("retrieve",):
            return CompanyDetailSerializer
        return CompanySerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filterset_fields = ("company", "owner", "is_primary")
    search_fields = ("first_name", "last_name", "email", "phone", "position")
    ordering_fields = ("created_at", "first_name")
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrManagerOrAdmin)

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsManagerOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        qs = Contact.objects.select_related("company", "owner").all()
        user = self.request.user
        if getattr(user, "role", None) in ("admin", "manager"):
            return qs
        return qs.filter(Q(owner=user) | Q(company__owner=user))

    def perform_create(self, serializer):
        company = serializer.validated_data.get("company")
        user = self.request.user

        if getattr(user, "role", None) in ("admin", "manager"):
            serializer.save(owner=user)
            return

        if company is None:
            raise PermissionDenied("Company must be provided.")
        if getattr(company, "owner", None) != user:
            raise PermissionDenied(
                "You cannot create contact for a company you don't own."
            )
        serializer.save(owner=user)
