from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.services import (
    create_notification,
    mark_notification_as_read,
    archive_notification,
)

from .mixins import CompanyQuerySetMixin, CompanyCreateMixin
from .permissions import (
    IsCompanyUser,
    IsCompanyObject,
    IsCompanyAdmin,
    IsOperationsManager,
    IsServiceManager,
    IsDispatcher,
    IsAccountant,
)
from .serializers import (
    CurrentUserSerializer,
    CompanyReadOnlySerializer,
    DepartmentSerializer, EmployeeSerializer, TeamSerializer,
    CustomerSerializer, CustomerContactSerializer, CustomerLocationSerializer,
    ServiceCategorySerializer, ServiceSerializer, ServiceRequirementSerializer,
    SkillSerializer, EmployeeSkillSerializer, CertificationSerializer,
    EmployeeCertificationSerializer,
    ContractSerializer, ContractServiceSerializer, SLASerializer,
    TicketSerializer, WorkOrderSerializer,
    WorkScheduleSerializer, EmployeeAvailabilitySerializer,
    AttendanceSerializer, TimeEntrySerializer, LeaveRequestSerializer,
    AssetCategorySerializer, AssetSerializer, AssetMaintenanceSerializer,
    ProductSerializer, WarehouseSerializer, StockSerializer,
    StockMovementSerializer,
    InvoiceSerializer, InvoiceItemSerializer, PaymentSerializer, ExpenseSerializer,
    NotificationSerializer,
)

from organizations.models import Company
from workforce.models import Department, Employee, Team
from customers.models import Customer, CustomerContact, CustomerLocation
from services.models import ServiceCategory, Service, ServiceRequirement
from skills.models import Skill, EmployeeSkill, Certification, EmployeeCertification
from contracts.models import Contract, ContractService, SLA
from tickets.models import Ticket
from workorders.models import WorkOrder
from scheduling.models import WorkSchedule, EmployeeAvailability
from attendance.models import Attendance, TimeEntry
from leave.models import LeaveRequest
from assets.models import AssetCategory, Asset, AssetMaintenance
from inventory.models import Product, Warehouse, Stock, StockMovement
from billing.models import Invoice, InvoiceItem, Payment, Expense
from notifications.models import Notification


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)


class SecurityTestAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get(self, request):
        return Response({
            "message": "API security check passed.",
            "user": request.user.email,
            "role": request.user.role,
            "company_id": request.user.company_id,
        })


class CompanyReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanyReadOnlySerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        return Company.objects.filter(id=self.request.user.company_id)


class BaseCompanyViewSet(
    CompanyQuerySetMixin,
    CompanyCreateMixin,
    viewsets.ModelViewSet,
):
    permission_classes = [IsAuthenticated, IsCompanyUser, IsCompanyObject]

    def get_permissions(self):
        if self.action == "destroy":
            return [
                IsAuthenticated(),
                IsCompanyUser(),
                IsCompanyAdmin(),
            ]
        return super().get_permissions()


