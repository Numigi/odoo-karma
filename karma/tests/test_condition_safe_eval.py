# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from decimal import Decimal

from odoo.tests.common import TransactionCase
from ..safe_eval import safe_eval


class TestConditionSafeEval(TransactionCase):
    """Test that python expressions evaluation available in karma are safe."""

    def test_builtin_functions_are_callable(self):
        assert safe_eval('len(user)', {'user': self.env.user}) == 1

    def test_arithmetic_expressions_can_be_evaluated(self):
        assert safe_eval('value * 50 / 100', {'value': Decimal(80)}) == 40

    def test_attributes_of_objects_are_not_accessible(self):
        with pytest.raises(ValueError):
            safe_eval('user.env', {'user': self.env.user})

    def test_attributes_of_objects_are_not_accessible_through_key_map(self):
        with pytest.raises(ValueError):
            safe_eval('user["login"]', {'user': self.env.user})

    def test_attributes_of_objects_can_not_be_set(self):
        with pytest.raises(ValueError):
            safe_eval('setattr(user, "login", "admin")', {'user': self.env.user})

    def test_attributes_of_objects_can_not_be_accessed_with_getattr(self):
        with pytest.raises(ValueError):
            safe_eval('getattr(user, "login")', {'user': self.env.user})
