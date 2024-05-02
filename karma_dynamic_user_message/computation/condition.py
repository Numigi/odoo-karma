# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.karma.computation.condition import ConditionKarmaComputer


class ConditionKarmaComputerAdvanced(ConditionKarmaComputer):
    """Advanced version of the ConditionKarmaComputer class."""

    def _create_score_detail_line(self, parent_score, karma_line, record):
        """Create a detail line for the given score line.

        :param parent_score: the `karma.score` record for which to create
        the detail lines.
        :param karma_line: the `karma.condition.line` to process
        :param record: the record to process
        """

        # Call the base function from the inherited class
        if (
            karma_line.karma_id.has_info_output
            and karma_line.karma_output_type == "information"
        ):
            # Set value for computation because not required, and not visible
            karma_line.result_if_true = 1
            karma_line.weighting = 1

        condition = self._condition_cache.get(karma_line)

        value = self._get_field_value(karma_line, record)

        condition_reached = self._eval_expression(karma_line.condition, value)

        result_expression = (
            karma_line.result_if_true
            if condition_reached
            else karma_line.result_if_false
        )
        score = self._eval_expression(result_expression, value)

        self._env["karma.score.condition.detail"].create(
            {
                "score_id": parent_score.id,
                "field_value": self._format_field_value(karma_line, value),
                "condition_id": condition.id,
                "condition_reached": condition_reached,
                "score": score,
                "result": score * karma_line.weighting,
            }
        )

    ConditionKarmaComputer._create_score_detail_line = _create_score_detail_line
