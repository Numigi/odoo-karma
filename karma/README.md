# Karma

Karma is a module that allows to compute and present scores for any type of object.

## The Karma Object

The Karma object represents the computation of a score for a given model.

Karmas are recursive, meaning that a Karma can be composed of children Karmas.

### Inherited Karma

An `Inherited Karma` is a Karma composed of children Karmas.
The score of this type of Karma is a weighting of the score of each child karma.

### Simple Karma

A `Simple Karma` is a Karma computed based on formulas (we call these formulas `Conditions`).
Each of these karmas are leaf nodes in the tree of karma inheritance.

![Karma Conditions](static/description/karma_conditions.png?raw=true)

## Conditions

A condition is similar to an `IF` formula in `Excel`.

It is composed of:

* a field (Description)
* a condition to evaluate (Condition)
* a `value if` the condition is `reached` (Result If True)
* a `value if` the condition is `not reached` (Result If False)

The column `Target` is a text shown to the final user to explain his score.

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

| Description | Condition | Value if True | Value if False |
|-------------|-----------|---------------|----------------|
| Number of products sold (previous month) | value > 10 | value / 10 | 0 |

The condition above means:

* If a customer bougth more than 10 different products in a month,
* Then he gets a score equal to the number of products bought divided by 10.

Now, let's suppose we would like to add an upper boundary for the potential score to reach.

| Description | Condition | Value if True | Value if False |
|-------------|-----------|---------------|----------------|
| Number of products sold (previous month) | value > 10 | min(value / 10, 5) | 0 |

The expression `min(value / 10, 5)` states that the maximum score attainable for this condition is 5 points.

#### Number of elements

For a field containing multiple items (i.e. Tags on a partner), you may use the function `len` to compute
the expression based on the number of items.

Here is an example with partner tags.

| Description | Condition | Value if True | Value if False |
|-------------|-----------|---------------|----------------|
| Tags | len(value) >= 2 | 5 | 0 |

The condition above means:

* If a partner has at least 2 tags,
* Then he gets a score of 5.

#### Presence of word in text

For a text field, it is possible to check whether the field contains a specific word (or expression).

Here is an example with partner emails.

| Description | Condition | Value if True | Value if False |
|-------------|-----------|---------------|----------------|
| Email | `@` in value | 1 | -10 |

The condition above means:

* If the email of a partner contains the symbol `@`,
* Then he gets a score of 1.
* Otherwise he gets a score of -10.

#### Standard Python Function

Here is a list of standard python functions available for the expressions:

* abs
* all
* any
* len
* max
* min
* round
* sum

These functions are documented here:

https://docs.python.org/3.5/library/functions.html

### Ponderation

The `Ponderation` column contains a factor by which to multiply the value obtained
(either by the `Value if True` or `Value if False` column).

| Description | Condition | Value if True | Value if False | Ponderation |
|-------------|-----------|---------------|----------------|-------------|
| Number of products sold (previous month) | value | min(value / 10, 1) | 0 | 5 |
| Total amount ordered (previous month) | value | min(value / 1000, 1) | 0 | 10 |

Suppose the following values for the previous month for a partner:

Number of products sold: 20
Total amount ordered: 55000

The result will be:

* `min(3 / 10, 1) * 5 -> 0.3 * 5 -> 1.5`
* `min(1500 / 1000, 1) * 10 -> 1 * 10 -> 10`

The 2 conditions are equivalent to:

| Description | Condition | Value if True | Value if False | Ponderation |
|-------------|-----------|---------------|----------------|-------------|
| Number of products sold (previous month) | value | min(`value * 5` / 10, 1) | 0 | 1 |
| Total amount ordered (previous month) | value | min(`value * 10` / 1000, 1) | 0 | 1 |

The purpose of the extra column `Ponderation` is to relax the syntax of the python expressions.

## Filters

The `Filters` tab is used to restrain the karma to a given domain of records.

In the following example, the karma is only applied to customers.

![Karma Filters](static/description/karma_filters.png?raw=true)

## Compute Button

The `Compute` button allows to compute the scores for every records targeted by the karma.

![Compute Button](static/description/compute_button.png?raw=true)

## Score Details

The `Score Details` smart button shows the list of scores computed for the active karma.

![Score Details Button](static/description/score_details_button.png?raw=true)

![Score Details List](static/description/score_details_list.png?raw=true)

## Karma Widget

The `Karma Widget` is a widget displayed on the form view of any kind of object.

![Contact Form](static/description/contact_form.png?raw=true)

### Application Specific Modules

A series of modules are available that add the karma widget to specific applications:

* `karma_crm`: Pipelines and Leads
* `karma_partner`: Contacts
* `karma_product`: Product Templates and Variants
* `karma_project`: Projects and Tasks

The only thing these modules do is to position the karma widget inside the form views.
Which karma should be displayed is entirely configurable through the `Karma` app.

### Display On Form View

The `Display On Form View` checkbox on the karma allows to display the `Karma Widget` on the form view of the given model.

![Display On Form View](static/description/display_on_form_view.png?raw=true)

When checking this box, the field `Label` becomes required. This field defines the text that appears in the bottom of the widget.

### Multiple Widgets Per Object

You may define a Karma object that applies to customers and one that applies to suppliers.
In case one contact is both a customer and a supplier, the 2 widgets will appear next to each other.

### Score Drilldown

When clicking on the score itself, the details that compose the score is shown.

![Score Drilldown Button](static/description/score_drilldown_button.png?raw=true)

![Score Drilldown Details](static/description/score_drilldown_details.png?raw=true)

### History

When clicking on `History`, the complete history of scores computed for the record is shown.

![History Button](static/description/history_button.png?raw=true)

![History List](static/description/history_list.png?raw=true)

Then, when clicking on the score of a row, the details for that row will be displayed.

## Cron Schedule

One important feature of karma is to periodically recompute the score for all targeted records based
on a `daily / weekly / monthly` schedule.

![Cron Schedule](static/description/cron_schedule.png?raw=true)

To activate the cron for a given karma object, the only thing to do is select a value in the `Cron Schedule` field.

## Compute On Save

When checking `Compute On Save` on the karma settings, the score is recomputed for a record when
clicking on `Save` from the form view of the record.

![Compute On Save](static/description/compute_on_save_checkbox.png?raw=true)

## Anticipate Computation

When checking `Authorize Anticipate Computation` on the karma settings, a refresh icon is displayed
on the karma widget. When clicking on the icon, the score is recomputed for the active record.

![Anticipate Computation Checkbox](static/description/anticipate_computation_checkbox.png?raw=true)

![Anticipate Computation Button](static/description/anticipate_computation_button.png?raw=true)

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
