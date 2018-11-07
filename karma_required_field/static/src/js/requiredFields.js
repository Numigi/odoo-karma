odoo.define("karma_required_field.requiredFields", function(require){

var ajax = require("web.ajax");
var Class = require("web.Class");

var KarmaRequiredFieldRegistry = Class.extend({
    init(){
        this._deferred = new $.Deferred();
        this._fieldsFetched = false;
        this._requiredFields = new Set();
    },
    /**
     * Get an array of filter values for the given model.
     *
     * @param {String} model: the model name
     * @param {String} fieldName: the name of the field
     */
    isFieldRequired(model, fieldName){
        var self = this;

        var index = model + ',' + fieldName;

        if(!this._fieldsFetched){
            this._fetchfields().then(function(){
                self._deferred.resolve();
            });
            this._fieldsFetched = true;
        }

        return $.when(this._deferred).then(function(){
            return self._requiredFields.has(index);
        });
    },
    /**
     * Fetch the fields from the server.
     *
     * All fields are cached on the first query.
     * This method is called only one time per session.
     */
    _fetchfields(){
        var self = this;
        return ajax.rpc("/web/dataset/call_kw/karma.required.field/get_required_field_list", {
            model: "karma.required.field",
            method: "get_required_field_list",
            args: [],
            kwargs: {},
        }).then(function(result){
            result.forEach(function(values){
                self._requiredFields.add(values.model + ',' + values.field);
            });
        });
    },
});

var requiredFieldRegistry = new KarmaRequiredFieldRegistry();

return {
    isFieldRequired(model, fieldName){
        return requiredFieldRegistry.isFieldRequired(model, fieldName)
    },
}

});
