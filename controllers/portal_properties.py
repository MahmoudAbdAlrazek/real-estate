# from timeit import default_number

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from werkzeug.exceptions import NotFound


class MyProperties(CustomerPortal, http.Controller):
    # تعريف كلاس للتحكم في الروابط التي تتعلق بعرض العقارات الخاصة بالمستخدم

    @http.route(['/my/properties', '/my/properties/page/<int:page>'], type='http', auth='user', website=True)
    def my_properties_list_view(self, page=1, sortby='id', groupby='none', search='', search_in='all', **kw):
        """
        دالة لعرض قائمة العقارات مع دعم تقسيم الصفحات (Pagination).
        """
        # الحصول على المعرف الخاص بالـ partner للمستخدم الحالي
        partner_id = request.env.user.partner_id.id

        # إعداد الخيارات المتاحة للترتيب
        sorted_list = {
                'id'   : {'label': 'ID', 'order': 'id asc'},
                'name' : {'label': 'Name', 'order': 'name'},
                'state': {'label': 'State', 'order': 'state'},
        }

        # إعداد خيارات Groupby
        groupby_list = {
                'none'         : {'label': 'None', 'field': None},
                'state'        : {'label': 'State', 'field': 'state'},
                'property_type': {'label': 'Property Type', 'field': 'property_type'}
        }

        # ترتيب افتراضي
        #     اذا كان sortby موجودًا، فإنه يُرجع القيمة المرتبطة به.
        #     إذا لم يكن موجودًا، فإنه يُرجع القيمة الافتراضية وهي sorted_list['id'].
        # ['order']: 'id'أو من المفتاح الافتراضي  (sortby سواء من بعد استرجاع العنصر سواء من
        # يتم استخراج قيمة المفتاح 'order' من العنصر
        default_order_by = sorted_list.get(sortby, sorted_list['id'])['order']

        # تحديد عدد السجلات التي ستُعرض في كل صفحة
        per_page = 3

        # البحث عن سجلات الموديل 'property.items' باستخدام البيئة `sudo`
        # يتم استخدام `sudo` لتجاوز قيود الوصول والتحكم في السجلات
        PropertyItems = request.env['property.items'].sudo()

        # تعريف شرط (Domain) للبحث عن السجلات، حاليًا يتم تعيينه كقائمة فارغة (يعني إرجاع كل السجلات)
        # إعداد شرط البحث (Domain)
        domain = []
        # Add search conditions based on search parameters

        if search:
            search_domain = []
            if search_in in ['name', 'all']:
                search_domain.append(('name', 'ilike', search))
            if search_in in ['state', 'all']:
                search_domain.append(('state', 'ilike', search))

            # Combine search conditions with OR operator if multiple conditions
            if len(search_domain) > 1:
                domain = ['|'] + search_domain
            else:
                domain = search_domain

        # إجمالي السجلات
        total_count = PropertyItems.search_count(domain)

        # حساب العدد الكلي للصفحات
        total_pages = (total_count + per_page - 1) // per_page  # هذا يحسب العدد الكلي للصفحات

        # التأكد أن رقم الصفحة لا يتجاوز العدد الكلي للصفحات
        if page > total_pages or page < 1:
            raise NotFound()  # رفع استثناء لتوجيه المستخدم إلى صفحة 404
            # page = total_pages  # إذا كانت الصفحة أكبر من عدد الصفحات المتاحة، نقوم بتوجيه المستخدم إلى آخر صفحة

        # إنشاء إعدادات تقسيم الصفحات باستخدام `request.website.pager`
        # url: رابط الصفحة الأساسي
        # total: العدد الإجمالي للسجلات
        # page: رقم الصفحة الحالي
        # step: عدد السجلات لكل صفحة
        pager_details = request.website.pager(
                url='/my/properties',
                total=total_count,
                url_args={'sortby': sortby, groupby: groupby, 'search': search, 'search_in': search_in},
                page=page,
                step=per_page
        )
        #  تقسيم الصفحات عن طريق عمل import لل pager اللي موجود في بورتال
        #  واستدامخ مباشر بدل منrequest.website.pager
        # pager_details = pager(
        #         url='/my/properties',
        #         total=total_count,
        #         url_args = {'sort_field': sort_field},
        #         page=page,
        #         step=per_page
        # )

        # البحث عن السجلات التي سيتم عرضها بناءً على الصفحة الحالية وحدود التقسيم (offset, limit)
        # offset = (رقم الصفحة - 1) × عدد السجلات في كل صفحة
        # offset = (page_number -1) * per_page
        properties = PropertyItems.search(
                domain, offset=pager_details['offset'], limit=per_page, order=default_order_by
        )

        # إذا كان هناك groupby محدد
        grouped_properties = {}
        # التحقق مما إذا كان groupby ليس "none"
        if groupby_list.get(groupby, {}).get('field') and groupby != 'none':
            group_field = groupby_list[groupby]['field']

            # التأكد من وجود المجال (field) قبل التجميع
            if group_field:
                # تعديل البحث ليشمل كل السجلات وليس فقط السجلات المقسمة
                all_properties = PropertyItems.search(
                        domain, order=default_order_by
                )

                for prop in all_properties:
                    # التعامل مع القيمة المحتملة None
                    group_value = prop[group_field] if prop[group_field] else 'Uncategorized'

                    if group_value not in grouped_properties:
                        grouped_properties[group_value] = []
                    grouped_properties[group_value].append(prop)

        # Prepare search options
        search_options = {
                'all'  : {'label': 'All Fields'},
                'name' : {'label': 'Name'},
                'state': {'label': 'State'}
        }
        # إعادة القالب 'real_estate.portal_my_properties' مع إرسال البيانات المطلوبة
        return request.render(
                'real_estate.portal_my_properties', {
                        'properties'        : properties,  # قائمة العقارات التي ستُعرض
                        'grouped_properties': grouped_properties,  # قائمة العقارات المجمعة حسب الحقل المحدد
                        'pager'             : pager_details,  # معلومات تقسيم الصفحات
                        'page_name'         : 'my_properties_list',  # اسم الصفحة لتمييزها
                        'sortby'            : sortby,  # حقل الترتيب
                        'groupby'           : groupby,  # حقل التقسيم
                        'searchbar_sortings': sorted_list,  # قيمة الترتيب
                        'searchbar_groupbys': groupby_list,  # قيمة التقسيم
                        'search'            : search,
                        'search_in'         : search_in,
                        'searchbar_inputs'  : search_options,

                }
        )

    @http.route('/my/properties/<model("property.items"):property_id>', type='http', auth='user', website=True)
    def my_properties_view_form(self, property_id, **kw):
        vals = {"property": property_id, "page_name": "my_properties_form", }
        # print(f"vals: {vals}")
        property_records = request.env['property.items'].sudo().search([])
        #         print(f"property_records: {property_records}")
        property_ids = property_records.ids
        #         print(f"property_ids: {property_ids}")
        property_index = property_ids.index(property_id.id)
        #         print(f"property_index: {property_index}")

        if property_index != 0 and property_ids[property_index - 1]:
            vals["prev_record"] = property_ids[property_index - 1]
        if property_index < len(property_ids) - 1 and property_ids[property_index + 1]:
            vals["next_record"] = property_ids[property_index + 1]

        return request.render(
                'real_estate.portal_my_properties_details_sidebar', vals)

    # دا راوت عشان اظهر واطبع التقرير
    @http.route('/my/properties/print/<model("property.items"):property_record>', type='http', auth='user', website=True)
    def my_properties_print_form_report(self, property_record, **kw):
        print(f"property_id: {property_record}")
        # تأكد من وجود السجل
        if not property_record:
            return request.not_found()

        return self._show_report(
                model=property_record,
                report_type='pdf',
                report_ref='real_estate.action_report_property_items',
                download=True, )

    # class CustomCustomerPortal(CustomerPortal):
#
#     def _prepare_home_portal_values(self, counters):
#         # Call the base method to get the original values
#         values = super(CustomCustomerPortal, self)._prepare_home_portal_values(counters)
#         print(f'counters: {counters}')
#         print(f'values: {values}')
#
#         values['property_count_all'] = request.env['property.items'].search_count([])
#         print(f'property_count_all: {values["property_count_all"]}')
#         return values
