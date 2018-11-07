odoo.define("karma_required_field.colorize", function(require){

var isFieldRequired = require("karma_required_field.requiredFields").isFieldRequired;

var targetElements = ["input", "select", "textarea", ".o_field_many2manytags"].join(',')

/**
 * Colorize the given field element.
 *
 * @param {jQueryElement} - the DOM element of the field
 */
function _colorizeInput(element){
    var inputElement = element.find(targetElements).addBack(targetElements);
    inputElement.addClass("o-karma-required");
}

function _renderEditWithKarmaColorize(){
    var deferred = this._super.apply(this, arguments);

    var model = this.record.model;
    var fieldName = this.field.name || this.attrs.name;
    isFieldRequired(model, fieldName).then((isRequired) => {
        if(isRequired){
            _colorizeInput(this.$el);
        }
    });

    return deferred;
}

/**
 * After saving the form view, trigger the computation of the karma for the record.
 */
 var basicFields = require("web.basic_fields");

basicFields.InputField.include({
    _renderEdit: _renderEditWithKarmaColorize,
});

basicFields.FieldDate.include({
    _renderEdit: _renderEditWithKarmaColorize,
});

basicFields.FieldDateTime.include({
    _renderEdit: _renderEditWithKarmaColorize,
});

var relationalFields = require("web.relational_fields");
relationalFields.FieldMany2One.include({
    _renderEdit: _renderEditWithKarmaColorize,
});

relationalFields.FieldMany2ManyTags.include({
    _renderEdit: _renderEditWithKarmaColorize,
});

relationalFields.FieldSelection.include({
    _renderEdit: _renderEditWithKarmaColorize,
});


/**
 * Colorize the notebook tabs on the form view if the page contains any required field.
 */
require("web.FormRenderer").include({
    _render(){
        this._pageElements = [];
        var deferred = this._super.apply(this, arguments);
        if(this.mode === "edit"){
            deferred.then(() => {
                /**
                 * Update the color of the notebook pages.
                 *
                 * Whether the page must be colorized or not depends on whether
                 * at least one field is colorized inside the page.
                 *
                 * The fields and other elements of the view are rendered asynchronously.
                 * Therefore, it is very hard to determine the exact moment
                 * where the form is completely rendered. This moment usually happens
                 * between 200 and 300 ms.
                 *
                 * We check every 100 ms for the first 2 second if the pages must be colorized
                 * or not.
                 */
                var delays = [...Array(21).keys()].map((i) => i * 100);  // [0, 100, 200...2000]
                delays.forEach((delay) => {
                    setTimeout(() => this._updateTabHeaderKarmaColors(), delay);
                });
            });
        }
        return deferred;
    },
    _renderTabHeader(page, page_id) {
        var element = this._super.apply(this, arguments);
        this._pageElements.push([element, page_id]);
        return element;
    },
    /**
     * Update the color of a single notebook page.
     *
     * @param {jQuery} tabHeaderElement - the tab header element
     * @param {String} pageId - the DOM id of the page to update
     */
    _updateSingleTabHeaderKarmaColors(tabHeaderElement, pageId){
        var pageElement = this.$el.find('.tab-pane#' + pageId);

        function elementHasNoInvisibleParent(){
            var invisibleParents = $(this).parents('.o_invisible_modifier');
            return !invisibleParents.length;
        }

        var mustBeColorized = Boolean(
            pageElement.find('.o-karma-required:not(.o_invisible_modifier)')
            .filter(elementHasNoInvisibleParent).length
        );
        if(mustBeColorized){
            if(!tabHeaderElement.hasClass("o-karma-required-page")){
                tabHeaderElement.addClass("o-karma-required-page");
            }
        }
        else{
            if(tabHeaderElement.hasClass("o-karma-required-page")){
                tabHeaderElement.removeClass("o-karma-required-page");
            }
        }
    },
    /**
     * Update the color on all notebook pages.
     */
    _updateTabHeaderKarmaColors(){
        this._pageElements.forEach((pageElementIDTuple) => {
            var tabHeaderElement = pageElementIDTuple[0];
            var pageId = pageElementIDTuple[1];
            this._updateSingleTabHeaderKarmaColors(tabHeaderElement, pageId);
        });
    },
    /**
     * Update tab colors after a field value was changed.
     *
     * When a field is changed, some karma fields previously not editable
     * may now be editable.
     */
    _updateAllModifiers(){
        var deferred = this._super.apply(this, arguments);
        deferred.then(() => this._updateTabHeaderKarmaColors());
        return deferred;
    },
});

});
