# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import abc

from .safe_eval import restricted_safe_eval


class KarmaComputationError(Exception):
    pass


class AbstractKarmaComputer(metaclass=abc.ABCMeta):
    """Class responsible for computing the scores of a karma."""

    def __init__(self, karma):
        self._karma = karma
        self._env = karma.env

    @abc.abstractmethod
    def compute(self, record):
        """Compute the score of a karma for a single record.

        :param record: the record for which to compute the score.
        :return: a karma.score record
        """
        pass


class InheritedKarmaComputer(AbstractKarmaScoreComputer):

    def __init__(self, karma):
        super().__init__(karma)
        self._total_weight = sum(l.weighting for l in karma.line_ids)

    def compute(self, record):
        score_line = self._env['karma.score']

        for line in self._karma.line_ids:
            self._create_score_detail_line(score_line, line, record)

        return score_line

    def _create_score_detail_line(self, parent_score, karma_line, record):
        vals = {
            'score_id': parent_score.id,
            'res_id': None,
            'res_model': None,
            'child_score_id': None,
            'score': 0,
            'weighting': karma_line.weighting,
            'result': 0,
        }

        related_record = self._get_related_record(karma_line, record)

        if related_record:
            vals['res_id'] = related_record.id
            vals['res_model'] = related_record._name

            child_score = self._find_last_child_karma_score(karma_line, record)

            if child_score:
                vals['child_score_id'] = child_score.id
                vals['score'] = child_score.score
                vals['result'] = self._compute_child_line_result(karma_line, score)

        self._env['karma.score.inherited.detail'].create(vals)

    def _compute_child_line_result(self, karma_line, score):
        return (
            score * karma_line.weighting / self._total_weight
            if self._total_weight else 0
        )

    def _get_related_record(self, karma_line, record):
        return record[karma_line.field_id.name]

    def _find_last_child_karma_score(self, karma_line, related_record):
        return self._env['karma.score'].search([
            ('karma_id', '=', karma_line.karma_id.id),
            ('res_id', '=', related_record.id),
            ('res_model', '=', related_record._name),
        ], limit=1, order='id desc')


class ConditionKarmaComputer(AbstractKarmaScoreComputer):

    def __init__(self, karma):
        super().__init__(karma)
        self._conditions = {}

    def compute(self, record):
        score_line = self._env['karma.score']

        for line in self._karma.condition_line_ids:
            self._create_score_detail_line(score_line, line, record)

        return score_line

    def _create_score_detail_line(self, score_line, karma_line, record):
        condition = self._get_score_condition(karma_line)

        value = self._get_field_value(karma_line, record)

        condition_fulfilled = self._eval_expression(karma_line.condition, record)

        result_expression = (
            karma_line.result_if_true
            if condition_fulfilled else karma_line.result_if_false
        )
        score = self._eval_expression(result_expression, value)

        self._env['karma.score.computed.detail'].create({
            'score_id': parent_score.id,
            'condition_id': condition.id,
            'condition_fulfilled': condition_fulfilled,
            'score': score,
            'result': score * karma_line.weighting,
        })

    def _get_field_value(self, karma_line, record):
        return record[karma_line.field_id.name]

    def _get_score_condition(self, karma_line):
        if karma_line not in self._conditions:
            self._conditions[karma_line] = self._env['karma.score.condition'].create({
                'field_id': karma_line.field_id.id,
                'condition': karma_line.condition,
                'result_if_true': karma_line.result_if_true,
                'result_if_false': karma_line.result_if_false,
                'weighting': karma_line.weighting,
            })

        return self._conditions[karma_line]

    def _eval_expression(self, expression, value):
        try:
            return safe_eval(expression, {'value': value})
        except Exception as err:
            raise KarmaComputationError(_(
                'The following expression could not be evaluated with the value {value}. '
                '\n\n{expression}'
                '\n\n{err}'
            ).format(expression=expression, value=value, err=err))
