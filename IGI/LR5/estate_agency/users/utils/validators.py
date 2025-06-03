from datetime import date
from django.utils.translation import gettext_lazy as _

from django.core.validators import BaseValidator


class RestrictedAgeValidator(BaseValidator):
    message = _("Ensure that date is older than %(limit_value)s")
    code = "restricted_age"

    def compare(self, birth_date, limit_value):
        if not isinstance(birth_date, date):
            raise TypeError("Birth_date must be a date")
        today = date.today()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )
        return age < limit_value
