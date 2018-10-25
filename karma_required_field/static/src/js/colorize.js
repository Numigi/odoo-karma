odoo.define("karma_required_field.colorize", function(require){

var isFieldRequired = require("karma_required_field.requiredFields").isFieldRequired;

var targetElements = [
    "input",
    "select",
    "textarea",
    ".o_field_many2manytags",
].join(',')

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

function _getChildrenNodes(node, tagName){
    var result = [];

    function _findChildFieldsRecursively(child){
        if(child.tag === tagName){
            result.push(child);
        }
        else if(child.children){
            child.children.forEach((c) => _findChildFieldsRecursively(c));
        }
    }
    _findChildFieldsRecursively(node);

    return result;
}

/**
 * Colorize notebook tabs when any field inside the page is colored.
 *
 * @param {jQueryElement} - the DOM element of the notebook page 
 */
require("web.FormRenderer").include({
    _render(){
        this._pageElements = [];
        var deferred = this._super.apply(this, arguments);
        if(this.mode === "edit"){
            deferred.then(() => {
                this._updatePageKarmaColors();
                setTimeout(() => this._updatePageKarmaColors(), 100);
                setTimeout(() => this._updatePageKarmaColors(), 200);
                setTimeout(() => this._updatePageKarmaColors(), 300);
                setTimeout(() => this._updatePageKarmaColors(), 400);
                setTimeout(() => this._updatePageKarmaColors(), 500);
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
     * Update tab colors after a field value was changed.
     *
     * When a field is changed, some karma fields previously not editable
     * may now be editable.
     */
    _updateAllModifiers(){
        var deferred = this._super.apply(this, arguments);
        deferred.then(() => this._updatePageKarmaColors());
        return deferred;
    },
    _updatePageKarmaColors(){
        this._pageElements.forEach((pageElementIDTuple) => {
            this._colorizeIfAnyChildFieldRequired(pageElementIDTuple);
        });
    },
    _colorizeIfAnyChildFieldRequired(pageElementIDTuple){
        var pageElement = pageElementIDTuple[0];
        var pageId = pageElementIDTuple[1];
        var page = this.$el.find('.tab-pane#' + pageId);

        var mustBeColorized = Boolean(page.find('.o-karma-required:not(.o_invisible_modifier)').length)
        if(mustBeColorized){
            if(!pageElement.hasClass("o-karma-required-page")){
                pageElement.addClass("o-karma-required-page");
            }
        }
        else{
            if(pageElement.hasClass("o-karma-required-page")){
                pageElement.removeClass("o-karma-required-page");
            }
        }
    },
});

});
