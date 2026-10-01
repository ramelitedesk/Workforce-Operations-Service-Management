from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from .views import (
    CurrentUserAPIView, SecurityTestAPIView,
    CompanyReadOnlyViewSet,
    DepartmentViewSet, EmployeeViewSet, TeamViewSet,
    CustomerViewSet, CustomerContactViewSet, CustomerLocationViewSet,
    ServiceCategoryViewSet, ServiceViewSet, ServiceRequirementViewSet,
    SkillViewSet, EmployeeSkillViewSet, CertificationViewSet,
    EmployeeCertificationViewSet,
    ContractViewSet, ContractServiceViewSet, SLAViewSet,
    TicketViewSet, WorkOrderViewSet,
    WorkScheduleViewSet, EmployeeAvailabilityViewSet,
    AttendanceViewSet, TimeEntryViewSet, LeaveRequestViewSet,
    AssetCategoryViewSet, AssetViewSet, AssetMaintenanceViewSet,
    ProductViewSet, WarehouseViewSet, StockViewSet, StockMovementViewSet,
    InvoiceViewSet, InvoiceItemViewSet, PaymentViewSet, ExpenseViewSet,
    NotificationViewSet,
)

router = DefaultRouter()

router.register("companies", CompanyReadOnlyViewSet, basename="company")
router.register("departments", DepartmentViewSet)
router.register("employees", EmployeeViewSet)
router.register("teams", TeamViewSet)
router.register("customers", CustomerViewSet)
router.register("customer-contacts", CustomerContactViewSet)
router.register("customer-locations", CustomerLocationViewSet)
router.register("service-categories", ServiceCategoryViewSet)
router.register("services", ServiceViewSet)
router.register("service-requirements", ServiceRequirementViewSet)
router.register("skills", SkillViewSet)
router.register("employee-skills", EmployeeSkillViewSet)
router.register("certifications", CertificationViewSet)
router.register("employee-certifications", EmployeeCertificationViewSet)
router.register("contracts", ContractViewSet)
router.register("contract-services", ContractServiceViewSet)
router.register("slas", SLAViewSet)
router.register("tickets", TicketViewSet)
router.register("work-orders", WorkOrderViewSet)
router.register("schedules", WorkScheduleViewSet)
router.register("employee-availability", EmployeeAvailabilityViewSet)
router.register("attendance", AttendanceViewSet)
router.register("time-entries", TimeEntryViewSet)
router.register("leave-requests", LeaveRequestViewSet)
router.register("asset-categories", AssetCategoryViewSet)
router.register("assets", AssetViewSet)
router.register("asset-maintenance", AssetMaintenanceViewSet)
router.register("inventory/products", ProductViewSet, basename="product")
router.register("inventory/warehouses", WarehouseViewSet, basename="warehouse")
router.register("inventory/stock", StockViewSet, basename="stock")
router.register("inventory/movements", StockMovementViewSet, basename="stock-movement")
router.register("invoices", InvoiceViewSet)
router.register("invoice-items", InvoiceItemViewSet)
router.register("payments", PaymentViewSet)
router.register("expenses", ExpenseViewSet)
router.register("notifications", NotificationViewSet)

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("auth/me/", CurrentUserAPIView.as_view(), name="current_user"),
    path("security/test/", SecurityTestAPIView.as_view(), name="security_test"),
    path("", include(router.urls)),
]
