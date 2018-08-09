# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


class InheritedKarmaComputer:
    """This class defines how Inherited Karma scores are computed."""

    def __init__(self, karma):
        self._karma = karma
        self._env = karma.env
        self._total_weight = sum(l.weighting for l in karma.line_ids)

    def compute(self, record):
        """Compute the karma score for the given record.

        :param record: the record to process.
        :return: a `karma.score.inherited` record.
        """
        score_line = self._env['karma.score'].create({
            'karma_id': self._karma.id,
            'res_id': record.id,
            'res_model': record._name,
        })

        for line in self._karma.line_ids:
            self._create_score_detail_line(score_line, line, record)

        score_line.score = sum(l.result for l in score_line.inherited_detail_ids)

        return score_line

    def _create_score_detail_line(self, parent_score, karma_line, record):
        """Create a detail line for the given score line.

        :param parent_score: the `karma.score` record for which to create the detail lines.
        :param karma_line: the `karma.line` to process
        :param record: the record to process
        """
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

            child_score = self._find_most_recent_child_karma_score(karma_line, related_record)

            if child_score:
                vals['child_score_id'] = child_score.id
                vals['score'] = child_score.score
                vals['result'] = self._compute_child_line_result(karma_line, child_score.score)

        self._env['karma.score.inherited.detail'].create(vals)

    def _compute_child_line_result(self, karma_line, score):
        return (
            score * karma_line.weighting / self._total_weight
            if self._total_weight else 0
        )

    def _get_related_record(self, karma_line, record):
        """Get a record related to the processed record.

        If the given `karma.line` record has a field, then that field is used as a relation
        to find the related record.

        If the given `karma.line` record does not have a field, this means that the
        children karma uses the same record as the parent karma.

        :param karma_line: the `karma.line` to process
        :param record: the main record to process
        """
        return record[karma_line.field_id.name] if karma_line.field_id else record

    def _find_most_recent_child_karma_score(self, karma_line, related_record):
        """Find the most recent child karma score computed for the given record.

        :param karma_line: the `karma.line` for which to find the matching score
        :param related_record: the record related to the child karma.
        """
        return self._env['karma.score'].search([
            ('karma_id', '=', karma_line.child_karma_id.id),
            ('res_id', '=', related_record.id),
            ('res_model', '=', related_record._name),
        ], limit=1, order='id desc')
