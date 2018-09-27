odoo.define("karma.computationOnSave", function(require){

/**
 * After saving the form view, trigger the computation of the karma for the record.
 */
require("web.FormController").include({
    saveRecord(){
        var deferred = this._super.apply(this, arguments);
        deferred.then(() => this.triggerKarmaScoreComputation())
        return deferred;
    },
    triggerKarmaScoreComputation(){
        var recordModel = this.renderer.state.model;
        var recordId = this.renderer.state.res_id;
        this._rpc({
            route: "/web/dataset/call_kw/karma/compute_score_on_save",
            params: {
                model: "karma",
                method: "compute_score_on_save",
                args: [recordModel, recordId],
                kwargs: {},
            }
        });
    },
});

});
