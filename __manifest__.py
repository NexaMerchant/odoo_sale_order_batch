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
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'delivery', 'stock', 'product', 'purchase', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

