# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import abc

from datetime import date
from typing import Iterable


class FieldTemplate(metaclass=abc.ABCMeta):

    def compute(
        self, records: Iterable[object], fieldName: str,
        date_from: date, date_to: date
    ):
        """Compute the field value for the given records and date interval.

        The given date_from and date_to parameters are expected to be UTC dates
        expressed in the user's timezone.

        :param records: the records for which to compute the field
        :param fieldName: the name of the attribute that will contain the field value
        :param date_form: the minimum date of the interval
        :param date_to: the maximum date of the interval
        """
        raise NotImplementedError()
