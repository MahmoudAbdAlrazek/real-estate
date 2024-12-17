{
        'name'       : "Real_Estate_Management_17",

        'summary'    : """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

        'description': """
        Long description of module's purpose
    """,

        'author'     : "My Company",
        'website'    : "https://www.yourcompany.com",

        # Categories can be used to filter modules in modules listing
        # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
        # for the full list
        'category'   : 'Uncategorized',
        'version'    : '0.1',

        # any module necessary for this one to work correctly
        'depends'    : ['base', 'mail', 'contacts', 'account', 'portal', 'website'],
        # 'depends': ['base', 'contacts', 'mail', 'sale_management',
        #             'account_accountant', 'website'
        #             ],

        # always loaded
        'data'       : [
                'security/security_property_items.xml',  # يجب أن يكون هذا الملف في القمة لأنه يحدد صلاحيات الوصول للموديلات. ن طريق group
                'security/security_property_state_change_reason.xml',
                'security/ir.model.access.csv',  # يجب أن يكون هذا الملف في القمة لأنه يحدد صلاحيات الوصول للموديلات.

                # إذا كان لديك ملفات تحتوي على بيانات ثابتة أو مرجعية مثل ملفات XML أو CSV
                # التي تحدد بيانات أولية، أضفها بعد ملفات الأمان:

                # تأتي في المرتبة الثالثة لأن التقارير غالبًا تعتمد على الموديلات والصلاحيات المحملة بالفعل.
                #  قم بإضافة ملفات التقارير بعد ملفات البيانات لأنها، تعتمد على الموديلات التي تم تحديدها سابقًا.
                'qweb_reports/report_property_items.xml',
                'qweb_reports/report_property_deals.xml',

                # أضف ملفات العرض التي تحدد كيفية عرض البيانات في واجهات المستخدم.
                # تأتي بعد ملفات البيانات والتقارير. .
                # هذه الملفات تحدد كيفية عرض البيانات في الواجهات المختلفة
                'views/property_items_view.xml',
                'views/luxury_property_views.xml',

                'views/partner_menu.xml',

                'views/property_maintenance_view.xml',
                'views/property_feature_view.xml',  # هذا يحتوي على نموذج PropertyFeature
                'data/property_feature_data.xml',  # إضافة هذا الملف لبيانات مزايا العقار
                'views/res_partner.xml',
                'views/property_deal_views.xml',
                'views/portal_template_view.xml',
                # 'views/res_setting.xml',

                # إذا كنت تستخدم Wizards في الموديل الخاص بك، أضفها بعد ملفات العرض
                'wizard/property_state_change_reason.xml',
                'wizard/change_state_wizard_view.xml',

                # أضف ملفات القوائم الأساسية (Base Menu):
                # أخيرًا، أضف ملفات القوائم الأساسية التي تحدد القوائم الرئيسية في النظام
                'views/base_menu_view.xml',

                # ملفات الوراثة (Inherit Views) والملفات الإضافية:
                # أضف أي ملفات وراثة (مثل res_partner_view_inherit.xml) أو أي ملفات إضافية في النهاية.

                'views/res_partner.xml',

                'views/menu_website.xml',
        ],

        'assets'     : {
                'web.assets_backend' : [
                        'real_estate/static/src/css/property_items.css',
                        #                 'school_management/static/src/js/custom.js',
                        #                 # 'real_estate/static/src/css/font.css',
                        #                 # 'real_estate/static/src/fonts/NerkoOne-Regular.ttf',
                ],
                'web.assets_frontend': [
                        'real_estate/static/src/css/property_items.css',

                        #                 'school_management/static/src/js/custom.js',
                        #
                        #                 # 'real_estate/static/src/css/font.css',
                        #                 # 'real_estate/static/src/fonts/NerkoOne-Regular.ttf',
                ],
        },

        # only loaded in demonstration mode
        'demo'       : [
                # 'demo/demo.xml',
        ],
}
# -*- coding: utf-8 -*-
