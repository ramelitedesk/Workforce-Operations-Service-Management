Workforce Operations & Service Management Platform

A Django-based enterprise workforce and field-service management platform designed to manage the complete operational lifecycle:

Create → Assign → Schedule → Execute → Track → Verify → Close → Report

The platform brings workforce management, customers, service operations, work orders, scheduling, attendance, assets, inventory, billing, notifications, reporting, and REST APIs into a single system.

Project Highlights

Custom email-based authentication and role-based access

Company-aware multi-tenant data isolation

Workforce, employees, departments, teams, skills, and certifications

Customer, contact, and service-location management

Services, service requirements, contracts, and SLAs

Ticket and work-order lifecycle management

Employee eligibility and assignment engine

Schedule and availability conflict validation

Attendance, time entries, and leave management

Asset and maintenance tracking

Inventory, stock movements, and warehouse management

Invoicing, payments, and expenses

In-app notifications

Celery + Redis background processing

Operational dashboard and reporting

REST API secured with JWT authentication

API throttling and company/role-based permissions

Automated API/security regression tests

Dockerized PostgreSQL, Redis, Django/Gunicorn, Celery Worker, and Celery Beat

Technology Stack

Layer

Technology

Backend

Django 6.1

API

Django REST Framework

Authentication

Django Auth + Simple JWT

Database

PostgreSQL 16

Background Jobs

Celery

Message Broker / Cache

Redis 7

Web Server

Gunicorn

Containers

Docker + Docker Compose

Frontend

Django templates / Bootstrap

Testing

Django Test Framework

Version Control

Git + GitHub

Core Modules

Accounts & Organizations

Custom user model with email-based login

Role-based access control

Company/organization management

Workforce

Departments

Employees

Teams

Skills

Certifications

Employee skill/certification records

Customers & Services

Customers

Customer contacts

Service locations

Service categories

Services

Service requirements

Contracts

SLAs

Service Operations

Tickets

Work orders

Assignment engine

Scheduling

Employee availability

Attendance

Time entries

Leave requests

Assets & Inventory

Asset categories

Asset tracking

Maintenance records

Products

Warehouses

Stock

Stock movements

Stock transfers

Billing & Notifications

Invoices

Invoice items

Payments

Expenses

In-app notifications

Notification processing through Celery

Reports & Dashboard

Operational dashboard

Workforce metrics

Ticket and work-order metrics

Attendance metrics

Invoice/revenue metrics

Low-stock monitoring

Operational alerts

Recent activity

REST API

The project includes a JWT-secured REST API with:

Authenticated API access

JWT access/refresh tokens

Company-level data isolation

Role-based permissions

Request throttling

Work-order endpoints and actions

Automated API/security regression tests

Architecture

Client / Browser
       |
       v
Django / Gunicorn
       |
       +--------------------+
       |                    |
       v                    v
PostgreSQL              Redis
       |                    |
       |              +-----+-----+
       |              |           |
       |              v           v
       |           Celery      Celery Beat
       |           Worker
       |
       v
Django Applications
       |
       +-- Accounts
       +-- Organizations
       +-- Workforce
       +-- Customers
       +-- Services
       +-- Contracts
       +-- Tickets
       +-- Work Orders
       +-- Scheduling
       +-- Attendance
       +-- Leave
       +-- Assignment
       +-- Assets
       +-- Inventory
       +-- Billing
       +-- Notifications
       +-- Reports
       +-- API

Business Workflow

Customer / Internal Request
          ↓
        Ticket
          ↓
      Work Order
          ↓
 Employee Eligibility
          ↓
    Assignment
          ↓
      Scheduling
          ↓
     Dispatch / Visit
          ↓
   Work Execution
          ↓
 Completion / Verification
          ↓
       Billing
          ↓
       Reporting

Docker Setup

The project is containerized for a consistent development environment.

Services:

web — Django application served by Gunicorn

db — PostgreSQL

redis — Redis

celery — Celery worker

celery-beat — scheduled Celery tasks

Start the project

Create a local .env file with the required environment variables, then run:

docker compose up -d --build

Apply migrations:

docker compose exec web python manage.py migrate

Collect static files:

docker compose exec web python manage.py collectstatic --noinput

Check container status:

docker compose ps

The Django application is available at:

http://127.0.0.1:8000/

Django Admin:

http://127.0.0.1:8000/admin/

Environment Variables

Sensitive configuration is kept outside source control in .env.

Example structure:

DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=workforce_db
DB_USER=postgres
DB_PASSWORD=your-database-password
DB_HOST=db
DB_PORT=5432
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

Never commit .env or production secrets to GitHub.

Testing

The API/security test suite currently contains 20 automated tests, covering areas including:

JWT authentication

Invalid authentication

Authenticated user access

Company isolation

Role-based permissions

JWT refresh

Work-order API access/regression

Run the API tests with:

docker compose exec web python manage.py test api

Expected result:

Ran 20 tests
OK

Additional project checks:

docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run

Project Status

The current implementation includes the core backend, operational modules, dashboard/reporting, REST API, Celery/Redis automation, Docker environment, and automated API/security tests.

The React frontend is intentionally planned as a future phase rather than part of the current implementation.

Future Enhancements

Potential future phases include:

React frontend

Advanced reporting and analytics

Mobile application

Maps/GPS integration

Push/SMS notification integrations

S3-compatible file storage

Expanded automated test coverage

Production deployment with Nginx and HTTPS

Advanced scheduling and optimization

Security Notes

.env is excluded from version control.

JWT authentication is used for the REST API.

API requests use authentication and throttling.

Company-aware permissions are implemented for API access.

Sensitive configuration is supplied through environment variables.

Author

Ramakrushna

GitHub: https://github.com/ramelitedesk

This project was built as a portfolio-focused enterprise Django application demonstrating backend architecture, business workflows, API development, database design, background processing, Dockerization, and automated testing.
