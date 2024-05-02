# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Karma(models.Model):
    _inherit = "karma"

    output_type = fields.Selection(
        [("score", "Score"), ("information", "Information")],
        string="Result Type",
        default="score",
        required=True,
    )

    has_info_output = fields.Boolean()
    info_message = fields.Char("Information Message", translate=True)
    update_restrictions = fields.Boolean(
        "Update Restrictions",
        help="If activated, apply a blocking exception on selected fields changes.",
    )
    update_restrictions_fields_ids = fields.Many2many(
        "ir.model.fields", string="Update Restrictions Fields"
    )
    restriction_message = fields.Char("Restriction Message", translate=True)

    @api.onchange("output_type")
    def _onchange_output_type(self):
        self.display_on_form_view = self.compute_on_save = self.has_info_output = (
            self.output_type == "information"
        )


class KarmaConditionLine(models.Model):

    _inherit = "karma.condition.line"

    # Make result fields from karma to required=False and manage conditions on views
    result_if_true = fields.Char(required=False)
    result_if_false = fields.Char(required=False)
    karma_output_type = fields.Char()
