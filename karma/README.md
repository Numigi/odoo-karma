# Karma

Karma is a module that allows to compute and present scores for any type of object.

## The Karma Object

The Karma object represents the computation of a score for a given model.

Karmas are recursive, meaning that a Karma can be composed of children Karmas.

### Inherited Karma

An `Inherited Karma` is a Karma composed of children Karmas.
The score of this type of Karma is a weighting of the score of each child karma.

### Ad Hoc Karma

An `Ad Hoc Karma` is a Karma computed based on formulas (we call these formulas `Conditions`).
Each of these karmas are leaf nodes in the tree of karma inheritance.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

The Karma app logo was taken from font-awesome and adapted:

https://fontawesome.com/icons/crown

More information
----------------
* Meet us at https://bit.ly/numigi-com
