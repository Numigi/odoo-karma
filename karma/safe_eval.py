# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from opcode import opmap
from odoo.tools.safe_eval import (
    safe_eval as _odoo_safe_eval,
    test_expr as _odoo_test_expr,
)


_SAFE_OPCODES = frozenset(opmap[x] for x in [
    # Unary operators
    'UNARY_INVERT',
    'UNARY_NEGATIVE',
    'UNARY_NOT',
    'UNARY_POSITIVE',

    # Binary operators
    'BINARY_ADD',
    'BINARY_AND',
    'BINARY_FLOOR_DIVIDE',
    'BINARY_LSHIFT',
    'BINARY_MODULO',
    'BINARY_MULTIPLY',
    'BINARY_OR',
    'BINARY_POWER',
    'BINARY_SUBTRACT',
    'BINARY_TRUE_DIVIDE',
    'BINARY_XOR',

    # Enable comparisons
    'COMPARE_OP',

    # Enable to load variables
    'LOAD_CONST',
    'LOAD_NAME',

    # Op codes required for calling local and global functions
    'CALL_FUNCTION',

    # Enable returning the result of the expression
    'RETURN_VALUE',
])


def restricted_safe_eval(expr, locals_dict=None):
    """Safely eval the given expression.

    This function is much more restrictive than the safe_eval function in Odoo.

    It allows basic arithmetic operations and calling functions.

    The callable functions are those supplied in the locals dict, plus the
    standard python builins (len, abs, etc).

    :param expr: the expression to eval
    :param locals_dict: the dictionary containing the locals
    :return: the result of the evaluation
    """
    _odoo_test_expr(expr, _SAFE_OPCODES)
    return _odoo_safe_eval(expr, locals_dict=locals_dict)
