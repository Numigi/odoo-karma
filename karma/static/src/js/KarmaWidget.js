odoo.define("karma.KarmaWidget", function (require) {
"use strict";

var Widget = require("web.Widget");
var widgetRegistry = require("web.widget_registry");
var core = require("web.core");
var _t = core._t;

/**
 * The main Karma widget.
 *
 * This widget displays the last score of a given record for a single karma.
 * The karma object, the record ID and and the record model are given at the initialization.
 *
 * Once initialized, the widget is autonomous.
 * The widget can however be refreshed from a parent component using the method `refreshScore`.
 */
var KarmaWidget = Widget.extend({
    template: "KarmaWidget",
    events: {
        "click .o_karma_widget__score": "scoreDrilldown",
        "click .o_karma_widget__refresh": "computeScore",
        "click .o_karma_widget__history": "openHistory",
    },
    /**
     * Initialize the widget.
     *
     * @param recordModel {String} the database ID of the record
     * @param recordId {Number} the database ID of the record
     * @param karma {Object} the data of the related karma object
     */
    init(parent, recordModel, recordId, karma){
        this._super(parent);
        this.recordModel = recordModel;
        this.recordId = recordId;
        this.karma = karma;
        this.score = null;
    },
    /**
     * Setup the tooltip.
     *
     * The text to render in the tooltip is contained in the field description
     * of the karma. It is passed to the DOM node through the qWeb template as the attribute `title`.
     * (t-att-title="karma.description").
     *
     * The line breaks \n must be replaced with html line breaks <br/>.
     */
    _setupTooltip(){
        var titleWithLineBreaks = (this.$el.attr("title") || "").replace("\n", "<br/>");
        this.$el.attr("title", titleWithLineBreaks);
        this.$el.tooltip();
    },
    renderElement(){
        this._super();
        this._setupTooltip();
    },
    /**
     * Find the last computed score for the given karma object.
     *
     * @param {Object} karma - the karma object
     * @returns {Object} the score object.
     */
    async findLastKarmaScore(){
        var scores = await this._rpc({
            model: "karma.score",
            method: "search_read",
            domain: [
                ["karma_id", "=", this.karma.id],
                ["res_id", "=", this.recordId],
                ["res_model", "=", this.recordModel],
            ],
            limit: 1,
            order: "id desc",
            params: {
                context: odoo.session_info.user_context,
            },
        });
        return scores.length ? scores[0] : null;
    },
    /**
     * Fetch the karma data from the server and render the widget.
     */
    async refreshScore(){
        this.score = await this.findLastKarmaScore();
        if(this.score){
            this.score.score = this.formatKarmaScore(this.score.score);
        }
        this.renderElement();
    },
    /**
     * Get the database ID of the record bound to the score to display.
     *
     */
    formatKarmaScore(score){
        if(score === null){
            return score;
        }
        if(score >= 100){
            return score.toFixed();
        }

        var scoreWith2Decimals = score.toFixed(2);

        // Remove non-relevant 0 digits
        // 12.34 -> 12.34
        // 12.30 -> 12.3
        // 12.00 -> 12
        // https://stackoverflow.com/questions/11832914/round-to-at-most-2-decimal-places-only-if-necessary/17141819
        return String(parseFloat(scoreWith2Decimals));
    },
    /**
     * Display the details that compose the score.
     */
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
    /**
     * Open the scores history for the current record.
     */
    openHistory(){
        this.do_action({
            res_model: "karma.score",
            name: _t("{karma_label} (history)").replace("{karma_label}", this.karma.label),
            views: [[false, "list"]],
            type: "ir.actions.act_window",
            domain: [
                ["res_id", "=", this.recordId],
                ["res_model", "=", this.recordModel],
            ],
            context: {
                "search_default_karma_id": this.karma.id,
            },
        });
    },
    /**
     * Compute (refresh) the score for the current record.
     */
    async computeScore(){
        await this._rpc({
            model: "karma",
            method: "run_anticipate_computation",
            args: [[this.karma.id], this.recordModel, this.recordId],
        });
        this.refreshScore();
    },
});

/**
 * A karma widget bound to a form view.
 */
var FormViewKarmaWidget = Widget.extend({
    template: "FormViewKarmaWidget",
    /**
     * Find karmas related to the record from the server.
     */
    async findRelatedKarmaObjects(){
        var recordId = this.getParent().state.res_id;
        var recordModel = this.getParent().state.model;
        if(!recordId){
            return [];
        }
        return await this._rpc({
            model: "karma",
            method: "find_karmas_to_display_on_form_view",
            args: [recordModel, recordId],
            params: {
                context: odoo.session_info.user_context,
            },
        });
    },
    /**
     * Render the karma widget.
     *
     * The karma widget is separated in another widget so that it can be used
     * outside the context of a form view.
     */
    _renderKarmaWidget(karma){
        var recordId = this.getParent().state.res_id;
        var recordModel = this.getParent().state.model;
        var widget = new KarmaWidget(this, recordModel, recordId, karma);
        widget.refreshScore();
        widget.renderElement();
        return widget.$el;
    },
    /**
     * After rendering the element, the karma widgets related to the record are rendered.
     */
    renderElement($el){
        this._super();
        var $el = this.$el;
        this.findRelatedKarmaObjects().then((karmas) => {
            karmas.forEach((karma) => {
                $el.append(this._renderKarmaWidget(karma));
            });
        });
    },
});

widgetRegistry.add("karma", FormViewKarmaWidget);

return KarmaWidget;

});
