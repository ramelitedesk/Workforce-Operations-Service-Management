from django.contrib.auth import get_user_model
from rest_framework import serializers

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

User = get_user_model()


class CompanyReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = "__all__"


class CurrentUserSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name",
            "phone", "role", "company", "is_active", "date_joined"
        ]
        read_only_fields = fields

    def get_company(self, obj):
        if not obj.company:
            return None
        return {"id": obj.company_id, "name": obj.company.name}


class CompanyScopedModelSerializer(serializers.ModelSerializer):
    """
    Secure default for company-owned resources:
    - company is never accepted from the client
    - company is read-only in responses
    - every FK to another company-owned object is checked when possible
    """

    class Meta:
        fields = "__all__"
        read_only_fields = ("company", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        company_id = getattr(getattr(request, "user", None), "company_id", None)

        if not company_id:
            raise serializers.ValidationError(
                {"company": "Authenticated user must belong to a company."}
            )

        for field_name, value in attrs.items():
            if value is None:
                continue

            model_field = self.Meta.model._meta.get_field(field_name)

            if not getattr(model_field, "many_to_one", False):
                continue

            related_company_id = getattr(value, "company_id", None)

            if related_company_id is not None and related_company_id != company_id:
                raise serializers.ValidationError(
                    {field_name: "Referenced object belongs to another company."}
                )

        return attrs


def make_company_serializer(model):
    return type(
        f"{model.__name__}Serializer",
        (CompanyScopedModelSerializer,),
        {
            "Meta": type(
                "Meta",
                (),
                {
                    "model": model,
                    "fields": "__all__",
                    "read_only_fields": (
                        "id", "company", "created_at", "updated_at"
                    ),
                },
            )
        },
    )


class DepartmentSerializer(make_company_serializer(Department)):
    pass


class EmployeeSerializer(make_company_serializer(Employee)):
    pass


class TeamSerializer(make_company_serializer(Team)):
    pass


class CustomerSerializer(make_company_serializer(Customer)):
    pass


class CustomerContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerContact
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CustomerLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerLocation
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ServiceCategorySerializer(make_company_serializer(ServiceCategory)):
    pass


class ServiceSerializer(make_company_serializer(Service)):
    pass


class ServiceRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequirement
        fields = "__all__"
        read_only_fields = ("id",)


class SkillSerializer(make_company_serializer(Skill)):
    pass


class EmployeeSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSkill
        fields = "__all__"
        read_only_fields = ("id",)


class CertificationSerializer(make_company_serializer(Certification)):
    pass


class EmployeeCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeCertification
        fields = "__all__"
        read_only_fields = ("id",)


class ContractSerializer(make_company_serializer(Contract)):
    pass


class ContractServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractService
        fields = "__all__"
        read_only_fields = ("id",)


class SLASerializer(make_company_serializer(SLA)):
    pass


class TicketSerializer(make_company_serializer(Ticket)):
    pass


class WorkOrderSerializer(make_company_serializer(WorkOrder)):
    pass


class WorkScheduleSerializer(make_company_serializer(WorkSchedule)):
    pass


class EmployeeAvailabilitySerializer(make_company_serializer(EmployeeAvailability)):
    pass


class AttendanceSerializer(make_company_serializer(Attendance)):
    pass


class TimeEntrySerializer(make_company_serializer(TimeEntry)):
    pass


class LeaveRequestSerializer(make_company_serializer(LeaveRequest)):
    pass


class AssetCategorySerializer(make_company_serializer(AssetCategory)):
    pass


class AssetSerializer(make_company_serializer(Asset)):
    pass


class AssetMaintenanceSerializer(make_company_serializer(AssetMaintenance)):
    pass


class ProductSerializer(make_company_serializer(Product)):
    pass


class WarehouseSerializer(make_company_serializer(Warehouse)):
    pass


class StockSerializer(make_company_serializer(Stock)):
    pass


class StockMovementSerializer(make_company_serializer(StockMovement)):
    pass


class InvoiceSerializer(make_company_serializer(Invoice)):
    pass


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = "__all__"
        read_only_fields = ("id",)


class PaymentSerializer(make_company_serializer(Payment)):
    pass


class ExpenseSerializer(make_company_serializer(Expense)):
    pass


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = (
            "id", "recipient", "status", "read_at",
            "created_at", "updated_at"
        )
