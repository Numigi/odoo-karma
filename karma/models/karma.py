# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class Karma(models.Model):

    _name = 'karma'
    _description = 'Karma'

    name = fields.Char(required=True)
    label = fields.Char()
    description = fields.Text()
    model_id = fields.Many2one('ir.model', 'Model', required=True)
    model = fields.Char(related='model_id.model')
    type_ = fields.Selection([
        ('inherited', 'Inherited'),
        ('condition', 'Ad Hoc'),
    ], required=True)
    active = fields.Boolean(default=True)
    line_ids = fields.One2many('karma.line', 'karma_id', 'Children Karmas')
    condition_line_ids = fields.One2many('karma.condition.line', 'karma_id', 'Conditions')
    domain = fields.Text()
    display_on_form_view = fields.Boolean()


class KarmaWithReference(models.Model):

    _inherit = 'karma'

    ref = fields.Char(readonly=True)


class KarmaConditionLine(models.Model):

    _name = 'karma.condition.line'
    _description = 'Karma Condition Line'
    _order = 'sequence'

    sequence = fields.Integer()
    karma_id = fields.Many2one('karma', 'Parent Karma', required=True, ondelete='cascade')
    field_id = fields.Many2one(
        'ir.model.fields', 'Field', required=True,
        domain="[('model_id', '=', parent.model_id)]")
    condition_label = fields.Char(required=True)
    condition = fields.Char(required=True)
    result_if_true = fields.Char(required=True)
    result_if_false = fields.Char(required=True, default='0')
    weighting = fields.Float('Weighting', digits=dp.get_precision('Karma Weighting'))


class KarmaLine(models.Model):

    _name = 'karma.line'
    _description = 'Karma Line'
    _order = 'sequence'

    sequence = fields.Integer()
    karma_id = fields.Many2one(
        'karma', 'Parent Karma', index=True, ondelete='cascade', required=True)
    child_karma_id = fields.Many2one('karma', 'Child Karma', index=True, required=True)
    model_id = fields.Many2one(related='child_karma_id.model_id')
    model = fields.Char(related='child_karma_id.model_id.model')
    field_id = fields.Many2one(
        'ir.model.fields', 'Field',
        domain="[('model_id', '=', parent.model_id), ('ttype', '=', 'many2one'),"
               " ('relation', '=', model)]")
    weighting = fields.Float('Weighting', digits=dp.get_precision('Karma Weighting'))
