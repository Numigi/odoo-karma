odoo.define("form_view_image_120px", function (require) {
"use strict";

/**
 * Automatically set the size of the image to 120 if it contains the class oe_avatar.
 */
require("web.basic_fields").FieldBinaryImage.include({
    init() {
        this._super.apply(this, arguments);
        var nodeClass = this.attrs.class;
        var hasAvatarClass = nodeClass && nodeClass.split(" ").indexOf("oe_avatar") !== -1;
        if(hasAvatarClass){
            this.nodeOptions.size = [120, 120];
        }
    },
});

});
