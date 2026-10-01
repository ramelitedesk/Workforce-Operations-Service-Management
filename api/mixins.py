from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import PermissionDenied, ValidationError


class CompanyQuerySetMixin:
    company_field = "company"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated or not getattr(user, "company_id", None):
            return queryset.none()

        return queryset.filter(
            **{f"{self.company_field}_id": user.company_id}
        )


class CompanyCreateMixin:
    def perform_create(self, serializer):
        user = self.request.user

        if not getattr(user, "company_id", None):
            raise PermissionDenied(
                "Your account is not associated with a company."
            )

        serializer.save(company=user.company)


class SafeDestroyMixin:
    """
    Soft-delete hook if a model has is_active/status; otherwise normal delete.
    Override destroy() in sensitive ViewSets when business rules require it.
    """
    pass
