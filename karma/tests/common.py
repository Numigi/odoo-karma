# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class BasicKarmaTestMixin(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_partner_karma()
        cls.setup_sale_order_karmas()

    @classmethod
    def setup_partner_karma(cls):
        cls.partner_karma = cls.env['karma'].create({
            'name': 'Partner Information',
            'type_': 'condition',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'description': 'Scores the completeness of the information on the partner.',
        })

        cls.field_email = cls.env['ir.model.fields'].search([
            ('model', '=', 'res.partner'),
            ('name', '=', 'email'),
        ])

        cls.field_tags = cls.env['ir.model.fields'].search([
            ('model', '=', 'res.partner'),
            ('name', '=', 'category_id'),
        ])

        cls.line_1 = cls.env['karma.condition.line'].create({
            'karma_id': cls.partner_karma.id,
            'field_id': cls.field_email.id,
            'condition_label': 'Email is filled',
            'condition': "value",
            'result_if_true': "1",
            'result_if_false': "0",
            'weighting': 10,
        })

        cls.line_2 = cls.env['karma.condition.line'].create({
            'karma_id': cls.partner_karma.id,
            'field_id': cls.field_tags.id,
            'condition_label': 'At least 1 partner tag',
            'condition': "value",
            'result_if_true': "len(value)",
            'result_if_false': "0",
            'weighting': 5,
        })

        cls.category = cls.env.ref('base.res_partner_category_0')

        cls.partner = cls.env['res.partner'].create({
            'name': 'John Doe',
        })

    @classmethod
    def setup_sale_order_karmas(cls):
        cls.sale_order_karma = cls.env['karma'].create({
            'name': 'Sale Order Conditions',
            'type_': 'condition',
            'model_id': cls.env.ref('sale.model_sale_order').id,
            'condition_line_ids': [(0, 0, {
                'field_id': cls.env['ir.model.fields'].search([
                    ('model', '=', 'sale.order'),
                    ('name', '=', 'amount_total'),
                ]).id,
                'condition_label': 'Total amount greater than 1000',
                'condition': "value > 1000",
                'result_if_true': "1",
                'result_if_false': "0",
                'weighting': 20,
            })]
        })

        cls.inherited_so_karma = cls.env['karma'].create({
            'name': 'Inherited Sale Order Karma',
            'type_': 'inherited',
            'model_id': cls.env.ref('sale.model_sale_order').id,
        })

        cls.line_1 = cls.env['karma.line'].create({
            'karma_id': cls.inherited_so_karma.id,
            'child_karma_id': cls.partner_karma.id,
            'field_id': cls.env['ir.model.fields'].search([
                ('model', '=', 'sale.order'),
                ('name', '=', 'partner_id'),
            ]).id,
            'weighting': 60,
        })

        cls.line_2 = cls.env['karma.line'].create({
            'karma_id': cls.inherited_so_karma.id,
            'child_karma_id': cls.sale_order_karma.id,
            'weighting': 40,
        })

        cls.product = cls.env['product.product'].create({
            'type': 'service',
            'name': 'Service',
        })

        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {
                'name': '/',
                'product_id': cls.product.id,
                'price_unit': 2000,
                'product_uom_qty': 1,
                'product_uom': cls.env.ref('uom.product_uom_unit').id,
            })]
        })
