# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import ast

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class Karma(models.Model):

    _name = 'karma'
    _description = 'Karma'

    name = fields.Char(required=True, translate=True)
    label = fields.Char(translate=True)
    description = fields.Text(translate=True)
    url = fields.Char(
        "Related Url",
        help="On the Karma widget, a clickable link is added to the karma name."
    )
    model_id = fields.Many2one('ir.model', 'Model', required=True)
    model = fields.Char(related='model_id.model', readonly=True)
    type_ = fields.Selection([
        ('inherited', 'Inherited'),
        ('condition', 'Simple'),
    ], required=True)
    active = fields.Boolean(default=True)
    line_ids = fields.One2many('karma.line', 'karma_id', 'Children Karmas')
    condition_line_ids = fields.One2many('karma.condition.line', 'karma_id', 'Conditions')
    domain = fields.Text()

    def _get_domain(self):
        return ast.literal_eval(self.domain) if self.domain else []

    def _domain_matches_record(self, record):
        """Evaluate whether the karma matches the given record.

        :param record: the record to check.
        :return: True if the record matches the karma's domain filter, false otherwise.
        """
        filter_domain = self._get_domain()
        found_records = self.env[record._name].search([('id', '=', record.id)] + filter_domain)
        return found_records.ids == [record.id]


class KarmaWithDisplayOnFormView(models.Model):
    """Add a boolean to indicate that the karma must be displayed on the form view.

    Multiple karma objects may be displayed on the form view of a given model.

    Only the karma(s) matching the record will be displayed.

    For example, if a karma on res.partner has the filter [('customer', '=', True)],
    it will only appear on the form view for customers.

    Therefore, you may have distinct karmas for customers and suppliers.
    In case a partner is supplier and customer, both karmas will appear
    on the form view.
    """

    _inherit = 'karma'

    display_on_form_view = fields.Boolean()

    @api.model
    def find_karmas_to_display_on_form_view(self, model, record_id):
        model_matching_karmas = self.search([
            ('model_id.model', '=', model),
            ('display_on_form_view', '=', True),
        ])
        record = self.env[model].browse(record_id)
        matching_karmas = model_matching_karmas.filtered(
            lambda k: k.sudo()._domain_matches_record(record))
        return matching_karmas.read()


class KarmaWithReference(models.Model):

    _inherit = 'karma'

    ref = fields.Char(readonly=True, copy=False)

    @api.model
    def create(self, vals):
        """Automatically set the reference number when creating the karma."""
        vals['ref'] = self.env['ir.sequence'].next_by_code('karma')
        return super().create(vals)


class KarmaConditionLine(models.Model):

    _name = 'karma.condition.line'
    _description = 'Karma Condition Line'
    _order = 'sequence'

    sequence = fields.Integer()
    karma_id = fields.Many2one('karma', 'Parent Karma', required=True, ondelete='cascade')
    field_id = fields.Many2one(
        'ir.model.fields', 'Field', required=True,
        domain="[('model_id', '=', parent.model_id)]")
    condition_label = fields.Char(required=True, translate=True)
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
    model_id = fields.Many2one(related='child_karma_id.model_id', readonly=True)
    model = fields.Char(related='child_karma_id.model_id.model', readonly=True)
    field_id = fields.Many2one(
        'ir.model.fields', 'Field',
        domain="[('model_id', '=', parent.model_id), ('ttype', '=', 'many2one'),"
               " ('relation', '=', model)]")
    weighting = fields.Float('Weighting', digits=dp.get_precision('Karma Weighting'))
