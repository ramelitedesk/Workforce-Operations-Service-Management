# Workforce Operations & Service Management Platform

A full-stack, enterprise-style workforce and service management platform built with **Django, Django REST Framework, PostgreSQL, Celery, Redis, Docker, and Gunicorn**.

The platform manages the complete operational lifecycle:

**Create → Assign → Schedule → Execute → Track → Verify → Close → Report**

It is designed around real-world business workflows including workforce management, customers, service operations, work orders, scheduling, attendance, leave, inventory, assets, billing, notifications, reporting, and auditability.

---

## 🚀 Key Features

### Workforce Management
- Employee management
- Departments and teams
- Employee skills and certifications
- Role-based access control
- Employee eligibility validation
- Workforce assignment workflows

### Customer & Service Management
- Customer management
- Customer contacts and locations
- Service categories
- Service catalog
- Service requirements
- Contract management
- SLA management

### Ticket & Work Order Management
- Ticket lifecycle management
- Work order creation and tracking
- Priority and status management
- Employee assignment
- Eligibility validation
- Work order status transitions
- Operational workflow tracking

### Scheduling & Attendance
- Employee availability
- Work scheduling
- Schedule conflict detection
- Attendance management
- Time entries
- Leave management
- Leave overlap and validation rules

### Assets & Inventory
- Asset management
- Asset categories
- Asset maintenance
- Product management
- Warehouse management
- Stock management
- Stock movements
- Inventory transfers
- Atomic inventory operations

### Billing & Payments
- Invoice management
- Invoice items
- Tax and discount calculations
- Payment tracking
- Partial payments
- Payment validation
- Invoice status updates
- Expense management

### Notifications & Background Processing
- Application notifications
- Read/unread notification management
- Background task processing
- Celery workers
- Celery Beat scheduled tasks
- Redis message broker

### Reporting & Dashboard
- Operational dashboard
- Workforce statistics
- Work order monitoring
- Operational reports
- Role-based dashboard access

### REST API & Security
- Django REST Framework
- JWT authentication
- Access and refresh tokens
- Role-based API permissions
- Company-level data isolation
- Multi-tenant architecture
- API throttling
- Authenticated API endpoints

### Testing
- Django automated test framework
- API test suite
- Authentication tests
- JWT tests
- Permission tests
- Company data isolation tests
- WorkOrder API tests

**20 automated API tests — 20/20 passing**

### DevOps & Deployment
- Dockerized application
- Docker Compose
- PostgreSQL container
- Redis container
- Celery worker container
- Celery Beat container
- Gunicorn application server
- Environment-based configuration
- Docker health checks
- Persistent Docker volumes

---

# 🖥️ Application Screenshots

## Dashboard

The operational dashboard provides a centralized view of workforce and service-management activities.

> Add your dashboard screenshot here.

<img width="1915" height="987" alt="image" src="https://github.com/user-attachments/assets/7257e257-6974-419e-a8ad-c404bbc94381" />

<img width="1894" height="985" alt="image" src="https://github.com/user-attachments/assets/b00106a3-2c12-44a6-b610-95a57dfb7c4d" />


---

## Django Admin

The Django Admin interface provides centralized management of application data and business entities.

> Add your Django Admin screenshot here.

<img width="1920" height="1038" alt="image" src="https://github.com/user-attachments/assets/8ca7caad-2459-4ea0-924a-7f0647aa699a" />


---

## REST API & JWT Authentication

The platform exposes authenticated REST APIs using Django REST Framework and JWT authentication.

> Add your Postman/API screenshot here.

<img width="1895" height="992" alt="image" src="https://github.com/user-attachments/assets/ef0f6ec7-bb37-4a70-af5b-a0faa8a02583" />


---

## Dockerized Architecture

The application runs as a multi-container environment using Docker Compose.

Services include:

- Django + Gunicorn
- PostgreSQL
- Redis
- Celery Worker
- Celery Beat

> Add your Docker Desktop screenshot here.

<img width="1891" height="1015" alt="image" src="https://github.com/user-attachments/assets/2870405c-c505-4a05-9b03-7881728a7d39" />


---

## Work Order Management

Work orders form the core operational workflow of the platform, connecting customers, services, employees, schedules, and execution status.

> Add your Work Order screenshot here.

<img width="1920" height="3538" alt="image" src="https://github.com/user-attachments/assets/904938ff-393f-4479-ba35-7ed7e03b2395" />


---

## Automated Tests

The API test suite verifies authentication, permissions, company-level data isolation, and WorkOrder API behavior.

```text
Found 20 test(s).
....................
Ran 20 tests
OK

<img width="1906" height="989" alt="image" src="https://github.com/user-attachments/assets/f7841c28-c829-4eda-8a65-303ad0cbe469" />
