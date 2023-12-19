# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class Karma(models.Model):

    _inherit = 'karma'

    show_properties = fields.Boolean("Show properties", copy=False)
    display_grade = fields.Boolean("Show grade", copy=False)
    display_score = fields.Boolean("Show score", copy=False)

    @api.onchange('model_id')
    def onchange_model_id(self):
        if self.model_id and self.show_properties:
            self.write({
                'show_properties': False,
                'display_grade': False,
                'display_score': False,
            })

    def _check_if_field_exist(self, model_id, name):
        field_exist = self.env['ir.model.fields'].search([
            ('model_id', '=', model_id.id), ('name', '=', name)
            ])
        return True if field_exist else False

    def create_new_field(self, name, ttype, model_id):
        self.ensure_one()
        if self._check_if_field_exist(model_id, name):
            return
        new_field = {
            'name': name,
            'field_description': "%s %s" % (
                self.label, name.split("_")[2].capitalize()),
            'ttype': ttype,
            'model_id': model_id.id,
            'model': model_id.name,
            'state': 'manual',
            'copied': False,
            'readonly': True,
        }
        self.env['ir.model.fields'].create(new_field)

    def _get_karma_properties_field_name(self):
        return ("x_karma_score_" + (self.ref).lower(),
                "x_karma_grade_" + (self.ref).lower())

    def add_field_properties(self):
        self.ensure_one()
        self.show_properties = True
        score_fname, grade_fname = self._get_karma_properties_field_name()
        self.create_new_field(
            name=score_fname, ttype='float', model_id=self.model_id)
        self.create_new_field(
            name=grade_fname, ttype='char', model_id=self.model_id)

    def _check_if_view_exist(self, model, name):
        view_exist = self.env['ir.ui.view'].search([
            ('model', '=', model), ('name', '=', name)
            ])
        return True if view_exist else False

    def add_field_to_view(self, field, view_type):
        key = 'karma_%s' % field.split("_")[2]
        view_ids = self.property_view_get(key)
        if view_ids:
            return
        if not self._check_if_field_exist(self.model_id, field):
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
                                <field name="%s" optional="show"/>
                             </xpath>
                             """ % field
            if view_type == "search":
                label = _("%s %s" % (self.label, field.split("_")[2]))
                arch_base = """<xpath expr="//group" position="inside">
                                <filter string="%s" name="%s" domain="[]"
                                context="{'group_by':'%s'}"/>
                                </xpath>
                            """ % (label, field, field)
            view_name = '%s.%s' % (view_id.name, field)
            value = {
                    'name': view_name,
                    'type': view_type,
                    'model': view_id.model,
                    'mode': 'extension',
                    'inherit_id': inherit_id.id,
                    'key': key,
                    'arch_base': arch_base,
                    'active': True
                    }
            if self._check_if_view_exist(view_id.model, view_name):
                return
            self.env['ir.ui.view'].sudo().create(value)

    def property_view_get(self, key):
        return self.env['ir.ui.view'].search([
            ('model', '=', self.model_id.model),
            ('key', '=', 'karma_%s' % key),
        ])

    def remove_field_form_view(self, key):
        view_ids = self.property_view_get(key)
        view_ids.sudo().unlink()

    def add_remove_property(self, property, field):
        if property:
            self.add_field_to_view(field=field, view_type='tree')
            self.add_field_to_view(field=field, view_type='search')
        else:
            self.remove_field_form_view(key=field.split("_")[2])

    def write(self, vals):
        super().write(vals)
        for rec in self:
            if rec.show_properties:
                (score_fname,
                 grade_fname) = rec._get_karma_properties_field_name()
                # Add fields to tree and search view
                if "display_score" in vals or "model_id" in vals:
                    display_score = (
                        "display_score" in vals or rec.display_score
                        )
                    rec.add_remove_property(display_score,
                                            field=score_fname)
                if "display_grade" in vals or "model_id" in vals:
                    display_grade = (
                        "display_grade" in vals or rec.display_grade
                        )
                    rec.add_remove_property(display_grade,
                                            field=grade_fname)
        return True

    @api.model
    def _compute(self, computer, record):
        result = super(Karma, self)._compute(computer, record)
        if self.show_properties:
            score_fname, grade_fname = self._get_karma_properties_field_name()
            model = self.model_id.model
            score_field = self.env[model]._fields.get(score_fname)
            grade_field = self.env[model]._fields.get(grade_fname)
            if score_field and result.score:
                record[score_fname] = result.score
            if grade_field and result.grade:
                record[grade_fname] = result.grade
        return result
