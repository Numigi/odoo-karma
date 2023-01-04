# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestKarmaDisplayOnFormView(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['karma'].search([]).write({'display_on_form_view': False})

        cls.customer_karma = cls.env['karma'].create({
            'name': 'Customer Karma',
            'type_': 'condition',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'display_on_form_view': True,
        })

        cls.supplier_karma = cls.env['karma'].create({
            'name': 'Customer Karma',
            'type_': 'condition',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'domain': "[('name', '=', 'supplier')]",
            'display_on_form_view': True,
        })

        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner Test',
        })

        cls.user = cls.env.ref('base.user_demo')

    def _find_karma(self):
        """Find the karma objects to display on the form view for the partner."""
        karma_data = self.env['karma'].sudo(self.user).find_karmas_to_display_on_form_view(
            'res.partner', self.partner.id)
        result = self.env['karma']
        for item in karma_data:
            result |= self.env['karma'].browse(item['id'])
        return result

    # def test_ifPartnerIsCustomer_thenCustomerKarmaIsDisplayed(self):
    #     """ to align with 14 , there is no customer or supplier in partner object"""
    #     self.partner.customer = True
    #     assert self._find_karma() == self.customer_karma

    # def test_ifPartnerIsSupplier_thenSupplierKarmaIsDisplayed(self):
    #     """ to align with 14 , there is no customer or supplier in partner object"""
    #     self.partner.name = 'supplier'
    #     assert self._find_karma() == self.supplier_karma

    def test_ifPartnerIsNeither_thenNoKarmaIsDisplayed(self):
        assert not self._find_karma()

    # def test_ifPartnerIsBoth_thenBothKarmasAreDisplayed(self):
    #     """ to align with 14 , there is no customer or supplier in partner object"""
    #     self.partner.customer = True
    #     self.partner.supplier = True
    #     assert self._find_karma() == self.customer_karma | self.supplier_karma

    # def test_ifDisplayOnFormViewIsFalse_thenKarmaIsNotDisplayed(self):
    #     """ to align with 14 , there is no customer or supplier in partner object"""
    #     self.partner.customer = True
    #     self.customer_karma.display_on_form_view = False
    #     assert not self._find_karma()
