# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _



class Karma(models.Model):

    _inherit = 'karma'

    hide_properties = fields.Boolean("Hide properties", default=True)
    display_grade = fields.Boolean("Show grade")
    display_score = fields.Boolean("Show score")

    def create_new_field(self, name,type, model_id):
        new_field = {
            'name': name,
            'field_description': name,
            'ttype': type,
            'model_id': model_id.id,
            'model': model_id.name,
            'state': 'base'
        }
        self.env['ir.model.fields'].create(new_field)

    def add_field_properties(self):
        self.hide_properties = False
        self.create_new_field(name="score", type='float', model_id=self.model_id)
        self.create_new_field(name="grade", type='char', model_id=self.model_id)

    def add_field_to_view(self, field, view_tye):
        search_views_ids = self.env['ir.ui.view'].search([
            ('model', '=', self.model_id.model),
            ('type', '=', view_tye),

        ])
        for view in search_views_ids:
            inherit_id = self.env.ref(view.xml_id)
            arch_base = _("""<?xml version="1.0"?>
                                                 <xpath expr="." position="inside">
                                                    <field name="%s"/>
                                                 </xpath>
                                                 """) % field
            value = {'name': 'filter.%s' % view.name,
                     'type': view_tye,
                     'model': view.model,
                     'mode': 'extension',
                     'inherit_id': inherit_id.id,
                     'arch_base': arch_base,
                     'active': True}
            self.env['ir.ui.view'].sudo().create(value)

    @api.onchange("display_grade")
    def onchange_display_grade(self):
        if self.display_grade:
            self.add_field_to_view(field='grade', view_tye='search')
            self.add_field_to_view(field='grade', view_tye='tree')
