odoo.define("karma_dynamic_user_message.KarmaWidget", function (require) {
"use strict";

var KarmaWidget = require("karma.KarmaWidget");

KarmaWidget.include({
    async refreshScore(){
        await this._super();
        if (this.score.number_evaluated_lines === this.score.total_number_lines && this.karma.output_type === "information") {
                var formRenderer = this.getParent().getParent();
                var $sheet = formRenderer.$el.find('.o_form_sheet');
                var divContent = '<div style="margin-top:7px;" class="mr16 ml16 alert alert-info">' + this.karma.info_message + '</div>';
                $sheet.before(divContent);
        }
        this.renderElement();
    },
    });
});
