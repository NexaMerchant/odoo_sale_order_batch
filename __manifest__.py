# -*- coding: utf-8 -*-
{
    'name': "sale_order_batch",

    'summary': "Sale Order Batch",

    'description': """
Sale Order Batch
    """,
    'author': "Steve Liu",
    'website': "https://github.com/xxl4",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'delivery', 'stock', 'product', 'purchase', 'account'],

    # always loaded
    'data': [

       # 'security/ir.model.access.csv',

        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/order_tree_v2.xml',
        'views/split_view_template.xml',
        'views/split_view_action.xml',
        'views/sale_report_templates.xml',
        'views/sale_order_tree_page.xml',
        'views/batch_set_shipping_status_view.xml',
        'views/wizard_views.xml',

        'wizards/batch_choose_delivery_carrier_views.xml',
        'wizards/batch_choose_delivery_carrier_access.xml',
        

        
        'report/report_batch_picking.xml',
        'report/report_batch_shipping_label.xml',

      #  'views/new_sale_order_view.xml',
      #  'views/left_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',

}

