# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class Karma(models.Model):

    _name = 'karma'
    _description = 'Karma'

    name = fields.Char(required=True)
    description = fields.Text()
    model_id = fields.Many2one('ir.model', 'Model', required=True)
    type_ = fields.Selection([
        ('inherited', 'Inheited'),
        ('condition', 'Ad Hoc'),
    ])
    active = fields.Boolean(default=True)
    line_ids = fields.One2many('karma.line', 'karma_id', 'Children Karmas')
    condition_line_ids = fields.One2many('karma.condition.line', 'karma_id', 'Conditions')
    domain = fields.Text()


class KarmaConditionLine(models.Model):

    _name = 'karma.condition.line'
    _description = 'Karma Condition Line'
    _order = 'sequence'

    sequence = fields.Integer()
    karma_id = fields.Many2one('karma', 'Parent Karma', required=True, ondelete='cascade')
    field_id = fields.Many2one(
        'ir.model.fields', 'Field', required=True,
        domain="[('parent.model_id', '=', model_id)]")
    condition_label = fields.Char(required=True)
    condition = fields.Char(required=True)
    result_if_true = fields.Char(required=True)
    result_if_false = fields.Char(required=True, default='0')
    weighting = fields.Float('Weighting', digits=dp.get_precision('Karma Weighting'))


class KarmaLine(models.Model):

    _name = 'karma.line'
    _description = 'Karma Line'

    karma_id = fields.Many2one(
        'karma', 'Parent Karma', index=True, ondelete='cascade', required=True)
    child_karma_id = fields.Many2one('karma', 'Child Karma', index=True, required=True)
    model_id = fields.Many2one(related='child_karma_id.model_id')
    field_id = fields.Many2one(
        'ir.model.fields', 'Field',
        domain="[('parent.model_id', '=', model_id), ('type', '=', 'many2one')]")
    weighting = fields.Float('Weighting', digits=dp.get_precision('Karma Weighting'))
