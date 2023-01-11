# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from freezegun import freeze_time
from odoo.tests import common
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestFieldTemplate(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'Test User',
            'login': 'test@example.com',
            'email': 'test@example.com',
            'tz': 'UTC',
        })

        cls.range_today = cls.env.ref('date_range_field_template.range_today')

        cls.template = cls.env.ref('karma_required_field.karma_field_avg_template')

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

        cls.product = cls.env['product.product'].create({'name': 'My Product'})
        cls.partner = cls.env['res.partner'].create({'name': 'My Partner'})

    @classmethod
    def log_changes(cls, record, fields_before, fields_after):
        cls.env['karma.required.field.log'].sudo(cls.user).log(
            record._name, record.id, fields_before, fields_after)
        log = cls.env['karma.required.field.log'].search([], limit=1, order='id desc')
        cls.env.cr.execute(
            'UPDATE karma_required_field_log SET create_date = %(date)s '
            'WHERE id = %(log_id)s', {
                'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'log_id': log.id,
            })

    def test_ifNoLog_thenScoreIsZero(self):
        assert self.user.x__karma_field_avg__res_partner__today == 0

    def test_ifFieldsAllFilled_thenScoreIs100(self):
        self.log_changes(self.partner, ['email', 'phone'], [])
        assert self.user.x__karma_field_avg__res_partner__today == 1

    def test_ifHalfFieldsFilled_thenScoreIs50(self):
        self.log_changes(self.partner, ['email', 'phone'], ['email'])
        assert round(self.user.x__karma_field_avg__res_partner__today, 2) == 0.5

    def test_ifNoEmptyFieldsBefore_andOneEmptyFieldAfter_thenScoreIsMinus100(self):
        self.log_changes(self.partner, [], ['email'])
        assert round(self.user.x__karma_field_avg__res_partner__today, 2) == -1

    def test_ifNoEmptyFieldsBefore_andTwoEmptyFieldAfter_thenScoreIsMinus200(self):
        self.log_changes(self.partner, [], ['email', 'phone'])
        assert round(self.user.x__karma_field_avg__res_partner__today, 2) == -2

    def test_ifMoreEmptyFieldsAfter_thenScoreIsNegative(self):
        self.log_changes(self.partner, ['email'], ['email', 'phone'])
        assert self.user.x__karma_field_avg__res_partner__today == -1

    def test_ifPartnerFieldsLogged_thenScoreForProductIsUnchanged(self):
        self.log_changes(self.partner, ['email', 'phone'], [])
        assert self.user.x__karma_field_avg__product_product__today == 0

    def test_ifProductFieldsLogged_thenScoreForPartnerIsUnchanged(self):
        self.log_changes(self.product, ['default_code', 'barcode'], [])
        assert self.user.x__karma_field_avg__res_partner__today == 0

    def test_ifChangesLoggedYesterday_thenScoreForTodayIsUnchanged(self):
        with freeze_time(datetime.now() - timedelta(1)):
            self.log_changes(self.partner, ['email', 'phone'], [])

        assert self.user.x__karma_field_avg__res_partner__today == 0

    def test_ifChangesLoggedTomorow_thenScoreForTodayIsUnchanged(self):
        with freeze_time(datetime.now() + timedelta(1)):
            self.log_changes(self.partner, ['email', 'phone'], [])

        assert self.user.x__karma_field_avg__res_partner__today == 0

    def test_ifMultipleLogEntries_thenTheScoreIsTheAverage(self):
        self.log_changes(self.partner, ['street', 'city', 'email', 'phone'], ['phone'])  # 0.75
        self.log_changes(self.partner, ['phone'], ['email', 'phone'])  # -1
        assert self.user.x__karma_field_avg__res_partner__today == -0.125