class DepartmentViewSet(BaseCompanyViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class EmployeeViewSet(BaseCompanyViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAuthenticated(), IsCompanyUser(), IsCompanyAdmin()]
        return [IsAuthenticated(), IsCompanyUser()]


class TeamViewSet(BaseCompanyViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class CustomerViewSet(BaseCompanyViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerContactViewSet(viewsets.ModelViewSet):
    queryset = CustomerContact.objects.all()
    serializer_class = CustomerContactSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        return CustomerContact.objects.filter(
            customer__company_id=self.request.user.company_id
        )

    def perform_create(self, serializer):
        customer = serializer.validated_data["customer"]
        if customer.company_id != self.request.user.company_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Customer belongs to another company.")
        serializer.save()


class CustomerLocationViewSet(viewsets.ModelViewSet):
    queryset = CustomerLocation.objects.all()
    serializer_class = CustomerLocationSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        return CustomerLocation.objects.filter(
            customer__company_id=self.request.user.company_id
        )

    def perform_create(self, serializer):
        customer = serializer.validated_data["customer"]
        if customer.company_id != self.request.user.company_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Customer belongs to another company.")
        serializer.save()


class ServiceCategoryViewSet(BaseCompanyViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer


class ServiceViewSet(BaseCompanyViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class ServiceRequirementViewSet(viewsets.ModelViewSet):
    queryset = ServiceRequirement.objects.all()
    serializer_class = ServiceRequirementSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        return ServiceRequirement.objects.filter(
            service__company_id=self.request.user.company_id
        )

    def perform_create(self, serializer):
        service = serializer.validated_data["service"]
        if service.company_id != self.request.user.company_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Service belongs to another company.")
        serializer.save()


class SkillViewSet(BaseCompanyViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class EmployeeSkillViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSkill.objects.all()
    serializer_class = EmployeeSkillSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        return EmployeeSkill.objects.filter(
            employee__company_id=self.request.user.company_id
        )


class CertificationViewSet(BaseCompanyViewSet):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer


class EmployeeCertificationViewSet(viewsets.ModelViewSet):
    queryset = EmployeeCertification.objects.all()
    serializer_class = EmployeeCertificationSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        return EmployeeCertification.objects.filter(
            employee__company_id=self.request.user.company_id
        )


class ContractViewSet(BaseCompanyViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer


class ContractServiceViewSet(viewsets.ModelViewSet):
    queryset = ContractService.objects.all()
    serializer_class = ContractServiceSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        return ContractService.objects.filter(
            contract__company_id=self.request.user.company_id
        )


class SLAViewSet(BaseCompanyViewSet):
    queryset = SLA.objects.all()
    serializer_class = SLASerializer


class TicketViewSet(BaseCompanyViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsCompanyUser, IsServiceManager],
    )
    def close(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = "CLOSED"
        ticket.closed_at = timezone.now()
        ticket.save(update_fields=["status", "closed_at"])
        return Response(TicketSerializer(ticket).data)


class WorkOrderViewSet(BaseCompanyViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer

    @action(
        detail=True,
        methods=["post"],
        url_path="dispatch",
        permission_classes=[
            IsAuthenticated,
            IsCompanyUser,
            IsDispatcher,
        ],
    )
    def dispatch_work_order(self, request, pk=None):
        work_order = self.get_object()

        work_order.status = "DISPATCHED"

        work_order.save(
            update_fields=["status"]
        )

        return Response(
            WorkOrderSerializer(work_order).data
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsAuthenticated,
            IsCompanyUser,
        ],
    )
    def start(self, request, pk=None):
        work_order = self.get_object()

        work_order.status = "IN_PROGRESS"
        work_order.actual_start = timezone.now()

        work_order.save(
            update_fields=[
                "status",
                "actual_start",
            ]
        )

        return Response(
            WorkOrderSerializer(work_order).data
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsAuthenticated,
            IsCompanyUser,
        ],
    )
    def complete(self, request, pk=None):
        work_order = self.get_object()

        work_order.status = "COMPLETED"
        work_order.actual_end = timezone.now()

        completion_notes = request.data.get(
            "completion_notes"
        )

        if (
            completion_notes is not None
            and hasattr(work_order, "completion_notes")
        ):
            work_order.completion_notes = completion_notes

            work_order.save(
                update_fields=[
                    "status",
                    "actual_end",
                    "completion_notes",
                ]
            )
        else:
            work_order.save(
                update_fields=[
                    "status",
                    "actual_end",
                ]
            )

        return Response(
            WorkOrderSerializer(work_order).data
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsAuthenticated,
            IsCompanyUser,
            IsServiceManager,
        ],
    )
    def verify(self, request, pk=None):
        work_order = self.get_object()

        work_order.status = "VERIFIED"

        if hasattr(
            work_order,
            "verification_notes",
        ):
            work_order.verification_notes = request.data.get(
                "verification_notes",
                getattr(
                    work_order,
                    "verification_notes",
                    "",
                ),
            )

        fields = ["status"]

        if hasattr(
            work_order,
            "verification_notes",
        ):
            fields.append(
                "verification_notes"
            )

        work_order.save(
            update_fields=fields
        )

        return Response(
            WorkOrderSerializer(work_order).data
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsAuthenticated,
            IsCompanyUser,
            IsServiceManager,
        ],
    )
    def close(self, request, pk=None):
        work_order = self.get_object()

        work_order.status = "CLOSED"

        work_order.save(
            update_fields=["status"]
        )

        return Response(
            WorkOrderSerializer(work_order).data
        )


class WorkScheduleViewSet(BaseCompanyViewSet):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer


class EmployeeAvailabilityViewSet(BaseCompanyViewSet):
    queryset = EmployeeAvailability.objects.all()
    serializer_class = EmployeeAvailabilitySerializer


class AttendanceViewSet(BaseCompanyViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer


class TimeEntryViewSet(BaseCompanyViewSet):
    queryset = TimeEntry.objects.all()
    serializer_class = TimeEntrySerializer


class LeaveRequestViewSet(BaseCompanyViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsAuthenticated, IsCompanyUser, IsOperationsManager
        ],
    )
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = "APPROVED"
        leave.reviewer = request.user
        leave.reviewed_at = timezone.now()
        leave.save(update_fields=["status", "reviewer", "reviewed_at"])
        return Response(LeaveRequestSerializer(leave).data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsAuthenticated, IsCompanyUser, IsOperationsManager
        ],
    )
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = "REJECTED"
        leave.reviewer = request.user
        leave.reviewed_at = timezone.now()
        leave.save(update_fields=["status", "reviewer", "reviewed_at"])
        return Response(LeaveRequestSerializer(leave).data)


class AssetCategoryViewSet(BaseCompanyViewSet):
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer


class AssetViewSet(BaseCompanyViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


class AssetMaintenanceViewSet(BaseCompanyViewSet):
    queryset = AssetMaintenance.objects.all()
    serializer_class = AssetMaintenanceSerializer


class ProductViewSet(BaseCompanyViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class WarehouseViewSet(BaseCompanyViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer


class StockViewSet(BaseCompanyViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        return StockMovement.objects.filter(
            company_id=self.request.user.company_id
        )


class InvoiceViewSet(BaseCompanyViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        return InvoiceItem.objects.filter(
            invoice__company_id=self.request.user.company_id
        )


class PaymentViewSet(BaseCompanyViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update"}:
            return [IsAuthenticated(), IsCompanyUser(), IsAccountant()]
        return [IsAuthenticated(), IsCompanyUser()]


class ExpenseViewSet(BaseCompanyViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update"}:
            return [IsAuthenticated(), IsCompanyUser(), IsAccountant()]
        return [IsAuthenticated(), IsCompanyUser()]


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):
        # API clients cannot choose another recipient.
        serializer.save(recipient=self.request.user, status="UNREAD")

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification = mark_notification_as_read(notification)
        return Response(NotificationSerializer(notification).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        notification = self.get_object()
        notification = archive_notification(notification)
        return Response(NotificationSerializer(notification).data)
