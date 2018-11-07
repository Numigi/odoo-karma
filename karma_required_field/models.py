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

    model_id = fields.Many2one('ir.model', 'Model', index=True)
    empty_fields_before = fields.Char()
    empty_fields_after = fields.Char()
    filled_fields = fields.Char()
    emptied_fields = fields.Char()
    number_empty_fields_before = fields.Integer()
    number_empty_fields_after = fields.Integer()
    number_fields_filled = fields.Integer()
    number_fields_emptied = fields.Integer()
    score = fields.Float()

    @api.model
    def log(self, model_name, record_id, empty_fields_before, empty_fields_after):
        model = self.env['ir.model'].search([('model', '=', model_name)], limit=1)
        filled_fields = set(empty_fields_before) - set(empty_fields_after)
        emptied_fields = set(empty_fields_after) - set(empty_fields_before)

        if empty_fields_before:
            score = (len(filled_fields) - len(emptied_fields)) / len(empty_fields_before)
        else:
            score = len(filled_fields) - len(emptied_fields)

        def field_list_to_string(field_list):
            return str(sorted(field_list)) if field_list else ""

        self.create({
            'model_id': model.id,
            'res_id': record_id,
            'res_model': model_name,
            'number_empty_fields_before': len(empty_fields_before),
            'number_empty_fields_after': len(empty_fields_after),
            'number_fields_filled': len(filled_fields),
            'number_fields_emptied': len(emptied_fields),
            'empty_fields_before': field_list_to_string(empty_fields_before),
            'empty_fields_after': field_list_to_string(empty_fields_after),
            'filled_fields': field_list_to_string(filled_fields),
            'emptied_fields': field_list_to_string(emptied_fields),
            'score': score,
        })

    def _compute_number_number_fields_filled(self):
        for line in self:
            line.number_fields_filled = (
                line.number_empty_fields_after -
                line.number_empty_fields_before
            )
