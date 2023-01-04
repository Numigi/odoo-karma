# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .condition import ConditionKarmaComputer
from .inherited import InheritedKarmaComputer

from . import (
    karma_with_compute,
    karma_with_anticipate_computation,
    karma_with_computation_job,
    karma_with_computation_scheduling,
    karma_with_compute_on_save,
    karma_with_number_evaluated_lines,
)
