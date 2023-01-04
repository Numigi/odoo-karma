# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytz
from datetime import datetime
from functools import partial

from odoo import api, fields, models, _
from odoo.addons.base.models.ir_model import FIELD_TYPES
from odoo.exceptions import UserError
from .tools import get_technical_field_name


class BaseWithRangeFieldComputing(models.AbstractModel):
    """Enable computing fields from range on any Odoo model."""

    _inherit = 'base'

    def compute_date_range_field(
        self, field_reference, range_reference, related_model_name=None,
    ):
        """Compute a field given a field template reference and a date range reference.

        :param field_reference: the reference of the field template
        :param range_reference: the date range reference (i.e. last_30_days)
        :param str related_model_name: the name of the related model
        """
        func = self.__get_date_range_computing_function(field_reference)

        field_name = get_technical_field_name(
            field_reference, range_reference, related_model_name=related_model_name)

        range_ = self.__get_range(range_reference)
        date_from = range_.get_date_min()
        date_to = range_.get_date_max()

        partial_func = partial(func, self, field_name, date_from, date_to)
        return partial_func(related_model_name) if related_model_name else partial_func()

    def __get_date_range_computing_function(self, field_reference):
        if field_reference not in self._date_range_fields:
            raise UserError(_(
                'No field template function found with the reference {reference}.'
            ).format(reference=field_reference))

        return self._date_range_fields[field_reference]

    def __get_range(self, range_reference):
        range_ = self.env['computed.field.date.range'].search([
            ('reference', '=', range_reference),
        ])

        if not range_:
            raise UserError(_(
                'No date range found with the reference {reference}.'
            ).format(reference=range_reference))

        return range_

    @classmethod
    def _register_date_range_field(cls, reference, func):
        """Register a date range field template for the model.

        :param reference: the reference of the field template
        :param func: the field template function
        """
        if not hasattr(cls, '_date_range_fields'):
            cls._date_range_fields = {}
        cls._date_range_fields[reference] = func
