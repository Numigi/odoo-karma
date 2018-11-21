odoo.define("karma_user_dashboard.dashboard", function (require) {
"use strict";

var core = require("web.core");
var rpc = require("web.rpc");
var Widget = require("web.Widget");

var KarmaWidget = require("karma.KarmaWidget");

/**
 * An item of the user Karma dashboard.
 *
 * One item is shown for each parent user karma to display in the dashboard.
 * It contains the parent karma and its direct children karmas.
 */
var DashboardItem = Widget.extend({
    template: "KarmaUserDashboardItem",
    init(parent, karma){
        this._super(parent);
        this.karma = karma;
    },
    _renderKarmaWidget(karma){
        var userId = odoo.session_info.user_context.uid;
        var widget = new KarmaWidget(this, "res.users", userId, karma);
        widget.refreshScore();
        widget.renderElement();
        return widget.$el;
    },
    /**
     * After rendering the element, initialize and render the karma widgets.
     * 
     * One widget is added for the parent karma.
     * One widget is added for each children karma.
     */
    renderElement(){
        this._super();
        var parentKarmaEl = this._renderKarmaWidget(this.karma);
        this.$(".o_karma_user_dashboard__parent-karma").append(parentKarmaEl);
        this.karma.children.forEach((childKarma) => {
            var childKarmaEl = this._renderKarmaWidget(childKarma);
            this.$(".o_karma_user_dashboard__children-karmas").append(childKarmaEl);
        });
    },
});

/**
 * The user dashboard of the Karma application.
 */
var Dashboard = Widget.extend({
    template: "KarmaUserDashboard",
    /**
     * Find karmas related to the user dashboard from the server.
     */
    async findRelatedKarmaObjects(){
        return rpc.query({
            model: "karma",
            method: "find_scores_to_display_on_user_dashboard",
        });
    },
    /**
     * After rendering the element, one dashboard item is added for each parent karma.
     */
    renderElement(){
        this._super();
        var $el = this.$el;
        this.findRelatedKarmaObjects().then((karmas) => {
            karmas.forEach((karma) => {
                var dashboardItem = new DashboardItem(this, karma);
                dashboardItem.renderElement();
                $el.append(dashboardItem.$el);
            });
        });
    },
});

core.action_registry.add("karma_user_dashboard", Dashboard);

return {
    Dashboard,
};

});
