odoo.define("karma.computationOnSave", function(require){

require("web.BasicModel").include({
    /**
     * After saving the record, trigger the computation of the karma for the record.
     *
     * The score must not be computed in the case of a virtual record.
     * Virtual records are used to represent a record that was not already created.
     * Instead of an integer ID, a virtual record has a string ID starting with `virtual_`.
     *
     * @param {String} recordId - a client side identifier of the record.
     *     This identifier is not related to the database ID of the record.
     */
    save(recordId){
        var saveDeferred = this._super.apply(this, arguments);
        var scoreDeferred = $.Deferred();
        var self = this;
        saveDeferred.then(function(){
            var record = self.localData[recordId];

            var isVirtualRecord = typeof record.res_id === "string";
            if(isVirtualRecord){
                scoreDeferred.resolve();
            }
            else{
                self.triggerKarmaScoreComputation(record.model, record.res_id).then(function(){
                    scoreDeferred.resolve();
                });
            }
        });
        return $.when(saveDeferred, scoreDeferred);
    },
    /**
     * Trigger the computation of karma scores for the given record.
     *
     * @param {Object} modelName - the model of the record for which to compute scores.
     * @param {Object} recordId - the ID of the record for which to compute scores.
     */
    triggerKarmaScoreComputation(modelName, recordId){
        return this._rpc({
            route: "/web/dataset/call_kw/karma/compute_score_on_save",
            params: {
                model: "karma",
                method: "compute_score_on_save",
                args: [modelName, recordId],
                kwargs: {},
            }
        });
    },
});

require("web.KanbanModel").include({
    /**
     * When adding a record from a kanban column, trigger the karma computation.
     */
    addRecordToGroup(groupID, resId){
        var result = this._super.apply(this, arguments);
        var group = this.localData[groupID];
        this.triggerKarmaScoreComputation(group.model, resId);
        return result;
    }
});

});
