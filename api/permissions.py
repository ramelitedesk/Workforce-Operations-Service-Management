from rest_framework.permissions import BasePermission


class IsCompanyUser(BasePermission):
    message = "A company assignment is required to access this resource."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "company_id", None)
        )


class IsCompanyObject(BasePermission):
    message = "You do not have access to this company resource."

    def has_object_permission(self, request, view, obj):
        user_company_id = getattr(request.user, "company_id", None)
        object_company_id = getattr(obj, "company_id", None)
        return (
            user_company_id is not None
            and object_company_id is not None
            and user_company_id == object_company_id
        )


class HasAnyRole(BasePermission):
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        allowed_roles = getattr(view, "allowed_roles", set())
        return getattr(request.user, "role", None) in allowed_roles


class IsCompanyAdmin(BasePermission):
    message = "Company administrator permission required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in {"SUPER_ADMIN", "COMPANY_ADMIN"}
        )


class IsOperationsManager(BasePermission):
    message = "Operations manager permission required."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {
            "SUPER_ADMIN", "COMPANY_ADMIN", "OPERATIONS_MANAGER"
        }


class IsServiceManager(BasePermission):
    message = "Service manager permission required."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {
            "SUPER_ADMIN", "COMPANY_ADMIN", "SERVICE_MANAGER"
        }


class IsDispatcher(BasePermission):
    message = "Dispatcher permission required."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {
            "SUPER_ADMIN", "COMPANY_ADMIN", "OPERATIONS_MANAGER", "DISPATCHER"
        }


class IsAccountant(BasePermission):
    message = "Accountant permission required."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {
            "SUPER_ADMIN", "COMPANY_ADMIN", "ACCOUNTANT"
        }
