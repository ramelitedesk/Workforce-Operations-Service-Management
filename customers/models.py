from django.db import models

from organizations.models import Company


class CustomerType(models.TextChoices):
    INDIVIDUAL = "INDIVIDUAL", "Individual"
    BUSINESS = "BUSINESS", "Business"


class CustomerStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    SUSPENDED = "SUSPENDED", "Suspended"


class Customer(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="customers",
    )

    customer_code = models.CharField(
        max_length=50,
    )

    customer_type = models.CharField(
        max_length=20,
        choices=CustomerType.choices,
        default=CustomerType.BUSINESS,
    )

    name = models.CharField(
        max_length=200,
    )

    legal_name = models.CharField(
        max_length=250,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    tax_number = models.CharField(
        max_length=100,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=CustomerStatus.choices,
        default=CustomerStatus.ACTIVE,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["company", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "customer_code"],
                name="unique_customer_code_per_company",
            )
        ]

    def __str__(self):
        return f"{self.customer_code} - {self.name}"


class CustomerContact(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="contacts",
    )

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
        blank=True,
    )

    designation = models.CharField(
        max_length=150,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    is_primary = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["customer", "first_name", "last_name"]

    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return f"{name} - {self.customer.name}"


class LocationType(models.TextChoices):
    HEAD_OFFICE = "HEAD_OFFICE", "Head Office"
    BRANCH = "BRANCH", "Branch"
    SERVICE_SITE = "SERVICE_SITE", "Service Site"
    BILLING = "BILLING", "Billing Address"
    SHIPPING = "SHIPPING", "Shipping Address"


class CustomerLocation(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="locations",
    )

    name = models.CharField(
        max_length=150,
    )

    location_type = models.CharField(
        max_length=30,
        choices=LocationType.choices,
        default=LocationType.SERVICE_SITE,
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100,
    )

    state = models.CharField(
        max_length=100,
    )

    country = models.CharField(
        max_length=100,
        default="India",
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    contact_name = models.CharField(
        max_length=150,
        blank=True,
    )

    contact_phone = models.CharField(
        max_length=20,
        blank=True,
    )

    is_primary = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["customer", "name"]

    def __str__(self):
        return f"{self.customer.name} - {self.name}"