odoo.define("karma_required_field.logKarmaRequiredFieldsOnSave", function(require){

var rpc = require("web.rpc");

/**
 * Determine whether the given field value is empty-like or not.
 *
 * A many2many field is empty if the array is empty.
 */
function isEmptyFieldValue(value){
    var isMany2manyEmptyValue = (
        value &&
        value.type === "list" &&
        value.res_ids.length === 0
    );
    if(isMany2manyEmptyValue){
        return !value.length;
    }
    return !value;
}

function isRequiredFieldWidget(widget){
    return widget.$el.find('.o-karma-required').length || widget.$el.hasClass('o-karma-required');
}

function isInvisibleFieldWidget(widget){
    return widget.$el.parents('.o_invisible_modifier').length || widget.$el.hasClass('o_invisible_modifier');
}

/**
 * After saving the form view, trigger the computation of the karma for the record.
 */
require("web.FormController").include({
    /**
     * Keep track of the initial values of the records managed by the controller.
     *
     * The same controller is used in Odoo to controller multiple form records.
     * Each record is called a `state`.
     * The initial values are tracked per `state` in the attribute _initialValues.
     *
     * When saving the form, we are then able to compare the difference between the
     * values before and after the changes done by the user.
     */
    init() {
        this._super.apply(this, arguments);
        this._initialValues = {};
    },
    /**
     * This method is called when the user:
     *  - opens the form view
     *  - switches from a record to another
     *  - clicks on edit/save/create
     *
     * At this point, we are able to make a copy of the record to keep track of changes.
     */
    _update(state){
        this._initialValues[this.renderer.state.id] = Object.assign({}, state.data);
        return this._super.apply(this, arguments);
    },
    /**
     * When a record is saved, log the karma required fields that changed.
     */
    saveRecord(){
        var karmaFields = this._getAvailableKarmaFieldWidgets();

        var initialValues = this._initialValues[this.renderer.state.id];
        var initialEmptyFields = karmaFields.filter((f) => isEmptyFieldValue(initialValues[f.name]));

        var finalValues = this.renderer.state.data;
        var finalEmptyFields = karmaFields.filter((f) => isEmptyFieldValue(finalValues[f.name]));

        var deferred = this._super.apply(this, arguments);
        deferred.then((record) => {
            if(initialEmptyFields.length || finalEmptyFields.length){
                this._logKarmaRequiredFields(initialEmptyFields, finalEmptyFields);
            }
        });
        return deferred;
    },
    /**
     * Get all field widgets that are `colorized` and visible.
     */
    _getAvailableKarmaFieldWidgets(){
        var fields = this.renderer.state.fields;
        var allFieldWidgets = this.renderer.allFieldWidgets[this.renderer.state.id];
        var availableKarmaFieldWidgets = allFieldWidgets.filter(
            (w) => isRequiredFieldWidget(w) && !isInvisibleFieldWidget(w));
        return availableKarmaFieldWidgets.map((w) => fields[w.attrs.name]);
    },
    /**
     * Log the given karma fields on the server.
     *
     * @param {Array<Object>} initialEmptyFields - the fields that were empty before editing the record.
     * @param {Array<Object>} finalEmptyFields - the fields that were empty after editing the record.
     */
    _logKarmaRequiredFields(initialEmptyFields, finalEmptyFields){
        var initialEmptyFieldsNames = initialEmptyFields.map((f) => f.name);
        var finalEmptyFieldsNames = finalEmptyFields.map((f) => f.name);
        var recordModel = this.renderer.state.model;
        var recordId = this.renderer.state.res_id;
        rpc.query({
            model: "karma.required.field.log",
            method: "log",
            args: [recordModel, recordId, initialEmptyFieldsNames, finalEmptyFieldsNames],
        });
    },
});

});
