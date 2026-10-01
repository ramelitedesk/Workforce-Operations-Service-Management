from django.contrib import admin

from .models import (
    Invoice,
    InvoiceItem,
    Payment,
    Expense,
)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = (
        "created_at",
        "line_subtotal_display",
        "tax_amount_display",
        "line_total_display",
    )

    fields = (
        "description",
        "quantity",
        "unit_price",
        "tax_rate",
        "discount_amount",
        "line_subtotal_display",
        "tax_amount_display",
        "line_total_display",
        "created_at",
    )

    def line_subtotal_display(self, obj):
        return obj.line_subtotal

    line_subtotal_display.short_description = "Subtotal"

    def tax_amount_display(self, obj):
        return obj.tax_amount

    tax_amount_display.short_description = "Tax"

    def line_total_display(self, obj):
        return obj.line_total

    line_total_display.short_description = "Total"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = (
        "invoice_number",
        "customer",
        "invoice_date",
        "due_date",
        "status",
        "total_amount",
        "amount_paid",
        "balance_due_display",
    )

    list_filter = (
        "company",
        "status",
        "invoice_date",
        "due_date",
    )

    search_fields = (
        "invoice_number",
        "customer__name",
        "customer__customer_code",
        "work_order__work_order_number",
    )

    ordering = (
        "-invoice_date",
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "balance_due_display",
    )

    inlines = [
        InvoiceItemInline,
    ]

    fieldsets = (
        (
            "Invoice",
            {
                "fields": (
                    "company",
                    "customer",
                    "work_order",
                    "invoice_number",
                    "invoice_date",
                    "due_date",
                    "status",
                )
            },
        ),
        (
            "Amounts",
            {
                "fields": (
                    "subtotal",
                    "tax_amount",
                    "discount_amount",
                    "total_amount",
                    "amount_paid",
                    "balance_due_display",
                )
            },
        ),
        (
            "Notes",
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

    def balance_due_display(self, obj):
        return obj.balance_due

    balance_due_display.short_description = "Balance Due"


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):

    list_display = (
        "invoice",
        "description",
        "quantity",
        "unit_price",
        "tax_rate",
        "discount_amount",
        "line_total_display",
    )

    search_fields = (
        "invoice__invoice_number",
        "description",
    )

    readonly_fields = (
        "created_at",
    )

    def line_total_display(self, obj):
        return obj.line_total

    line_total_display.short_description = "Line Total"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "invoice",
        "company",
        "amount",
        "payment_date",
        "payment_method",
        "status",
        "reference_number",
        "recorded_by",
    )

    list_filter = (
        "company",
        "status",
        "payment_method",
        "payment_date",
    )

    search_fields = (
        "invoice__invoice_number",
        "invoice__customer__name",
        "reference_number",
    )

    ordering = (
        "-payment_date",
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):

    list_display = (
        "description",
        "company",
        "work_order",
        "amount",
        "expense_date",
        "status",
        "created_by",
    )

    list_filter = (
        "company",
        "status",
        "expense_date",
    )

    search_fields = (
        "description",
        "work_order__work_order_number",
        "notes",
    )

    ordering = (
        "-expense_date",
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )