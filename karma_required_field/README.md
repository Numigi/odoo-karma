# Karma Required Fields

This module aims to encourage users to fill important fields in form views of any object.

A new concept of `Karma Field` is added.

![Karma Field List](static/description/karma_field_list.png?raw=true)

When added to the Karma field list, the field is colorized in the form view of the object.

![Partner Form](static/description/partner_form.png?raw=true)

It helps the user to quickly identify all important fields in the view.

An empty Karma field does not block a user from saving, in contrast to a true required field.

## Notebook Pages

If a Karma field is placed inside a notebook page, the tab will be colorized as well.

![Notebook Page](static/description/notebook_page.png?raw=true)

## Karma Score Based On Completion

The module allows to score a user based on his assiduity to fill the Karma fields.

When a form view is saved, the karma fields filled (or emptied) are logged.

This allows to use the core `Karma` features to score the user based on his
effort for filling the Karma fields.

### Invisible Fields

A field that the user can not see is never logged.
For example, if a field is visible only to the members of a group, it will not be logged for non-members.

### Readonly Fields

If a field is read-only, it will not be logged (it will not even be colorized).

### Usage

#### Setup Computed Fields

* Go to `Karma / Settings / Computed Fields`
* Select `Karma Field Average`

![Karma Field Average](static/description/karma_field_average.png?raw=true)

This computed field is added by the module in order to score the user based on the average
completion of the Karma fields for a given model over a specific period of time.

![Karma Field Average Form](static/description/karma_field_average_form.png?raw=true)

In the example above, we defined 4 fields on `res.users`.
Each of these fields computes the average completion of Karma fields, but with different parameters.

* 2 fields related to the completion of `Contacts`
* 2 fields related to the completion of `Leads`

The `Date Range` defines over what period of time the average completion ratio is based.

`Current Week` means that only the records modified between the `Sunday` and `Saturday` of the current week
are included in the computation.

#### Setup The User Karma

* Go to `Karma / Settings / Karma`

![Karma List](static/description/karma_list.png?raw=true)

* Create a Karma with following values:
  - Model: `Users (res.users)`
  - Type: `Simple`

![Karma Form](static/description/karma_form.png?raw=true)

For each model that you whish to score the field completion, you must add a condition line.

In the example above, the users will be scored over the completion of `Contacts (res.partner)` and `Leads (crm.lead)`.
The completion of `Leads` have an higher weighting than `Contacts`, thus will have an higher impact over the Karma score.

#### Edit An Object

* Go to the form view of a scored object

![Lead Form](static/description/lead_form.png?raw=true)

* Fill some Karma fields

![Lead Form Filled](static/description/lead_form_filled.png?raw=true)

#### Compute The Karma Score

* Now, go back to the user Karma.

![Karma Form Compute Score](static/description/karma_form_compute_score.png?raw=true)

* Click on `Compute`.
* Click on the `Score Details` smart button.

![Karma Score List](static/description/karma_score_list.png?raw=true)

* Drilldown to see the details of the Karma score.

![Karma Score Details](static/description/karma_score_details.png?raw=true)

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
