// javascript
odoo.define('sale_order_batch.SplitView', function (require) {
    "use strict";

    const AbstractAction = require('web.AbstractAction');
    const ListView = require('web.ListView');
    const core = require('web.core');
    const ActionManager = require('web.ActionManager');

    const SplitView = AbstractAction.extend({
        template: 'sale_order_batch.SaleOrderSplitLayout',
        start: function () {
            // 使用 _rpc 调用，或者直接利用 ActionManager加载标准树视图（示例采用 ActionManager.start_action）
            const self = this;
            this.$el.on('click', 'a[data-filter]', function (ev) {
                const filter = $(this).data('filter');
                // 处理筛选条件点击事件，此处可以定义对应的操作
                console.log('筛选条件：', filter);
            });

            // 使用 ActionManager加载已有销售订单树视图
            // 此处 ref 使用标准销售订单树视图或者你自定义的树视图的 XML id
            return this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'sale.order',
                view_mode: 'tree,form',
                views: [[false, 'tree'], [false, 'form']],
                target: 'current',
                context: {},
            }, {clear_breadcrumbs: true}).then(function () {
                // 渲染完成后的操作
                self.$('#sale_order_tree_container').append(self.$el.find('.o_content'));
            });
        },
    });

    core.action_registry.add('sale_order_split_view', SplitView);
    return SplitView;
});