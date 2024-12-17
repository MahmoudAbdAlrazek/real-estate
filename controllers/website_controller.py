from odoo import http
from odoo.http import request
from werkzeug.urls import url_encode


class PropertyItemsController(http.Controller):

    @http.route('/property', type='http', auth='public', website=True)
    def property_items_form(self, **kwargs):
        # تحميل الدول من قاعدة البيانات
        countries = request.env['res.country'].sudo().search([])

        # تحميل العملات من قاعدة البيانات
        currencies = request.env['res.currency'].sudo().search([])

        # تحميل الميزات من قاعدة البيانات
        features = request.env['property.feature'].sudo().search([])

        # تحميل الرسالة إذا كانت موجودة
        message = kwargs.get('message')

        return request.render(
                'real_estate.property_items_form_template', {
                        'countries' : countries,  # إرسال قائمة الدول إلى الواجهة
                        'currencies': currencies,  # إرسال قائمة العملات إلى الواجهة
                        'features'  : features,  # إرسال قائمة الميزات إلى الواجهة
                        'message'   : message,  # إرسال الرسالة
                })

    @http.route('/property/submit', type='http', auth='public', website=True, methods=['POST'])
    def submit_property_form(self, **kwargs):
        # التحقق من القيم المدخلة
        name = kwargs.get('name')
        partner_name = kwargs.get('partner_name')
        country_id = kwargs.get('state_id')  # ملاحظة أنه تم تعديل اسم الحقل
        email = kwargs.get('customer_email')
        city = kwargs.get('city')
        selling_price = kwargs.get('selling_price')
        currency_id = kwargs.get('currency_id')
        property_type = kwargs.get('property_type')
        number_of_rooms = kwargs.get('number_of_rooms')
        number_of_bathrooms = kwargs.get('number_of_bathrooms')

        if not name or not partner_name or not country_id:
            return request.redirect('/property?message=Missing+required+fields')

        # إنشاء سجل العميل أولاً
        partner = request.env['res.partner'].sudo().create(
                {
                        'name' : partner_name,
                        'email': email,
                        'city' : city,
                })

        # إنشاء سجل العقار
        property_vals = {
                'name'               : name,
                'partner_id'         : partner.id,
                'country_id'         : int(country_id),
                'selling_price'      : selling_price,
                'currency_id'        : int(currency_id),
                'property_type'      : property_type,
                'number_of_rooms'    : number_of_rooms,
                'number_of_bathrooms': number_of_bathrooms,
        }
        property_item = request.env['property.items'].sudo().create(property_vals)

        # رسالة النجاح
        message = 'Property item created successfully'
        return request.redirect(f"/property?{url_encode({'message': message})}")
