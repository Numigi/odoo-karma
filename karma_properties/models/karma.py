# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Karma(models.Model):

    _inherit = 'karma'

    show_properties = fields.Boolean("Show properties", copy=False)
    show_grade = fields.Boolean("Show grade", copy=False)
    show_score = fields.Boolean("Show score", copy=False)

    @api.onchange('model_id')
    def onchange_model_id(self):
        if self.model_id and self.show_properties:
            self.write({
                'show_properties': False,
                'show_grade': False,
                'show_score': False,
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
        try:
            self.env['ir.model.fields'].create(new_field)
        except ValidationError as e:
            raise ValidationError(_("Invalid reference: {}".format(e)))

    def _get_karma_properties_field_name(self):
        return ("x_karma_score_" + (self.ref).replace('-', '_').lower(),
                "x_karma_grade_" + (self.ref).replace('-', '_').lower())

    def _get_karma_properties_view_ref(self, field, view_type):
        view_ref = 'karma_properties.%s.%s' % (field, view_type)
        return self.env.ref(view_ref, raise_if_not_found=False)

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
        view_ids = self._get_karma_properties_view_ref(field, view_type)
        if view_ids:
            return
        if not self._check_if_field_exist(self.model_id, field):
            return
        view_ids = self.env['ir.ui.view'].search([
            ('model', '=', self.model_id.model),
            ('type', '=', view_type),
            ('mode', '=', 'primary'),
            ('key', 'not like', 'karma')
        ], limit=1)
        for view_id in view_ids:
            inherit_id = self.env.ref(view_id.xml_id)
            arch_base = """<?xml version="1.0"?>
                             <xpath expr="." position="inside">
                                <field name="%s" optional="show"/>
                             </xpath>
                             """ % field
            if view_type == "search":
                arch_base = """<xpath expr="//group" position="inside">
                                <filter name="%s" domain="[]"
                                context="{'group_by':'%s'}"/>
                                </xpath>
                            """ % (field, field)
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
            view_id = self.env['ir.ui.view'].sudo().create(value)
            self.env['ir.model.data'].sudo().create({
                'module': 'karma_properties',
                'name': '%s.%s' % (field, view_type),
                'model': 'ir.ui.view',
                'res_id': view_id.id,
                'noupdate': True,
            })

    def remove_view(self, field, view_type):
        view_id = self._get_karma_properties_view_ref(field, view_type)
        if view_id:
            view_id.sudo().unlink()

    def add_remove_property(self, property, field):
        if property:
            self.add_field_to_view(field, 'tree')
            self.add_field_to_view(field, 'search')
        else:
            self.remove_view(field, 'tree')
            self.remove_view(field, 'search')

    def write(self, vals):
        super().write(vals)
        for rec in self:
            if rec.show_properties:
                (score_fname,
                 grade_fname) = rec._get_karma_properties_field_name()
                # Add or Remove tree and search views
                if "show_grade" in vals:
                    rec.add_remove_property(vals['show_grade'],
                                            field=grade_fname)
                if "show_score" in vals:
                    rec.add_remove_property(vals['show_score'],
                                            field=score_fname)
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
