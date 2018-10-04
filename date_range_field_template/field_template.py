# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from odoo import api, fields, models
from odoo.addons.base.ir.ir_model import FIELD_TYPES
from typing import Iterable


class ComputedFieldTemplate(models.Model):
    """A model used to reflect field templates."""

    _name = 'computed.field.template'
    _description = 'Computed Field Template'

    name = fields.Char(required=True, translate=True)
    model_id = fields.Many2one('ir.model', 'Model', required=True, ondelete='restrict')
    reference = fields.Char(required=True)
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
