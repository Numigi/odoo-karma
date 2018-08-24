# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import functools
import logging
import uuid

from datetime import datetime

from odoo import models
from odoo.addons.queue_job.job import job
from .condition import KarmaConditionEvaluationError
from ..computation import ConditionKarmaComputer, InheritedKarmaComputer

_logger = logging.getLogger(__name__)


class KarmaWithScoreComputingJob(models.Model):
    """Add cron jobs to karmas."""

    _inherit = 'karma'

    @job
    def compute_all_scores(self, raise_=False):
        """Compute the scores for all records targeted by the karma.

        :param raise_: whether to raise the exception when a single computation fails.

            raise_=False prevents a complete rollback if a computation error happens
            for a single record.

            raise_=True can be used for testing purposes.
        """
        records = self._get_targeted_records()
        computer = self._get_score_computer()
        session = self.env['karma.session'].create({
            'karma_id': self.id,
            'start_time': datetime.now(),
            'number_of_records': len(records),
        })

        scores = self.env['karma.score']

        for record in records:
            compute_func = functools.partial(computer.compute, record)
            context_managers = [
                KarmaErrorLogContextManager(session, record),
                SavepointContextManager(self.env),
            ]

            if not raise_:
                context_managers.insert(0, IgnoreConditionEvaluationContextManager())

            score = call_with_context_managers(compute_func, context_managers)
            if score is not None:
                scores |= score

        scores.write({'session_id': session.id})

        session.end_time = datetime.now()
        self.write({
            'last_cron_date': datetime.now().date(),
            'force_next_cron_date': False,
        })

    def _get_targeted_records(self):
        domain = self._get_domain()
        return self.env[self.model_id.model].search(domain)

    def _get_score_computer(self):
        computer_cls = (
            InheritedKarmaComputer if self.type_ == 'inherited' else ConditionKarmaComputer
        )
        return computer_cls(self)


def call_with_context_managers(func, managers):
    """Call a given function with all given context managers.

    This function replaces nested context managers.

    The following:

    with manager_one:
        with manager_to:
            with manager_3:
                do something

    Is simplified to:

    call_with_context_managers(do_something, [manager_one, ...])
    """
    if not managers:
        return func()

    next_manager = managers[0]
    with next_manager:
        return call_with_context_managers(func, managers[1:])


class SavepointContextManager:
    """Class that allows to run a nested transaction given an environment."""

    def __init__(self, env):
        self._env = env
        self._cr = env.cr
        self._savepoint_id = 'savepoint_{sid}'.format(sid=uuid.uuid4().hex)

    def __enter__(self):
        self._begin_nested()

    def __exit__(self, type_, value, traceback):
        if value:
            self._rollback()
            return False
        else:
            self._release()
            return True

    def _begin_nested(self):
        self._cr.execute('SAVEPOINT {sp}'.format(sp=self._savepoint_id))

    def _rollback(self):
        self._cr.execute('ROLLBACK TO SAVEPOINT {sp}'.format(sp=self._savepoint_id))
        self._env.clear()

    def _release(self):
        self._cr.execute('RELEASE SAVEPOINT {sp}'.format(sp=self._savepoint_id))


class KarmaErrorLogContextManager:

    def __init__(self, session, record):
        self._session = session
        self._record = record

    def __enter__(self):
        pass

    def __exit__(self, type_, value, traceback):
        if value:
            self._log_error_in_syslogs(value)
            self._create_error_log_record(value)
            return False
        else:
            return True

    def _log_error_in_syslogs(self, err):
        message = (
            'An error happened while computing the score of the Karma {karma} '
            'for the record with ID={record_id}.\n\n{err}'
            .format(
                karma=self._session.karma_id.display_name,
                record_id=self._record.id,
                err=repr(err)
            )
        )
        _logger.error(message)

    def _create_error_log_record(self, err):
        self._session.env['karma.error.log'].create({
            'karma_id': self._session.karma_id.id,
            'res_id': self._record.id,
            'res_model': self._record._name,
            'error_message': repr(err),
            'session_id': self._session.id,
        })


class IgnoreConditionEvaluationContextManager:
    """A context manager that ignores errors related to condition evaluation."""

    def __enter__(self):
        pass

    def __exit__(self, type_, value, traceback):
        if value:
            error_should_be_ignored = isinstance(value, KarmaConditionEvaluationError)
            return error_should_be_ignored

        return True
