odoo.define("karma.KarmaDetailDrilldown", function(require){

var basicFields = require("web.basic_fields");
var core = require("web.core");
var registry = require("web.field_registry");

var _t = core._t;

var ScoreDrilldownWidget = basicFields.FieldFloat.extend({
    tagName: "a",
    start(){
        return this._super.apply(this, arguments).then(() => {
            this.$el.click((event) => {
                event.preventDefault();
                event.stopPropagation();
                this.drilldown();
            });
            this._colorizeLink();
        });
    },
    /**
     * Colorize the link.
     *
     * Since Odoo version 12.0, links without an href are not colored.
     */
    _colorizeLink(){
        this.$el.attr("href", "#");
    },
    /**
     * Open the details that compose the karma score.
     */
    drilldown(){
        var karmaType;
        var scoreId;

        if(this.model === "karma.score"){
            karmaType = this.recordData.karma_type;
            scoreId = this.recordData.id;
        }
        else {
            // Details from a line of inherited score detail.
            karmaType = this.recordData.child_score_karma_type;
            scoreId = this.recordData.child_score_id.data.id;
        }
        var actionModel = (
            karmaType === "inherited" ?
            "karma.score.inherited.detail" : "karma.score.condition.detail"
        );
        this.do_action({
            res_model: actionModel,
            name: _t("Details"),
            views: [[false, "list"]],
            type: "ir.actions.act_window",
            domain: [["score_id", "=", scoreId]],
        });
    },
});

registry.add("karma_score_drilldown", ScoreDrilldownWidget);

});
