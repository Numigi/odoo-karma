# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.karma.tests.test_condition_computation import (
    TestComputedKarmaComputation,
)
from odoo.exceptions import UserError


class TestKarmaRestriction(TestComputedKarmaComputation):
    def setUp(self):
        super().setUp()

    def test_karma_restriction_on_write(self):
        # Update the karma, to activate the output type to information.
        self.job_position = self.env["ir.model.fields"].search(
            [
                ("model", "=", "res.partner"),
                ("name", "=", "function"),
            ]
        )
        # Recreate condition lines with different conditions.
        self.line_2.unlink()
        self.line_2 = self.env["karma.condition.line"].create(
            {
                "karma_id": self.karma.id,
                "field_id": self.job_position.id,
                "condition_label": "Have function",
                "condition": "value != ''",
                "result_if_true": "1",
                "result_if_false": "0",
                "weighting": 5,
            }
        )

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
