# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import UserError


class BaseModelExtend(models.AbstractModel):
    _inherit = "base"

    def write(self, vals):
        karma_model_restrictions = self.env["karma"].search(
            [
                (
                    "model_id",
                    "=",
                    self.env["ir.model"].search([("model", "=", self._name)]).id,
                )
            ]
        )

        restriction_active, karma = self._get_karma_restriction_active(
            karma_model_restrictions
        )

        if restriction_active:
            self._process_karma_restrictions_warning(karma, vals)

        result = super(BaseModelExtend, self).write(vals)
        return result

    def _get_karma_restriction_active(self, karma_model_restrictions):
        restriction_active = False
        karma = None
        for karma in karma_model_restrictions:
            # Get only the karma that have the update_restrictions activated
            # and the output_type is information.
            # If at least one karma has the update_restrictions activated,
            # break the loop to avoid unnecessary iterations and raise the warning
            if karma.update_restrictions and karma.output_type == "information":
                restriction_active = True
                karma = karma
                break
        return restriction_active, karma

    def _process_karma_restrictions_warning(self, karma, vals):
        # Find the last karma score for the record
        karma_score = self.env["karma.score"].search(
            [
                ("karma_id", "=", karma.id),
                ("res_id", "=", self.id),
                ("res_model", "=", self._name),
            ],
            order="id desc",
            limit=1,
        )
        # Check if all conditions are met
        if karma_score and karma_score.score == sum(
            [x.weighting for x in karma.condition_line_ids]
        ):
            for field in vals:
                if karma.update_restrictions_fields_ids and field in [
                    x.name for x in karma.update_restrictions_fields_ids
                ]:
                    raise UserError(karma.restriction_message)
