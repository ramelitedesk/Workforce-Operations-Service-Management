from django.contrib import admin

from .models import Contract, ContractService, SLA


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "contract_number",
        "name",
        "company",
        "customer",
        "start_date",
        "end_date",
        "status",
        "contract_value",
        "auto_renew",
    )

    list_filter = (
        "company",
        "status",
        "auto_renew",
    )

    search_fields = (
        "contract_number",
        "name",
        "customer__name",
        "company__name",
    )

    ordering = (
        "company",
        "contract_number",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Contract Information",
            {
                "fields": (
                    "company",
                    "customer",
                    "contract_number",
                    "name",
                    "description",
                    "status",
                )
            },
        ),
        (
            "Contract Period & Value",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "contract_value",
                    "auto_renew",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "notes",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(ContractService)
class ContractServiceAdmin(admin.ModelAdmin):
    list_display = (
        "contract",
        "service",
        "agreed_price",
        "included_quantity",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "contract__company",
    )

    search_fields = (
        "contract__contract_number",
        "contract__name",
        "service__code",
        "service__name",
    )

    ordering = (
        "contract",
        "service",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "contract",
        "priority",
        "response_time_minutes",
        "resolution_time_minutes",
        "is_active",
    )

    list_filter = (
        "priority",
        "is_active",
        "contract__company",
    )

    search_fields = (
        "name",
        "contract__contract_number",
        "contract__name",
    )

    ordering = (
        "contract",
        "priority",
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "SLA Information",
            {
                "fields": (
                    "contract",
                    "name",
                    "description",
                    "priority",
                )
            },
        ),
        (
            "SLA Targets",
            {
                "fields": (
                    "response_time_minutes",
                    "resolution_time_minutes",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_active",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )