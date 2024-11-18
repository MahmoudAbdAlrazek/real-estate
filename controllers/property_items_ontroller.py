from odoo import http
from odoo.http import request
import json


class CustomRestApiController(http.Controller):

    # استرجاع جميع السجلات من نموذج معين
    @http.route('/api/property_item', type='http', auth='none', methods=['GET'], csrf=False)
    def get_property_items(self, **kwargs):
        try:
            # محاولة استرجاع البيانات من النموذج
            items = request.env['property.items'].sudo().search([])

            # التحقق من وجود البيانات
            if not items:
                return request.make_response(
                        json.dumps({'error': 'No records found'}),
                        headers=[('Content-Type', 'application/json')],
                        status=404
                )

            # قراءة البيانات المطلوبة من الحقول
            items_data = items.read(['name', 'res_partner_id', 'selling_price', 'state'])

            # إعادة الاستجابة كـ JSON
            return request.make_response(
                    json.dumps(items_data),
                    headers=[('Content-Type', 'application/json')],
                    status=200
            )

        except Exception as e:
            # معالجة أي خطأ غير متوقع
            error_message = {
                    'error'  : 'An error occurred while processing the request',
                    'details': str(e)
            }
            return request.make_response(
                    json.dumps(error_message),
                    headers=[('Content-Type', 'application/json')],
                    status=500
            )

    # إنشاء سجل جديد
    @http.route('/api/property_item', type='json', auth='public', methods=['POST'], csrf=False)
    def create_property_item(self, **kwargs):
        name = kwargs.get('name')
        state = kwargs.get('state')
        selling_price = kwargs.get('selling_price')
        if not name or not state:
            return request.make_response(json.dumps({'error': 'Missing required fields'}), status=400)

        new_item = request.env['property.items'].sudo().create(
                {
                        'name'         : name,
                        'state'        : state,
                        'selling_price': price,
                })
        return request.make_response(json.dumps(new_item.read(['name', 'state', 'price'])[0]), headers=[('Content-Type', 'application/json')])

    # تعديل سجل موجود
    @http.route('/api/property_item/<int:item_id>', type='json', auth='public', methods=['PUT'], csrf=False)
    def update_property_item(self, item_id, **kwargs):
        item = request.env['property.items'].sudo().browse(item_id)
        if not item.exists():
            return request.make_response(json.dumps({'error': 'Item not found'}), status=404)

        item.write(
                {
                        'name' : kwargs.get('name', item.name),
                        'state': kwargs.get('state', item.state),
                        'price': kwargs.get('price', item.price),
                })
        return request.make_response(json.dumps(item.read(['name', 'state', 'price'])[0]), headers=[('Content-Type', 'application/json')])

    # حذف سجل
    @http.route('/api/property_item/<int:item_id>', type='json', auth='public', methods=['DELETE'], csrf=False)
    def delete_property_item(self, item_id, **kwargs):
        item = request.env['property.items'].sudo().browse(item_id)
        if not item.exists():
            return request.make_response(json.dumps({'error': 'Item not found'}), status=404)

        item.unlink()
        return request.make_response(json.dumps({'success': 'Item deleted'}), headers=[('Content-Type', 'application/json')])

# import json
# import math
#
# from odoo import http  # http: مكتبة توفر أدوات لإنشاء Web Controllers في Odoo.
# from odoo.http import request  # request: كائن يستخدم للتعامل مع الطلبات والاستجابات (HTTP Requests and Responses) في Odoo.
#
# class PropertyItemController(http.Controller):
#
#     # create operations
#     @http.route('/v1/property_items_create_http', type='http', auth='none', methods=['POST'], csrf=False)
#     def create_properties_item_http(self):
#         # محاولة قراءة وتحليل البيانات المرسلة عبر الطلب كـ JSON
#         try:
#             # الوصول إلى البيانات : request.httprequest.data هي الطريقة التي تستخدمها للوصول
#             # إلى بيانات الطلب التي أرسلها المستخدم. هذه البيانات تكون على شكل نص (سلسلة نصية).
#             # محاولة تحميل البيانات القادمة من الطلب وتحويلها من صيغة JSON إلى صيغة القاموس (dictionary)
#             args = json.loads(request.httprequest.data)
#         except (json.JSONDecodeError, TypeError) as e:
#             # عند وجود خطأ في تحويل البيانات، يتم إرجاع استجابة بحالة 400 (خطأ في الطلب) مع رسالة خطأ توضح المشكلة
#             # إذا كان هناك خطأ في تحليل JSON (مثل تنسيق غير صحيح)، قم بإرجاع استجابة بحالة 400
#             # ما هو request.make_json_response؟
#             # هي دالة في إطار عمل Odoo تُستخدم لإنشاء استجابة HTTP بصيغة JSON.
#             # هذه الاستجابة تُرسل إلى العميل الذي أرسل الطلب،
#             # وعادةً ما تكون نتيجة عملية تم تنفيذها على الخادم.
#             return request.make_json_response(
#                     {
#                             'message': 'Invalid JSON data',  # رسالة الخطأ للمستخدم، تشير إلى أن البيانات المرسلة غير صحيحة
#                             'error'  : str(e)  # تفاصيل الخطأ، مثل رسائل الاستثناء
#                     },
#                     status=400
#                     # حالة HTTP 400: طلب غير صحيح، يشير إلى أن هناك مشكلة في البيانات المدخلة
#             )
#             # استخدام invalid_response
#             # return invalid_response_http('Invalid JSON data', str(e), 400)
#             # return invalid_response(message='Invalid JSON data', error=str(e), status=400)
#
#         # او استخدام http.Respone
#         # from odoo.http import Response
#         # except (json.JSONDecodeError, TypeError) as e:
#         #     # التقاط خطأ JSON وتفاصيل الخطأ
#         #     return Response(
#         #             json.dumps(
#         #                     {
#         #                             'error': {
#         #                                     'message': 'Invalid JSON data',
#         #                                     'data'   : str(e)
#         #                             }
#         #                     }),
#         #             status=400,
#         #             mimetype='application/json'
#         #     )
#         #
#
#         # محاولة إنشاء سجل جديد في النموذج "property.item" باستخدام البيانات المحولة
#         # محاولة إنشاء سجل جديد في نموذج 'property.item'
#         try:
#             # إنشاء سجل جديد باستخدام البيانات التي تمت قراءتها
#             res = request.env['property.items'].sudo().create(args)
#         except Exception as e:
#             # عند حدوث خطأ أثناء عملية الإنشاء، يتم إرجاع استجابة بحالة 500 (خطأ في الخادم) مع رسالة خطأ توضح المشكلة
#             # إذا حدث خطأ أثناء محاولة إنشاء السجل، قم بإرجاع استجابة بحالة 500
#             return request.make_json_response(
#                     {
#                             'message': 'Failed to create property item',  # رسالة الخطأ للمستخدم، تشير إلى فشل إنشاء السجل
#                             'error'  : str(e)  # تفاصيل الخطأ، مثل رسائل الاستثناء
#                     },
#                     status=500  # حالة HTTP 500: خطأ في الخادم، يشير إلى أن هناك مشكلة في معالجة الطلب
#             )
#             # استخدام invalid_response
#             # return invalid_response_http('Failed to create property item', str(e), 500)
#
#         # عند نجاح إنشاء السجل، يتم إرجاع استجابة بحالة 201 (تم الإنشاء) مع رسالة تأكيد تحتوي على معرف السجل الجديد
#         # إذا تم إنشاء السجل بنجاح، قم بإرجاع استجابة بحالة 201
#         return request.make_json_response(
#                 {
#                         'message': 'success created',  # رسالة نجاح للمستخدم، تشير إلى أن السجل تم إنشاؤه بنجاح
#                         'id'     : res.id,  ## معرف السجل الذي تم إنشاؤه، يتم إرجاعه لتأكيد العملية
#                         'name'   : res.name
#                 },
#                 status=201)  # حالة HTTP 201: تم الإنشاء بنجاح، يشير إلى أن السجل تم إنشاؤه بشكل صحيح
