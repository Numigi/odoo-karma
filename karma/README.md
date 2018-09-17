# Karma

Karma is a module that allows to compute and present scores for any type of object.

## The Karma Object

The Karma object represents the computation of a score for a given model.

Karmas are recursive, meaning that a Karma can be composed of children Karmas.

### Inherited Karma

An `Inherited Karma` is a Karma composed of children Karmas.
The score of this type of Karma is a weighting of the score of each child karma.

### Simple Karma

An `Simple Karma` is a Karma computed based on formulas (we call these formulas `Conditions`).
Each of these karmas are leaf nodes in the tree of karma inheritance.

## Conditions

A condition is similar to an `IF` formula in `Excel`.

It is composed of:

* a field
* a condition to evaluate
* a `value if` the condition is `reached`
* a `value if` the condition is `not reached`

### Fields

The selected field can be any type of field (computed or stored).
For example, the field could be the number of sale orders of a partner for the previous month (if such field exists).

The Karma application does not define how fields are computed on a model.
The module `date_range_field_template` defines an easy way to create new fields based on time ranges.

### Python Expressions

The conditions are python expressions.
The syntax is however restricted to basic arithmetic operations and functions.

When evaluated, the expression receives the variable `value` which contains the value of the field.

If the field evaluated is the `Email` of a partner, `value` would contain the email address of the partner.
If the field evaluated is the `Tags` of a partner, `value` would contain a recordset of partner tags.

#### Arithmetic Operations

Basic arithmetic operations are available.

If the field contains a number, you could for example have the python expression `value > 10` which means
`True if the field value is greater than 10`.

| Field | Condition | Value if True | Value if False |
|-------|-----------|---------------|----------------|
| Number of products sold (previous month) | value > 10 | value / 10 | 0 |

The condition above means:

* If a customer bougth more than 10 different products in a month,
* Then he gets a score equal to the number of products bought divided by 10.

Now, let's suppose we would like to add an upper boundary for the potential score to reach.

| Field | Condition | Value if True | Value if False |
|-------|-----------|---------------|----------------|
| Number of products sold (previous month) | value > 10 | max(value / 10, 5) | 0 |

The expression `max(value / 10, 5)` states that the max score attainable for this condition is 5 points.

#### Number of elements

For a field containing multiple items (i.e. Tags on a partner), you may use the function `len` to compute
the expression based on the number of items.

Here is an example with partner tags.

| Field | Condition | Value if True | Value if False |
|-------|-----------|---------------|----------------|
| Tags | len(value) >= 2 | 5 | 0 |

The condition above means:

* If a partner has at least 2 tags,
* Then he gets a score of 5.

### Ponderation

The `Ponderation` column contains a factor by which to multiply the value obtained
(either by the `Value if True` or `Value if False` column).

| Field | Condition | Value if True | Value if False | Ponderation |
|-------|-----------|---------------|----------------|-------------|
| Number of products sold (previous month) | value | max(value / 10, 1) | 0 | 5 |
| Total amount ordered (previous month) | value | max(value / 1000, 1) | 0 | 10 |

Suppose the following values for the previous month for a partner:

Number of products sold: 20
Total amount ordered: 55000

The result will be:

* `max(3 / 10, 1) * 5 -> 0.3 * 5 -> 1.5`
* `max(1500 / 1000, 1) * 10 -> 1 * 10 -> 10`

The 2 conditions are equivalent to:

| Field | Condition | Value if True | Value if False | Ponderation |
|-------|-----------|---------------|----------------|-------------|
| Number of products sold (previous month) | value | max(`value * 5` / 10, 1) | 0 | 1 |
| Total amount ordered (previous month) | value | max(`value * 10` / 1000, 1) | 0 | 1 |

The purpose of the extra column `Ponderation` is to relax the syntax of the python expressions.

## Extending Karma

It is possible to easily extend the score computation.
This is done through the method `_compute` of the model `karma` which serves as a hook for that purpose.

```python
from odoo import api, models

class KarmaWithExtraComputationBehavior(models.Model):

    _inherit = 'karma'

    @api.model
    def _compute(self, computer, record):
        new_score = computer.compute(record)
        ...  # do extra computation
        return new_score
```

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

The Karma app logo was taken from font-awesome and adapted:

https://fontawesome.com/icons/crown

More information
----------------
* Meet us at https://bit.ly/numigi-com
