# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from .tools import get_technical_field_name


class ComputedField(models.Model):

    _name = 'computed.field'
    _description = 'Computed Field'

    name = fields.Char(related='field_id.field_description', readonly=True)
    template_id = fields.Many2one(
        'computed.field.template', 'Field Template', required=True, ondelete='restrict')
    range_id = fields.Many2one(
        'computed.field.date.range', 'Date Range', required=True, ondelete='restrict')
    field_id = fields.Many2one('ir.model.fields', 'Field', ondelete='restrict')
    related_model_id = fields.Many2one('ir.model', 'Related Model')

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._create_related_field()
        return record

    @api.multi
    def write(self, vals):
        super().write(vals)
        self._update_related_field()
        return True

    @api.multi
    def unlink(self):
        """Unlink the related field if the computed field is unlinked.

        The reason is that a computed field entry should only be deletable
        if the related field is deletable. Otherwise, we end up with a field
        that still exists in the system but does not appear in the list of computed
        fields.

        In other words, we accept deleting an unused computed field.
        """
        fields = self.mapped('field_id')
        super().unlink()
        fields.sudo().unlink()
        return True

    def _create_related_field(self):
        initial_values = self._get_field_values()
        initial_values['field_description'] = self._get_field_label()
        self.field_id = self.env['ir.model.fields'].sudo().create(initial_values)

    def _update_related_field(self):
        for record in self:
            record.field_id.sudo().write(record._get_field_values())

    def _get_related_model_name(self):
        """Get the name of the model related to the field."""
        return (
            self.related_model_id.model if self.template_id.related_model_argument
            else None
        )

    def _get_field_values(self):
        """Get the values to propagate to the ir.model.fields record.

        :return: a dictionary containing the ir.model.fields values
        """
        technical_name = get_technical_field_name(
            self.template_id.reference, self.range_id.reference,
            related_model=self._get_related_model_name())
        return {
            'column1': False,
            'column2': False,
            'compute': self._get_compute_script(),
            'copy': False,
            'depends': False,
            'domain': False,
            'groups': False,
            'help': False,
            'index': False,
            'model': self.template_id.model_id.model,
            'model_id': self.template_id.model_id.id,
            'name': technical_name,
            'on_delete': False,
            'readonly': True,
            'related': False,
            'relation': False,
            'relation_field': False,
            'required': False,
            'selectable': False,
            'selection': False,
            'size': False,
            'state': 'manual',
            'store': False,
            'translate': False,
            'ttype': self.template_id.field_type,
        }

    def _get_field_label(self):
        template = self.template_id.name
        range_ = self.range_id.name
        if self.template_id.related_model_argument:
            return '{template} ({model} / {range})'.format(
                template=template, range=range_, model=self.related_model_id.name)
        else:
            return '{template} ({range})'.format(
                template=template, range=range_)

    def _get_compute_script(self):
        template = self.template_id.reference
        range_ = self.range_id.reference

        if self.template_id.related_model_argument:
            return (
                "self.compute_date_range_field"
                "('{template}', '{range}', related_model='{model}')").format(
                template=template, range=range_,
                model=self._get_related_model_name())
        else:
            return "self.compute_date_range_field('{template}', '{range}')".format(
                template=template, range=range_)

    def _update_related_field_label(self):
        for lang in self.env['res.lang'].search([]):
            for record in self.with_context(lang=lang.code):
                record.field_id.sudo().field_description = record._get_field_label()
