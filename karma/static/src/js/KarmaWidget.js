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
        this.score = {};
        this.refreshData();
    },
    start(){
        this._super.apply(this, arguments);
    },
    async refreshData(){
        var form = this.getParent();
        var karmas = await this._rpc({
            model: "karma",
            method: "search_read",
            domain: [
                ["display_on_form_view", "=", true],
                ["model_id.model", "=", form.state.model],
            ],
            limit: 1,
            order: "id",
        });

        if(karmas.length){
            this.karma = karmas[0];
            this.score = await this.findLastKarmaScore(this.karma);
        }
        else{
            this.karma = null;
            this.score = null;
        }
        this.renderElement();
    },
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
    scoreDrilldown(){
        var actionModel = (
            this.karma.type_ === "inherited" ?
            "karma.score.inherited.detail" : "karma.score.condition.detail"
        );
        this.do_action({
            res_model: actionModel,
            name: _t("{karma_label} (details)").replace("{karma_label}", this.karma.label),
            views: [[false, "list"]],
            type: "ir.actions.act_window",
            domain: [["score_id", "=", this.score.id]],
        });
    },
    openHistory(){
        var form = this.getParent();
        this.do_action({
            res_model: "karma.score",
            name: _t("{karma_label} (history)").replace("{karma_label}", this.karma.label),
            views: [[false, "list"]],
            type: "ir.actions.act_window",
            domain: [
                ["res_id", "=", form.state.res_id],
                ["res_model", "=", form.state.model],
            ],
            context: {
                "search_default_karma_id": this.karma.id,
            },
        });
    },
    async computeScore(){
        var form = this.getParent();
        await this._rpc({
            model: "karma",
            method: "run_anticipate_computation",
            args: [[this.karma.id], form.state.model, form.state.res_id],
        });
        this.refreshData();
    },
});

widgetRegistry.add("karma", KarmaWidget);

});
