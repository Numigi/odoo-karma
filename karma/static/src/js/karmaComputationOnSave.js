odoo.define("karma.computationOnSave", function(require){

/**
 * After saving the record, trigger the computation of the karma for the record.
 */
require("web.BasicModel").include({
    save(recordId){
        var saveDeferred = this._super.apply(this, arguments);
        var scoreDeferred = $.Deferred();
        var self = this;
        saveDeferred.then(function(){
            self.triggerKarmaScoreComputation(recordId).then(function(){
                scoreDeferred.resolve();
            });
        });
        return $.when(saveDeferred, scoreDeferred);
    },
    triggerKarmaScoreComputation(recordId){
        var record = this.localData[recordId];
        return this._rpc({
            route: "/web/dataset/call_kw/karma/compute_score_on_save",
            params: {
                model: "karma",
                method: "compute_score_on_save",
                args: [record.model, record.res_id],
                kwargs: {},
            }
        });
    },
});

});
