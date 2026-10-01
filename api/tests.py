from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from organizations.models import Company
from inventory.models import Product
from workforce.models import Employee


class AuthenticationAPITests(APITestCase):

    def setUp(self):
        self.password = "TestPassword123!"

        self.user = User.objects.create_user(
            email="apitest@example.com",
            password=self.password,
            first_name="API",
            last_name="Tester",
        )

    def test_jwt_login_success(self):
        response = self.client.post(
            "/api/auth/token/",
            {
                "email": "apitest@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_jwt_login_invalid_password(self):
        response = self.client.post(
            "/api/auth/token/",
            {
                "email": "apitest@example.com",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_current_user_requires_authentication(self):
        response = self.client.get("/api/auth/me/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_current_user_authenticated(self):
        response = self.client.post(
            "/api/auth/token/",
            {
                "email": "apitest@example.com",
                "password": self.password,
            },
            format="json",
        )

        access_token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get("/api/auth/me/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["email"],
            "apitest@example.com",
        )





class CompanyIsolationAPITests(APITestCase):

    def setUp(self):
        self.password = "TestPassword123!"

        self.company_a = Company.objects.create(
            name="Company A",
        )

        self.company_b = Company.objects.create(
            name="Company B",
        )

        self.user_a = User.objects.create_user(
            email="companya@example.com",
            password=self.password,
            first_name="Company",
            last_name="A User",
            company=self.company_a,
            role="COMPANY_ADMIN",
        )

        self.product_a = Product.objects.create(
            company=self.company_a,
            sku="PROD-A-001",
            name="Company A Product",
            unit="PCS",
            minimum_stock=10,
            reorder_level=5,
            unit_cost=100,
        )

        self.product_b = Product.objects.create(
            company=self.company_b,
            sku="PROD-B-001",
            name="Company B Product",
            unit="PCS",
            minimum_stock=10,
            reorder_level=5,
            unit_cost=200,
        )

        response = self.client.post(
            "/api/auth/token/",
            {
                "email": "companya@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.access_token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

    def test_user_only_sees_own_company_products(self):
        response = self.client.get(
            "/api/inventory/products/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data

        product_ids = [
            product["id"]
            for product in results
        ]

        self.assertIn(
            self.product_a.id,
            product_ids,
        )

        self.assertNotIn(
            self.product_b.id,
            product_ids,
        )

    def test_user_cannot_access_other_company_product(self):
        response = self.client.get(
            f"/api/inventory/products/{self.product_b.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_company_is_derived_from_authenticated_user(self):
        response = self.client.post(
            "/api/inventory/products/",
            {
                "company": self.company_b.id,
                "sku": "PROD-A-002",
                "name": "Attempted Cross Company Product",
                "unit": "PCS",
                "minimum_stock": 10,
                "reorder_level": 5,
                "unit_cost": 150,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        created_product = Product.objects.get(
            sku="PROD-A-002"
        )

        self.assertEqual(
            created_product.company_id,
            self.company_a.id,
        )

        self.assertNotEqual(
            created_product.company_id,
            self.company_b.id,
        )        


class RolePermissionAPITests(APITestCase):

    def setUp(self):
        self.password = "TestPassword123!"

        self.company = Company.objects.create(
            name="Permission Test Company",
        )

        self.company_admin = User.objects.create_user(
            email="admin@example.com",
            password=self.password,
            first_name="Company",
            last_name="Admin",
            company=self.company,
            role="COMPANY_ADMIN",
        )

        self.employee_user = User.objects.create_user(
            email="employee@example.com",
            password=self.password,
            first_name="Regular",
            last_name="Employee",
            company=self.company,
            role="EMPLOYEE",
        )

    def get_access_token(self, email):
        response = self.client.post(
            "/api/auth/token/",
            {
                "email": email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        return response.data["access"]

    def test_company_admin_can_access_employee_endpoint(self):
        access_token = self.get_access_token(
            "admin@example.com"
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get(
            "/api/employees/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_regular_employee_cannot_create_employee(self):
        access_token = self.get_access_token(
            "employee@example.com"
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.post(
            "/api/employees/",
            {
                "employee_id": "EMP-TEST-001",
                "designation": "Technician",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )        

class WorkOrderAPITests(APITestCase):

    def setUp(self):
        self.password = "TestPassword123!"

        self.company = Company.objects.create(
            name="Work Order Test Company",
        )

        self.user = User.objects.create_user(
            email="workorder@example.com",
            password=self.password,
            first_name="Work",
            last_name="Order User",
            company=self.company,
            role="COMPANY_ADMIN",
        )

        response = self.client.post(
            "/api/auth/token/",
        {
              "email": "workorder@example.com",
            "password": self.password,
        },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def test_work_orders_endpoint_is_accessible(self):
        response = self.client.get(
            "/api/work-orders/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )


    def test_work_order_endpoint_does_not_require_pk_for_list(self):
        response = self.client.get(
            "/api/work-orders/"
        )

        self.assertNotEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )



class NotificationAPITests(APITestCase):

    def setUp(self):
        self.password = "TestPassword123!"

        self.company = Company.objects.create(
            name="Notification Test Company",
        )

        self.user = User.objects.create_user(
            email="notification@example.com",
            password=self.password,
            first_name="Notification",
            last_name="Tester",
            company=self.company,
            role="EMPLOYEE",
        )

        response = self.client.post(
            "/api/auth/token/",
            {
                "email": "notification@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def test_notification_endpoint_is_accessible(self):
        response = self.client.get(
            "/api/notifications/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_notification_can_be_created(self):
        response = self.client.post(
            "/api/notifications/",
            {
                "title": "Test Notification",
                "message": "Automated API test notification.",
                "notification_type": "INFO",
                "channel": "IN_APP",
                "priority": "NORMAL",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["title"],
            "Test Notification",
        )



class InventoryAPITests(APITestCase):

    def setUp(self):
        self.password = "TestPassword123!"

        self.company = Company.objects.create(
            name="Inventory Test Company",
        )

        self.user = User.objects.create_user(
            email="inventory@example.com",
            password=self.password,
            first_name="Inventory",
            last_name="Tester",
            company=self.company,
            role="COMPANY_ADMIN",
        )

        response = self.client.post(
            "/api/auth/token/",
            {
                "email": "inventory@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def test_products_endpoint_is_accessible(self):
        response = self.client.get(
            "/api/inventory/products/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_product_can_be_created(self):
        response = self.client.post(
            "/api/inventory/products/",
            {
                "sku": "AUTO-TEST-001",
                "name": "Automated Test Product",
                "unit": "PCS",
                "status": "ACTIVE",
                "minimum_stock": 10,
                "reorder_level": 5,
                "unit_cost": 100,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["sku"],
            "AUTO-TEST-001",
        )


class EmployeeAPITests(APITestCase):

    def setUp(self):
        self.password = "TestPassword123!"

        self.company = Company.objects.create(
            name="Employee Test Company",
        )

        self.user = User.objects.create_user(
            email="employeeapi@example.com",
            password=self.password,
            first_name="Employee",
            last_name="API Tester",
            company=self.company,
            role="COMPANY_ADMIN",
        )

        response = self.client.post(
            "/api/auth/token/",
            {
                "email": "employeeapi@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def test_employees_endpoint_is_accessible(self):
        response = self.client.get(
            "/api/employees/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )



class TicketAPITests(APITestCase):

    def setUp(self):
        self.password = "TestPassword123!"

        self.company = Company.objects.create(
            name="Ticket Test Company",
        )

        self.user = User.objects.create_user(
            email="ticketapi@example.com",
            password=self.password,
            first_name="Ticket",
            last_name="Tester",
            company=self.company,
            role="COMPANY_ADMIN",
        )

        response = self.client.post(
            "/api/auth/token/",
            {
                "email": "ticketapi@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def test_tickets_endpoint_is_accessible(self):
        response = self.client.get(
            "/api/tickets/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )



class BillingAPITests(APITestCase):

    def setUp(self):
        self.password = "TestPassword123!"

        self.company = Company.objects.create(
            name="Billing Test Company",
        )

        self.user = User.objects.create_user(
            email="billingapi@example.com",
            password=self.password,
            first_name="Billing",
            last_name="Tester",
            company=self.company,
            role="ACCOUNTANT",
        )

        response = self.client.post(
            "/api/auth/token/",
            {
                "email": "billingapi@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def test_invoices_endpoint_is_accessible(self):
        response = self.client.get(
            "/api/invoices/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_payments_endpoint_is_accessible(self):
        response = self.client.get(
            "/api/payments/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_expenses_endpoint_is_accessible(self):
        response = self.client.get(
            "/api/expenses/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )


def test_jwt_refresh_token(self):
    response = self.client.post(
        "/api/auth/token/",
        {
            "email": "apitest@example.com",
            "password": self.password,
        },
        format="json",
    )

    self.assertEqual(
        response.status_code,
        status.HTTP_200_OK,
    )

    refresh_token = response.data["refresh"]

    response = self.client.post(
        "/api/auth/token/refresh/",
        {
            "refresh": refresh_token,
        },
        format="json",
    )

    self.assertEqual(
        response.status_code,
        status.HTTP_200_OK,
    )

    self.assertIn(
        "access",
        response.data,
    )                                                        