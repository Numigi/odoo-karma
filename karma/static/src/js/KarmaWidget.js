odoo.define("karma.KarmaWidget", function (require) {
"use strict";

var Widget = require("web.Widget");
var widgetRegistry = require("web.widget_registry");
var core = require("web.core");
var _t = core._t;

var KarmaWidget = Widget.extend({
    template: "KarmaWidget",
    events: {
        "click .o_karma_widget__score": "scoreDrilldown",
        "click .o_karma_widget__refresh": "computeScore",
        "click .o_karma_widget__history": "openHistory",
    },
    init(){
        this._super.apply(this, arguments);
        this.karmas = [];

        var form = this.getParent();
        if(form.state.res_id){
            this.refreshData();
        }
    },
    /**
     * Fetch the data from the server and refresh the widget.
     */
    async refreshData(){
        var form = this.getParent();
        this.karmas = await this._rpc({
            model: "karma",
            method: "find_karmas_to_display_on_form_view",
            args: [form.state.model, form.state.res_id],
        });

        var scoreDeferred = this.karmas.map(async (k) => {
            k.score = await this.findLastKarmaScore(k);
        });
        await Promise.all(scoreDeferred);
        this.renderElement();
    },
    /**
     * Find the last computed score for the given karma object.
     *
     * @param {Object} karma - the karma object
     * @returns {Object} the score object.
     */
    async findLastKarmaScore(karma){
        var form = this.getParent();
        var scores = await this._rpc({
            model: "karma.score",
            method: "search_read",
            domain: [
                ["karma_id", "=", karma.id],
                ["res_id", "=", form.state.res_id],
                ["res_model", "=", form.state.model],
            ],
            limit: 1,
            order: "id desc",
        });
        return scores.length ? scores[0] : null;
    },
    /**
     * Get the Karma related to the given click event.
     *
     * More than one Karma may theoritically appear in the widget.
     * The if of the karma related to the click can be found using the attribute `karma`
     * on the target's parent `.o_karma_widget__item` node.
     *
     * @param {jQuery.Event} event - the click event
     * @returns {Object} the karma object.
     */
    getKarmaFromEvent(event){
        var target = $(event.target);
        var karmaId = parseInt(target.closest(".o_karma_widget__item").attr("karma"));
        return this.karmas.filter((k) => k.id === karmaId)[0];
    },
    /**
     * Display the details that compose the score.
     */
    scoreDrilldown(event){
        var karma = this.getKarmaFromEvent(event);
        var actionModel = (
            karma.type_ === "inherited" ?
            "karma.score.inherited.detail" : "karma.score.condition.detail"
        );
        this.do_action({
            res_model: actionModel,
            name: _t("{karma_label} (details)").replace("{karma_label}", karma.label),
            views: [[false, "list"]],
            type: "ir.actions.act_window",
            domain: [["score_id", "=", karma.score.id]],
        });
    },
    /**
     * Open the scores history for the current record.
     */
    openHistory(event){
        var karma = this.getKarmaFromEvent(event);
        var form = this.getParent();
        this.do_action({
            res_model: "karma.score",
            name: _t("{karma_label} (history)").replace("{karma_label}", karma.label),
            views: [[false, "list"]],
            type: "ir.actions.act_window",
            domain: [
                ["res_id", "=", form.state.res_id],
                ["res_model", "=", form.state.model],
            ],
            context: {
                "search_default_karma_id": karma.id,
            },
        });
    },
    /**
     * Compute (refresh) the score for the current record.
     */
    async computeScore(event){
        var karma = this.getKarmaFromEvent(event);
        var form = this.getParent();
        await this._rpc({
            model: "karma",
            method: "run_anticipate_computation",
            args: [[karma.id], form.state.model, form.state.res_id],
        });
        this.refreshData();
    },
});

widgetRegistry.add("karma", KarmaWidget);

});
