# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import abc


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
