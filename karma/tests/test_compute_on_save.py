# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .test_condition_computation import ComputedKarmaCase


class ComputeKarmaOnSave(ComputedKarmaCase):

    def test_ifComputeOnSaveDisabled_thenScoreIsNotComputed(self):
        self.karma.compute_on_save = False

        self.env['karma'].compute_score_on_save('res.partner', self.partner.id)
        assert not self._find_last_score(self.partner)

    def test_ifComputeOnSaveEnabled_thenScoreIsComputed(self):
        self.karma.compute_on_save = True

        self.env['karma'].compute_score_on_save('res.partner', self.partner.id)
        assert self._find_last_score(self.partner)

    def test_ifRecordIsExcludedByDomain_thenScoreIsNotComputed(self):
        self.karma.compute_on_save = True
        self.karma.domain = "[('customer', '=', True)]"
        self.partner.customer = False

        self.env['karma'].compute_score_on_save('res.partner', self.partner.id)
        assert not self._find_last_score(self.partner)

    def test_ifRecordIsIncludedByDomain_thenScoreIsNotComputed(self):
        self.karma.compute_on_save = True
        self.karma.domain = "[('customer', '=', True)]"
        self.partner.customer = True

        self.env['karma'].compute_score_on_save('res.partner', self.partner.id)
        assert self._find_last_score(self.partner)

    def test_ifComputationTriggered_scoreIsNotComputedForOtherRecords(self):
        self.karma.compute_on_save = True

        self.env['karma'].compute_score_on_save('res.partner', self.partner.id)
        assert not self._find_last_score(self.partner_2)
