# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class Karma(models.Model):

    _inherit = 'karma'

    hide_properties = fields.Boolean("Hide properties", default=True)
    display_grade = fields.Boolean("Show grade")
    display_score = fields.Boolean("Show score")

    def create_new_field(self, name, type, model_id):
        new_field = {
            'name': name,
            'field_description': name.split("_")[2].capitalize(),
            'ttype': type,
            'model_id': model_id.id,
            'model': model_id.name,
        }
        self.env['ir.model.fields'].create(new_field)

    def add_field_properties(self):
        self.hide_properties = False
        self.create_new_field(name="x_karma_score", type='float', model_id=self.model_id)
        self.create_new_field(name="x_karma_grade", type='char', model_id=self.model_id)

    def add_field_to_view(self, field, view_tye):
        view_ids = self.env['ir.ui.view'].search([
            ('model', '=', self.model_id.model),
            ('type', '=', view_tye),
            ('key', '!=', 'karma')
        ])
        _logger.info("add_field_to_view -- view_ids %s" % view_ids)
        for view_id in view_ids:
            inherit_id = self.env.ref(view_id.xml_id)
            _logger.info("--------- view_id %s , %s" % (view_id, inherit_id))
            arch_base = _("""<?xml version="1.0"?>
                             <xpath expr="." position="inside">
                                <field name="%s"/>
                             </xpath>
                             """) % field
            value = {'name': 'karma.%s.%s' % (field, view_id.name),
                     'type': view_tye,
                     'model': view_id.model,
                     'mode': 'extension',
                     'inherit_id': inherit_id.id,
                     'key': 'karma_%s' % field.split("_")[2],
                     'arch_base': arch_base,
                     'active': True}
            self.env['ir.ui.view'].sudo().create(value)

    def remove_field_form_view(self, key):
        view_ids = self.env['ir.ui.view'].search([
            ('model', '=', self.model_id.model),
            ('key', '=', 'karma_%s' % key),
        ])
        _logger.info("--------- view_id %s" % (view_ids))
        view_ids.sudo().unlink()

    # @api.onchange("display_grade")
    # def onchange_display_grade(self):
    #     if self.display_grade:
    #         _logger.info("heeere")
    #         self.add_field_to_view(field='grade', view_tye='search')
    #         self.add_field_to_view(field='grade', view_tye='tree')

    def action_dispaly_grade(self):
        self.add_field_to_view(field='x_karma_grade', view_tye='tree')

    def action_dispaly_score(self):
        self.add_field_to_view(field='x_karma_score', view_tye='tree')

    def action_remove_grade(self):
        self.remove_field_form_view(key='grade')

    def action_remove_score(self):
        self.remove_field_form_view(key='score')

