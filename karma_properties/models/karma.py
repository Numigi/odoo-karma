# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class Karma(models.Model):

    _inherit = 'karma'

    show_properties = fields.Boolean("Show properties", default=False)
    display_grade = fields.Boolean("Show grade")
    display_score = fields.Boolean("Show score")

    def create_new_field(self, name, type, model_id):
        new_field = {
            'name': name,
            'field_description': "%s %s" % (self.label, name.split("_")[2].capitalize()),
            'ttype': type,
            'model_id': model_id.id,
            'model': model_id.name,
        }
        self.env['ir.model.fields'].create(new_field)

    def add_field_properties(self):
        self.show_properties = True
        self.create_new_field(name="x_karma_score", type='float', model_id=self.model_id)
        self.create_new_field(name="x_karma_grade", type='char', model_id=self.model_id)

    def add_field_to_view(self, field, view_type):
        key = 'karma_%s' % field.split("_")[2]
        view_ids = self.property_view_get(key)
        if view_ids:
            return
        view_ids = self.env['ir.ui.view'].search([
            ('model', '=', self.model_id.model),
            ('type', '=', view_type),
            ('mode', '=', 'primary'),
            ('key', 'not like', 'karma')
        ])
        for view_id in view_ids:
            inherit_id = self.env.ref(view_id.xml_id)
            arch_base = """<?xml version="1.0"?>
                             <xpath expr="." position="inside">
                                <field name="%s"/>
                             </xpath>
                             """ % field
            if view_type == "search":
                label = _("%s %s" % (self.label, field.split("_")[2]))
                group_by = """ 
                            <filter string="%s" name="%s" domain="[]" context="{'group_by':'%s'}"/>
                        """ % (label, field, field)
                arch_base = arch_base.split("</xpath>",1)[0] + group_by + "</xpath>"
            value = {
                    'name': 'karma.%s.%s' % (field, view_id.name),
                    'type': view_type,
                    'model': view_id.model,
                    'mode': 'extension',
                    'inherit_id': inherit_id.id,
                    'key': key,
                    'arch_base': arch_base,
                    'active': True
                    }
            self.env['ir.ui.view'].sudo().create(value)

    def property_view_get(self, key):
        return self.env['ir.ui.view'].search([
            ('model', '=', self.model_id.model),
            ('key', '=', 'karma_%s' % key),
        ])

    def remove_field_form_view(self, key):
        view_ids = self.property_view_get(key)
        view_ids.sudo().unlink()

    def show_property(self, vals, field):
        if vals:
            self.add_field_to_view(field=field, view_type='tree')
            self.add_field_to_view(field=field, view_type='search')
        else:
            self.remove_field_form_view(key=field.split("_")[2])

    def write(self, vals):
        super().write(vals)
        if "display_grade" in vals:
            self.show_property(vals['display_grade'], field='x_karma_grade')
        if "display_score" in vals:
            self.show_property(vals['display_score'], field='x_karma_score')
        return True

    @api.model
    def _compute(self, computer, record):
        score = super()._compute(computer, record)
        if self.show_properties:
            record.x_karma_score = score.score
            record.x_karma_grade = score.grade
        return score






