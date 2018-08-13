# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo import fields
from odoo.tests.common import SavepointCase


class BasicKarmaHierarchyCase(SavepointCase):
    """Test Case with a basic Karma hierarchy with no condition lines.

    K1
    |
    -----
    |   |
    K2  K3
    |
    ---------
    |   |   |
    K4  K5  K6

    This test case has no condition lines because how a karma is
    computed is not relevant for testing the scheduling of karmas.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.karma_1 = cls.env['karma'].create({
            'name': 'Karma 1',
            'type_': 'inherited',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'cron_schedule': 'daily',
        })

        cls.karma_2 = cls.env['karma'].create({
            'name': 'Karma 2',
            'type_': 'inherited',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'cron_schedule': 'daily',
        })

        cls.karma_3 = cls.env['karma'].create({
            'name': 'Karma 3',
            'type_': 'condition',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'cron_schedule': 'daily',
        })

        cls.karma_4 = cls.env['karma'].create({
            'name': 'Karma 4',
            'type_': 'condition',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'cron_schedule': 'daily',
        })

        cls.karma_5 = cls.env['karma'].create({
            'name': 'Karma 5',
            'type_': 'condition',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'cron_schedule': 'daily',
        })

        cls.karma_6 = cls.env['karma'].create({
            'name': 'Karma 6',
            'type_': 'condition',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'cron_schedule': 'daily',
        })

        for (parent, child) in [
            (cls.karma_1, cls.karma_2),
            (cls.karma_1, cls.karma_3),
            (cls.karma_2, cls.karma_4),
            (cls.karma_2, cls.karma_5),
            (cls.karma_2, cls.karma_6),
        ]:
            cls.env['karma.line'].create({'karma_id': parent.id, 'child_karma_id': child.id})

    def _find_job(self, karma):
        job = self.env['queue.job'].search([
            ('model_name', '=', 'karma'),
            ('method_name', '=', 'compute_all_scores'),
        ]).filtered(lambda j: j.record_ids == [karma.id])
        assert job.ensure_one()
        return job


class TestKarmaComputationScheduling(BasicKarmaHierarchyCase):

    def test_schedule_computation(self):
        self.env['karma'].schedule_computation()

        job_1 = self._find_job(self.karma_1)
        job_2 = self._find_job(self.karma_2)
        job_3 = self._find_job(self.karma_3)
        job_4 = self._find_job(self.karma_4)
        job_5 = self._find_job(self.karma_5)
        job_6 = self._find_job(self.karma_6)

        assert job_1.eta > job_2.eta
        assert job_2.eta > fields.Datetime.to_string(datetime.now())

        assert not job_3.eta
        assert not job_4.eta
        assert not job_5.eta
        assert not job_6.eta


class TestKarmaSchedulingWithLoopInHierarchy(BasicKarmaHierarchyCase):
    """Test case with a more complex Karma structure inclusing a loop.

    We augment the basic karma hierarchy with 2 new karmas (K7 and K8).

    K1
    |
    -----
    |   |
    K2  K3
    |
    ---------
    |   |   |
    K4  K5  K6
    |
    -
    |
    K7
    |
    -----
    |   |
    K2  K8

    Now, their is now a loop in the structure K2 -> K4 -> K7 -> K2.

    K7 has a depth of 2: K7 -> K2 -> (K5, K6)
    K4 has a depth of 3: K4 -> K7 -> K2 -> (K5, K6)
    K2 has a depth of 3: K2 -> K4 -> K7 -> K8
    K1 has a depth of 4: K1 -> K2 -> K4 -> K7 -> K8

    Therefore, the expected execution order is:

     * K3, K5, K6, K8 (Ad Hoc Karmas)
     * K2, K4, K7
     * K1

    The precise order between K2, K4 and K7 is not important because they form
    a loop.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.karma_4.type_ = 'inherited'

        cls.karma_7 = cls.env['karma'].create({
            'name': 'Karma 7',
            'type_': 'inherited',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'cron_schedule': 'daily',
        })

        cls.karma_8 = cls.env['karma'].create({
            'name': 'Karma 8',
            'type_': 'condition',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'cron_schedule': 'daily',
        })

        cls.env['karma.line'].create({
            'karma_id': cls.karma_4.id, 'child_karma_id': cls.karma_7.id,
        })

        cls.env['karma.line'].create({
            'karma_id': cls.karma_7.id, 'child_karma_id': cls.karma_2.id,
        })

        cls.env['karma.line'].create({
            'karma_id': cls.karma_7.id, 'child_karma_id': cls.karma_8.id,
        })

    def test_schedule_computation_with_infinite_recursion(self):

        self.env['karma'].schedule_computation()

        job_1 = self._find_job(self.karma_1)
        job_2 = self._find_job(self.karma_2)
        job_3 = self._find_job(self.karma_3)
        job_4 = self._find_job(self.karma_4)
        job_5 = self._find_job(self.karma_5)
        job_6 = self._find_job(self.karma_6)
        job_7 = self._find_job(self.karma_7)
        job_8 = self._find_job(self.karma_8)

        assert not job_3.eta
        assert not job_5.eta
        assert not job_6.eta
        assert not job_8.eta

        now = fields.Datetime.to_string(datetime.now())

        assert job_2.eta > now
        assert job_4.eta > now
        assert job_7.eta > now

        assert job_1.eta > job_2.eta
        assert job_1.eta > job_4.eta
        assert job_1.eta > job_7.eta
