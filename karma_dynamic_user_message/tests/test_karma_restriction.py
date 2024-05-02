# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError
from ..computation import ConditionKarmaComputer


class TestKarmaRestriction(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.karma = cls.env["karma"].create(
            {
                "name": "Partner Information",
                "type_": "condition",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "description": "Scores the completeness of the information on the partner.",
            }
        )

        cls.field_email = cls.env["ir.model.fields"].search(
            [
                ("model", "=", "res.partner"),
                ("name", "=", "email"),
            ]
        )

        cls.job_position = cls.env["ir.model.fields"].search(
            [
                ("model", "=", "res.partner"),
                ("name", "=", "function"),
            ]
        )

        cls.line_1 = cls.env["karma.condition.line"].create(
            {
                "karma_id": cls.karma.id,
                "field_id": cls.field_email.id,
                "condition_label": "Email contains @",
                "condition": "'@' in value",
                "result_if_true": "1",
                "result_if_false": "0",
                "weighting": 10,
            }
        )

        cls.line_2 = cls.env["karma.condition.line"].create(
            {
                "karma_id": cls.karma.id,
                "field_id": cls.job_position.id,
                "condition_label": "Have function",
                "condition": "value != ''",
                "result_if_true": "1",
                "result_if_false": "0",
                "weighting": 5,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "John Doe",
            }
        )

        cls.computer = ConditionKarmaComputer(cls.karma)

    def test_karma_restriction_on_write(self):
        # Activate the restriction on the karma.
        self.karma.write({"output_type": "information"})
        self.karma._onchange_output_type()
        self.karma.write(
            {
                "update_restrictions": True,
                "update_restrictions_fields_ids": [
                    (6, 0, [self.ref("base.field_res_partner__email")])
                ],
                "restriction_message": "You cannot change the email.",
            }
        )

        # Ensure that no raise is triggered at the beginning.
        self.partner.email = "test_karma@test.ca"
        self.partner.name = "James"

        # Compute the initial karma score on the partner.
        score_line = self.computer.compute(self.partner)
        self.assertEqual(score_line.score, 10)

        # Write is possible here on email field because function is not set.
        self.partner.write({"email": "my.old.one.mail@nn.nn"})

        # Then add a function to partner.
        self.partner.function = "Developer"

        # Compute the karma on the partner.
        score_line = self.computer.compute(self.partner)
        self.assertEqual(score_line.score, 15)

        # Test UserError raised when trying to write on a field with a restriction.
        with self.assertRaises(UserError):
            self.partner.write({"email": "new.mail@nn.nn"})

        # When the condition is removed, the raise will not be triggered.
        self.line_2.unlink()
        self.partner.write({"email": "new.mail@nn.nn"})
