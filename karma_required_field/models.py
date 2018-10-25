# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields


class KarmaRequiredField(models.Model):

    _name = 'karma.required.field'
    _description = 'Karma Required Field'

    model_id = fields.Many2one('ir.model', 'Model', ondelete='cascade', required=True)
    field_id = fields.Many2one(
        'ir.model.fields', 'Field', ondelete='cascade', required=True,
        domain="[('model_id', '=', model_id)]",
    )
    active = fields.Boolean(default=True)

    @api.model
    def get_required_field_list(self):
        return [
            {'field': f.field_id.name, 'model': f.model_id.model}
            for f in self.sudo().search([])
        ]

    _sql_constraints = [
        ('unique_field', 'unique(field_id)',
         'A record with the same field already exists.'),
    ]


class KarmaRequiredFieldLog(models.Model):

    _name = 'karma.required.field.log'
    _description = 'Karma Required Field Log'
    _inherit = 'karma.related.record.info'

    field_id = fields.Many2one(
        'ir.model.fields', 'Field', ondelete='cascade', required=True,
    )
    field_value = fields.Char()
