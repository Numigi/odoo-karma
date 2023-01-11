# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import sys

from odoo import models, _
from odoo.tools import pycompat
from ..safe_eval import restricted_safe_eval


class KarmaConditionEvaluationError(Exception):
    pass


FIELD_NULL_VALUES = {
    'boolean': False,
    'char': '',
    'html': '',
    'text': '',
}


class ConditionKarmaComputer:
    """This class defines how Simple Karma scores are computed."""

    def __init__(self, karma):
        self._karma = karma.sudo()
        self._env = self._karma.env
        self._condition_cache = ScoreConditionCache(self._env)

    def compute(self, record):
        """Compute the score for a given record.

        :param record: the record to process
        :return: a `karma.score.condition` record
        """
        record = record.sudo()
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
        condition = self._condition_cache.get(karma_line)

        value = self._get_field_value(karma_line, record)

        condition_reached = self._eval_expression(karma_line.condition, value)

        result_expression = (
            karma_line.result_if_true
            if condition_reached else karma_line.result_if_false
        )
        score = self._eval_expression(result_expression, value)

        self._env['karma.score.condition.detail'].create({
            'score_id': parent_score.id,
            'field_value': self._format_field_value(karma_line, value),
            'condition_id': condition.id,
            'condition_reached': condition_reached,
            'score': score,
            'result': score * karma_line.weighting,
        })

    @staticmethod
    def _get_field_value(karma_line, record):
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

    @staticmethod
    def _format_field_value(karma_line, value):
        """Format a field value for displaying in the details of a karma score.

        :param value: the value to format
        """
        if karma_line.field_id.ttype == 'binary':
            return _('Filled') if value else _('Empty')

        if isinstance(value, models.Model):
            return ', '.join(value.mapped('display_name'))
        else:
            return value

    @staticmethod
    def _eval_expression(expression, value):
        """Evaluate an expression for a given value.

        In case of an error in the execution in the evaluation of the expression,
        the safe_eval function from Odoo raises ValueError.
        This method adds more context to the exception raised.

        :param expression: the expression to eval.
        :param value: the value to assign to the `value` attribute of the expression.
        """
        try:
            return restricted_safe_eval(expression, {'value': value})
        except ValueError as err:
            error_message = _(
                'The following expression could not be evaluated with the value {value}. '
                '\n\n{expression}'
                '\n\n{err}'
            ).format(value=value, expression=expression, err=err)
            # pycompat.reraise(
            #     KarmaConditionEvaluationError,
            #     KarmaConditionEvaluationError(error_message),
            #     sys.exc_info()[2],
            # )


class ScoreConditionCache:
    """Class responsible for caching records of `karma.score.condition`.

    The purpose of this complexity is to limit disk space usage of score data.

    A record of `karma.score.condition` represents a snapshot of a `karma.condition.line`.
    If the condition lines on a karma record are chagned, this has no impact on
    scores already computed.

    All scores that are computed from the same `karma.condition.line` will be linked to the
    same `karma.score.condition` record unless the `karma.condition.line` changes.
    """

    def __init__(self, env):
        self._env = env
        self._conditions = {}
        self._langs = self._env['res.lang'].search([])

    def get(self, karma_line):
        """Get a `karma.score.condition` record matching a `karma.condition.line`.

        If a matching `karma.score.condition` does not exist, then create a new one.

        :param karma_line: a `karma.condition.line` record
        :return: a `karma.score.condition` record
        """
        if karma_line not in self._conditions:
            condition = self._find_matching_score_condition(karma_line)

            if not condition:
                condition = self._create_score_condition(karma_line)

            self._conditions[karma_line] = condition

        else:
            condition = self._conditions[karma_line]

            # If a rollback happened, a cached condition may not exist in the database.
            if not condition.exists():
                self._conditions = {}
                return self.get(karma_line)

        return condition

    def _find_matching_score_condition(self, karma_line):
        condition = self._env['karma.score.condition'].search([
            ('karma_id', '=', karma_line.karma_id.id),
            ('field_id', '=', karma_line.field_id.id),
            ('condition', '=', karma_line.condition),
            ('result_if_true', '=', karma_line.result_if_true),
            ('result_if_false', '=', karma_line.result_if_false),
            ('weighting', '=', karma_line.weighting),
        ], order='id desc', limit=1)

        def karma_line_matches_condition_label(lang):
            return (
                condition.with_context(lang=lang.code).condition_label ==
                karma_line.with_context(lang=lang.code).condition_label
            )

        matches_labels = all(karma_line_matches_condition_label(lang) for lang in self._langs)
        return condition if matches_labels else None

    def _create_score_condition(self, karma_line):
        condition = self._env['karma.score.condition'].create({
            'karma_id': karma_line.karma_id.id,
            'condition_label': karma_line.condition_label,
            'field_id': karma_line.field_id.id,
            'condition': karma_line.condition,
            'result_if_true': karma_line.result_if_true,
            'result_if_false': karma_line.result_if_false,
            'weighting': karma_line.weighting,
        })

        # Translate the condition in every languages.
        for lang in self._langs:
            condition.with_context(lang=lang.code).write({
                'condition_label': karma_line.with_context(lang=lang.code).condition_label,
            })

        return condition
