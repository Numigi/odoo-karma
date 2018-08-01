# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import abc

from datetime import date
from odoo import api, fields, models
from odoo.addons.base.ir.ir_model import FIELD_TYPES
from typing import Iterable


class FieldTemplate(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def compute(
        self, records: Iterable[object], field_name: str, date_from: date, date_to: date
    ):
        """Compute the field value for the given records and date range.

        The given date_from and date_to parameters are expected to be UTC dates
        expressed in the user's timezone.

        :param records: the records for which to compute the field
        :param field_name: the name of the attribute that will contain the field value
        :param date_form: the minimum date of the range
        :param date_to: the maximum date of the range
        """
        raise NotImplementedError()


class ComputedFieldTemplate(models.Model):
    """A model used to reflect field templates."""

    _name = 'computed.field.template'
    _description = 'Computed Field Template'

    name = fields.Char(required=True, translate=True)
    model_id = fields.Many2one('ir.model', 'Model', required=True, ondelete='restrict')
    reference = fields.Char(required=True)
    active = fields.Boolean(default=True)
    field_type = fields.Selection(FIELD_TYPES, 'Field Type', required=True)
    field_ids = fields.One2many('computed.field', 'template_id', 'Fields')

    _sql_constraints = [
        ('unique_reference', 'unique(reference, model_id)',
         'The reference of a field template must be unique per model.'),
    ]

    @api.multi
    def write(self, vals):
        super().write(vals)
        self.field_ids._update_related_field()
        return True
