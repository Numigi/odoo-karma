# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from odoo.tests import common


def compute_message_sent_count(records, field_name, date_from, date_to, related_model):
    for user in records:
        user[field_name] = user.env['mail.message'].search([
            ('author_id.user_ids', '=', user.id),
            ('date', '>=', fields.Date.to_string(date_from)),
            ('date', '<=', fields.Date.to_string(date_to)),
            ('model', '=', related_model),
        ], count=True)


class ResUsersWithMessageCount(models.Model):

    _inherit = 'res.users'

    def _register_hook(self):
        super()._register_hook()
        self._register_date_range_field('message_sent_count', compute_message_sent_count)


class TestFieldTemplate(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.ref('base.user_demo')
        cls.user.groups_id |= cls.env.ref('stock.group_stock_manager')

        cls.range_today = cls.env.ref('date_range_field_template.range_today')

        cls.template = cls.env['computed.field.template'].create({
            'name': 'Message Sent Count',
            'model_id': cls.env.ref('base.model_res_users').id,
            'reference': 'message_sent_count',
            'field_type': 'integer',
            'related_model_argument': True,
        })

        cls.env['computed.field'].create({
            'template_id': cls.template.id,
            'range_id': cls.range_today.id,
            'related_model_id': cls.env.ref('base.model_res_partner').id,
        })

        cls.env['computed.field'].create({
            'template_id': cls.template.id,
            'range_id': cls.range_today.id,
            'related_model_id': cls.env.ref('product.model_product_product').id,
        })

    def test_ifCreatePartner_partnerMessageCountIsIncreased(self):
        value_before = self.user.x__message_sent_count__res_partner__today
        self.env['res.partner'].sudo(self.user).create({'name': 'My new partner'})
        self.user.refresh()
        value_after = self.user.x__message_sent_count__res_partner__today
        assert value_before < value_after

    def test_ifCreateProduct_productMessageCountIsIncreased(self):
        value_before = self.user.x__message_sent_count__product_product__today
        self.env['product.product'].sudo(self.user).create({'name': 'My new product'})
        self.user.refresh()
        value_after = self.user.x__message_sent_count__product_product__today
        assert value_before < value_after

    def test_ifCreateProduct_partnerMessageCountDoesNotChange(self):
        value_before = self.user.x__message_sent_count__res_partner__today
        self.env['product.product'].sudo(self.user).create({'name': 'My new product'})
        self.user.refresh()
        value_after = self.user.x__message_sent_count__res_partner__today
        assert value_before == value_after

    def test_ifCreatePartner_productMessageCountDoesNotChange(self):
        value_before = self.user.x__message_sent_count__product_product__today
        self.env['res.partner'].sudo(self.user).create({'name': 'My new partner'})
        self.user.refresh()
        value_after = self.user.x__message_sent_count__product_product__today
        assert value_before == value_after
