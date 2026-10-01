from django.utils import timezone

from workforce.models import Employee
from .models import Service


def get_eligible_employees(service):
    """
    Return active employees belonging to the service's company
    who satisfy all required service requirements.
    """

    employees = Employee.objects.filter(
        company=service.company,
        status="ACTIVE",
    ).select_related(
        "user",
        "company",
    )

    required_requirements = service.requirements.filter(
        is_required=True
    ).select_related(
        "skill",
        "certification",
    )

    today = timezone.localdate()

    eligible_employees = []

    for employee in employees:

        employee_is_eligible = True

        for requirement in required_requirements:

            # ---------------------------------
            # Skill requirement
            # ---------------------------------
            if requirement.requirement_type == "SKILL":

                employee_skill = employee.skills.filter(
                    skill=requirement.skill
                ).first()

                if not employee_skill:
                    employee_is_eligible = False
                    break

                if requirement.minimum_proficiency:
                    if (
                        employee_skill.proficiency
                        < requirement.minimum_proficiency
                    ):
                        employee_is_eligible = False
                        break

            # ---------------------------------
            # Certification requirement
            # ---------------------------------
            elif requirement.requirement_type == "CERTIFICATION":

                employee_certification = (
                    employee.certifications
                    .filter(
                        certification=requirement.certification,
                        issue_date__lte=today,
                    )
                    .order_by("-expiry_date")
                    .first()
                )

                if not employee_certification:
                    employee_is_eligible = False
                    break

                # Certification with an expiry date
                if employee_certification.expiry_date:
                    if employee_certification.expiry_date < today:
                        employee_is_eligible = False
                        break

        if employee_is_eligible:
            eligible_employees.append(employee)

    return eligible_employees