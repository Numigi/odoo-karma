# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _
from ..safe_eval import restricted_safe_eval
from .common import KarmaComputationError, AbstractKarmaComputer


FIELD_NULL_VALUES = {
    'boolean': False,
    'char': '',
    'html': '',
    'text': '',
}


class ConditionKarmaComputer(AbstractKarmaComputer):
    """This class defines how Ad Hoc Karma scores are computed."""

    def __init__(self, karma):
        """Add a dict for caching `karma.score.condition` records.

        `karma.score.condition` are snapshots of `karma.score.condition` when
        a score is computed.
        """
        super().__init__(karma)
        self._conditions = {}

    def compute(self, record):
        """Compute the score for a given record.

        :param record: the record to process
        :return: a `karma.score.condition` record
        """
        score_line = self._env['karma.score'].create({
            'karma_id': self._karma.id,
            'res_id': record.id,
            'res_model': record._name,
        })

        for line in self._karma.condition_line_ids:
            self._create_score_detail_line(score_line, line, record)

        score_line.score = sum(l.result for l in score_line.condition_detail_ids)

        return score_line

    def _create_score_detail_line(self, parent_score, karma_line, record):
        """Create a detail line for the given score line.

        :param parent_score: the `karma.score` record for which to create the detail lines.
        :param karma_line: the `karma.condition.line` to process
        :param record: the record to process
        """
        condition = self._get_score_condition(karma_line)

        value = self._get_field_value(karma_line, record)

        condition_fulfilled = self._eval_expression(karma_line.condition, value)

        result_expression = (
            karma_line.result_if_true
            if condition_fulfilled else karma_line.result_if_false
        )
        score = self._eval_expression(result_expression, value)

        self._env['karma.score.condition.detail'].create({
            'score_id': parent_score.id,
            'condition_id': condition.id,
            'condition_fulfilled': condition_fulfilled,
            'score': score,
            'result': score * karma_line.weighting,
        })

    def _get_field_value(self, karma_line, record):
        """Get the value of the field for the given record.

        For some types of field, an alternative value is returned when the
        field as a non-true value.

        This simplifies the complexity of the expressions for those types of fields.

        For example, when evaluating the field `email` of a partner, if the email was
        not filled, then it contains False.

        Therefore, the following condition:

            value is not False and `@` in value

        is simplified to:

            `@` in value

        :param karma_line: the karma.condition.line to evaluate
        :param record: the record to evaluate
        :return: the field value
        """
        value = record[karma_line.field_id.name]

        if not value and karma_line.field_id.ttype in FIELD_NULL_VALUES:
            value = FIELD_NULL_VALUES[karma_line.field_id.ttype]

        return value

    def _get_score_condition(self, karma_line):
        """Get a `karma.score.condition` record matching a `karma.condition.line`.

        If a matching `karma.score.condition` does not exist, then create a new one.

        The purpose of this complexity is to limit disk space usage of score data.

        :param karma_line: a `karma.condition.line` record
        :return: a `karma.score.condition` record
        """
        if karma_line not in self._conditions:
            condition = self._find_matching_score_condition(karma_line)

            if not condition:
                condition = self._create_score_condition(karma_line)

            self._conditions[karma_line] = condition

        return self._conditions[karma_line]

    def _find_matching_score_condition(self, karma_line):
        return self._env['karma.score.condition'].search([
            ('condition_label', '=', karma_line.condition_label),
            ('field_id', '=', karma_line.field_id.id),
            ('condition', '=', karma_line.condition),
            ('result_if_true', '=', karma_line.result_if_true),
            ('result_if_false', '=', karma_line.result_if_false),
            ('weighting', '=', karma_line.weighting),
        ], limit=1)

    def _create_score_condition(self, karma_line):
        return self._env['karma.score.condition'].create({
            'condition_label': karma_line.condition_label,
            'field_id': karma_line.field_id.id,
            'condition': karma_line.condition,
            'result_if_true': karma_line.result_if_true,
            'result_if_false': karma_line.result_if_false,
            'weighting': karma_line.weighting,
        })

    def _eval_expression(self, expression, value):
        """Evaluate an expression for a given value.

        :param expression: the expression to eval.
        :param value: the value to assign to the `value` attribute of the expression.
        """
        try:
            return restricted_safe_eval(expression, {'value': value})
        except Exception as err:
            raise KarmaComputationError(_(
                'The following expression could not be evaluated with the value {value}. '
                '\n\n{expression}'
                '\n\n{err}'
            ).format(expression=expression, value=value, err=err))
