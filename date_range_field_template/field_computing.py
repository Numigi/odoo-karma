# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytz
from datetime import datetime

from odoo import api, fields, models
from odoo.addons.base.ir.ir_model import FIELD_TYPES
from odoo.exceptions import UserError
from .field_template import FieldTemplate
from .tools import get_technical_field_name


class BaseWithRangeFieldComputing(models.AbstractModel):
    """Enable computing fields from range on any Odoo model."""

    _inherit = 'base'

    @api.multi
    def compute_date_range_field(self, field_reference: str, range_reference: str):
        """Compute a field given a field template reference and a date range reference.

        :param field_reference: the reference of the field template
        :param range_reference: the date range reference (i.e. last_30_days)
        """
        template = self.__get_template(field_reference)

        field_name = get_technical_field_name(field_reference, range_reference)

        range_ = self.__get_range(range_reference)
        date_from = range_.get_date_min()
        date_to = range_.get_date_max()

        return template.compute(self, field_name, date_from, date_to)

    def __get_template(self, field_reference):
        if field_reference not in self._date_range_fields:
            raise UserError(_(
                'No field template found with the reference {reference}.'
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

    @api.model_cr
    def _register_hook(self):
        super()._register_hook()
        self.__class__._date_range_fields = {}

    @classmethod
    def _register_date_range_field(cls, reference: str, template: FieldTemplate):
        """Register a date range field template for the model.

        :param reference: the reference of the field template
        :param template: the field template
        """
        cls._date_range_fields[reference] = template
