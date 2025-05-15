/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";

// ✅ patch 接收 3 个参数：目标对象，patch 名称，patch 内容
patch(ListRenderer.prototype, 'sale_order_batch.TreeNoOpen', {
    onCellClicked(ev) {
        // ev.stopPropagation();
        // ev.preventDefault();
        console.log("✅ Cell click disabled by patch" + ev.currentTarget);
        console.log("✅ Cell click disabled by patch" + ev.target);
    },
});