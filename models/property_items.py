import random
from datetime import date
from email.policy import default
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.models import UserError

import xlsxwriter
import io
from io import BytesIO
import base64
from xlsxwriter import Workbook  # أضف هذا السطر


class PropertyItems(models.Model):
    _name = 'property.items'
    _description = 'Real Estate Property'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # الوحدة تتيح التنبيهات والتنشيطات للمستخدمين على السجلات

    reference_number = fields.Char(string='Reference Number', readonly=True, copy=False, default='new')  # copy=False يمنع النسخ التلقائي
    suffix = fields.Char(string='Suffix', readonly=True, copy=False)
    # reference_number = fields.Char(string='Reference Number', readonly=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('property.items'))

    partner_id = fields.Many2one(
            'res.partner',
            string='Partner Owner',
            tracking=True, )

    customer_email = fields.Char(related='partner_id.email', string='Email')

    color = fields.Integer(string='Color', default=lambda self: random.randint(0, 11))

    # البيانات الأساسية
    name = fields.Char(string='Property Name', tracking=True, )
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Archive', default=True)

    create_date = fields.Datetime(string='Creation Date', readonly=True, default=fields.Datetime.now)
    write_date = fields.Datetime(string='Last Updated', readonly=True, default=fields.Datetime.now)

    # بيانات الموقع
    location = fields.Char(string='Location', tracking=True)
    address = fields.Char(string='Address', tracking=True)
    latitude = fields.Float(string='Latitude')
    longitude = fields.Float(string='Longitude')
    city = fields.Char(string='City', )
    state_id = fields.Many2one('res.country.state', string='Country State', )
    # النموذج res.country يأتي ضمن الوحدة (module) الأساسية في Odoo، التي تُسمى base.
    #  يخزن معلومات عن الدول. يمكن أن يحتوي على حقول مثل اسم الدولة، رمز الدولة، ورمز الهاتف.
    country_id = fields.Many2one('res.country', string='Country', )

    # البيانات المالية
    selling_price = fields.Float(tracking=True, )
    # selling_price = fields.Float(tracking=True, required=True, groups='real_estate.group_property_item_admin')
    # تاريخ البيع المتوقع
    expected_selling_date = fields.Date(string="Expected Selling Date", )
    rental_price = fields.Float(string='Rental Price', tracking=True, )  # سعر ألإيجار
    # النموذج res.currency يأتي افتراضيًا مع  Odoo كجزء من الوحدة الأساسية base
    currency_id = fields.Many2one('res.currency', string='Currency')

    #  تعيين حقل منطقي لتحديد إذا ما كان التاريخ قد مر أم لا
    is_past = fields.Boolean(string='Is Past', compute='_compute_is_past', store=True)
    # البيانات التوصيفية
    property_type = fields.Selection([('residential', 'Residential'), ('commercial', 'Commercial'), ('industrial', 'Industrial'), ('land', 'Land'), ('office', 'Office')], default='residential')
    size = fields.Float(string='Size (in sq. meters)', compute='_compute_total_size')
    number_of_rooms = fields.Integer(string='Number of Rooms', tracking=True)
    number_of_bathrooms = fields.Integer(string='Number of Bathrooms', tracking=True)
    has_garage = fields.Boolean(string='Has Garage', tracking=True)
    has_pool = fields.Boolean(string='Has Pool', tracking=True)
    year_built = fields.Integer(string='Year Built', tracking=True)

    # بيانات الحالة
    state = fields.Selection([('available', 'Available'), ('rented', 'Rented'), ('sold', 'Sold'), ('closed', 'Closed')], string='State', default='available', tracking=True)

    # معلومات إضافية
    images = fields.Binary(string='Images')
    feature_ids = fields.Many2many('property.feature', 'property_feature_rel', 'property_id', 'feature_id', string='Features')
    neighborhood = fields.Char(string='Neighborhood')

    # بيانات الصيانة
    maintenance_ids = fields.One2many('property.maintenance', 'property_id', string='Maintenance Requests')

    # تاريخ إدراج العقار وتاريخ بيع العقار  مدة بيع العقار
    selling_date = fields.Date(string="Selling Date")
    listing_date = fields.Date(string="Listing Date", default=fields.Date.today())
    selling_duration_text = fields.Char(string="Days to Sell", compute='_compute_selling_duration_text')

    # # سجل الأنشطة
    # إذا كان لديك نموذج property.items لإدارة العقارات،
    # يمكنك استخدام هذا الحقل لإدارة الأنشطة المرتبطة بكل عقار. على سبيل المثال،
    # يمكنك إضافة تذكيرات للمتابعة مع العملاء، مواعيد للصيانة، أو أي نوع آخر من الأنشطة ذات الصلة.
    activity_ids = fields.One2many('mail.activity', 'res_id', string='Activities', domain=[('res_model', '=', 'property.items')])
    #
    # # التسجيلات المرفقة
    # إذا كنت تدير نموذج property.items لإدارة العقارات،
    # يمكنك استخدام هذا الحقل لإضافة مرفقات مثل الصور الفوتوغرافية للعقارات،
    # أو مستندات مثل عقود التأجير أو الوثائق القانونية الأخرى المتعلقة بكل عقار.
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Attachments', domain=lambda self: [('res_model', '=', 'property.items')])

    xls_file = fields.Binary("Excel File", readonly=True)
    xls_file_name = fields.Char("File Name", readonly=True)

    # SQL constraint to enforce unique name
    # _sql_constraints = [
    #         ('unique_property_name', 'unique(name)', 'The property name must be unique!')
    # ]

    def generate_xls_report(self):
        # إنشاء كائن BytesIO لتخزين بيانات الملف
        output = BytesIO()
        # إنشاء ملف Excel باستخدام xlsxwriter
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Property Items')

        # إضافة تنسيق للعناوين والرؤوس
        title_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center'})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'align': 'center'})
        cell_format = workbook.add_format({'align': 'center'})

        # كتابة عنوان رئيسي للجدول
        worksheet.merge_range('A1:I1', 'Property Items Report', title_format)

        # كتابة رؤوس الأعمدة مع تنسيق
        headers = ['Reference Number', 'Property Name', 'Partner Owner', 'State', 'Country',
                   'Selling Price', 'Expected Selling Date', 'Rental Price', 'Currency']
        worksheet.write_row(1, 0, headers, header_format)

        # الحصول على بيانات الممتلكات
        properties = self.search([])  # يمكنك تخصيص هذا البحث حسب الحاجة

        # كتابة البيانات إلى ورقة العمل مع تنسيق للخلايا
        for row, property in enumerate(properties, start=2):
            worksheet.write(row, 0, property.reference_number, cell_format)
            worksheet.write(row, 1, property.name, cell_format)
            worksheet.write(row, 2, property.partner_id.name if property.partner_id else "", cell_format)
            worksheet.write(row, 3, property.state_id.name if property.state_id else "", cell_format)
            worksheet.write(row, 4, property.country_id.name if property.country_id else "", cell_format)
            worksheet.write(row, 5, property.selling_price, cell_format)
            worksheet.write(row, 6, property.expected_selling_date, cell_format)
            worksheet.write(row, 7, property.rental_price, cell_format)
            worksheet.write(row, 8, property.currency_id.name if property.currency_id else "", cell_format)

        # ضبط عرض الأعمدة لتحسين التنسيق
        worksheet.set_column(0, 0, 15)  # Reference Number column
        worksheet.set_column(1, 1, 25)  # Property Name column
        worksheet.set_column(2, 2, 20)  # Partner Owner column
        worksheet.set_column(3, 4, 15)  # State and Country columns
        worksheet.set_column(5, 5, 15)  # Selling Price column
        worksheet.set_column(6, 7, 20)  # Expected Selling Date and Rental Price columns
        worksheet.set_column(8, 8, 15)  # Currency column

        # إغلاق دفتر العمل
        workbook.close()
        output.seek(0)

        # إعداد الملف الثنائي للتخزين في السجل
        file_content = output.read()
        encoded_file = base64.b64encode(file_content)
        # or او اكتب امر في سطر واحد كدا
        # تحويل البيانات إلى تنسيق base64 وتحويلها إلى استجابة URL مباشرة
        file_content = base64.b64encode(output.read()).decode('utf-8')

        # تحديث السجل مع الملف المولد
        # دا بيخلي لما اضغط علي زرار يحط تقرير في سجل دا
        self.xls_file = encoded_file
        self.xls_file_name = 'property_items_report.xlsx'

    def export_property_items_xlsx(self):
        # إنشاء كائن BytesIO لتخزين بيانات ملف Excel في الذاكرة
        output = io.BytesIO()
        # إنشاء ملف Excel جديد باستخدام مكتبة xlsxwriter
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        # إضافة ورقة جديدة إلى ملف Excel باسم "Property Items"
        worksheet = workbook.add_worksheet('Property Items')

        # إعداد تنسيق للرؤوس مع خلفية ملونة ومحاذاة في الوسط
        header_format = workbook.add_format({'bold': True, 'bg_color': '#FFA07A', 'align': 'center', 'valign': 'vcenter'})
        # إعداد تنسيق للخلايا مع محاذاة في الوسط
        cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})  # إضافة حدود للخلايا
        # إعداد تنسيق خاص للعنوان
        title_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#FFCCCB'})

        # كتابة عنوان في الصف الأول، دمج الخلايا في العمودين 0 إلى 11
        worksheet.merge_range('A1:L1', 'Property Items Report', title_format)

        # تعريف رؤوس الأعمدة
        headers = [
                'Reference Number', 'Property Name', 'Location', 'City',
                'State', 'Country', 'Selling Price', 'Expected Selling Date',
                'Rental Price', 'Currency', 'Property Type', 'Owner Email'
        ]

        # كتابة رؤوس الأعمدة في الصف الثاني (الصف 1) من ورقة العمل باستخدام التنسيق المحدد
        worksheet.write_row(1, 0, headers, header_format)  # تغيير الصف إلى 1 حيث الصف 0 يستخدم للعناوين

        # البحث عن جميع السجلات من نموذج "property.items"
        items = self.search([])  # تأكد من وجود سجلات
        print(f"Found {len(items)} items.")  # طباعة عدد العناصر المكتشفة
        # إذا لم يتم العثور على أي عنصر، يتم رفع استثناء ليشير إلى عدم وجود بيانات للتصدير
        if not items:
            raise UserError("لا توجد بيانات لتصديرها.")

        # الحصول على خيارات حقل "property_type" كقائمة
        property_type_selection = self.env['property.items']._fields['property_type'].selection

        # كتابة البيانات إلى ورقة العمل
        for row_num, item in enumerate(items, start=2):  # بدء من الصف 2
            print(f"Exporting item: {item.name}")  # طباعة اسم العنصر الجاري تصديره
            # كتابة بيانات العنصر في الصف الحالي
            worksheet.write(row_num, 0, item.reference_number or '', cell_format)
            worksheet.write(row_num, 1, item.name or '', cell_format)
            worksheet.write(row_num, 2, item.location or '', cell_format)
            worksheet.write(row_num, 3, item.city or '', cell_format)
            worksheet.write(row_num, 4, item.state_id.name if item.state_id else '', cell_format)  # إذا كان يوجد state_id، يتم كتابة اسمه
            worksheet.write(row_num, 5, item.country_id.name if item.country_id else '', cell_format)  # إذا كان يوجد country_id، يتم كتابة اسمه
            worksheet.write(row_num, 6, item.selling_price or 0.0, cell_format)  # إذا لم يكن هناك سعر، يتم كتابة 0.0
            worksheet.write(row_num, 7, item.expected_selling_date.strftime('%Y-%m-%d') if item.expected_selling_date else '', cell_format)  # تنسيق التاريخ
            worksheet.write(row_num, 8, item.rental_price or 0.0, cell_format)
            worksheet.write(row_num, 9, item.currency_id.name if item.currency_id else '', cell_format)  # كتابة العملة
            # تحويل نوع الملكية إلى نص من الاختيار
            worksheet.write(row_num, 10, dict(property_type_selection).get(item.property_type, ''), cell_format)  # تحويل الرقم إلى نص
            worksheet.write(row_num, 11, item.customer_email or '', cell_format)  # كتابة البريد الإلكتروني للمالك

        # ضبط عرض الأعمدة بناءً على المحتوى
        for i, header in enumerate(headers):
            max_length = len(header)  # بدءاً من طول الرأس
            for item in items:
                # استخدام getattr للحصول على القيمة بشكل ديناميكي
                cell_content = str(getattr(item, header.replace(' ', '_').lower(), ''))  # تعيين المفتاح بشكل صحيح
                max_length = max(max_length, len(cell_content))  # إيجاد أطول محتوى في العمود
            worksheet.set_column(i, i, max_length + 2)  # إضافة 2 لتحسين المساحة

        # إغلاق ملف Excel بعد الانتهاء من الكتابة
        workbook.close()
        # إعادة المؤشر إلى بداية الكائن حتى يمكن قراءة البيانات
        output.seek(0)

        # إنشاء سجل في نموذج "ir.attachment" لتخزين الملف المولد
        attachment = self.env['ir.attachment'].create(
                {
                        'name'       : 'Property_Items_Report.xlsx',  # اسم الملف
                        'type'       : 'binary',  # نوع السجل
                        'datas'      : base64.b64encode(output.read()),  # ترميز البيانات إلى Base64
                        'store_fname': 'Property_Items_Report.xlsx',  # اسم التخزين للملف
                        'res_model'  : 'property.items',  # النموذج المرتبط بالسجل
                        'res_id'     : False,  # معرف السجل المرتبط (غير موجود هنا)
                })

        # إعادة توجيه المستخدم إلى الرابط لتنزيل الملف المولد
        return {
                'type'  : 'ir.actions.act_url',  # نوع الإجراء
                'url'   : f'/web/content/{attachment.id}?download=true',  # الرابط لتنزيل الملف
                'target': 'self',  # فتح الرابط في نفس النافذة
        }

    @api.model_create_multi
    def create(self, vals_list):
        # التعامل مع قائمة القيم
        for vals in vals_list:
            # إذا كانت 'reference_number' في القيم هي 'new', قم بإنشاء رقم مرجعي جديد
            if vals.get('reference_number', _('new')) == _('new'):
                vals['reference_number'] = self.env['ir.sequence'].next_by_code('prop_sequence') or _('new')

        # بعد تحديث القيم، قم بإنشاء السجلات
        return super(PropertyItems, self).create(vals_list)

    def copy(self, default=None):
        """
        يتم استدعاء هذه الدالة عند استخدام زر "تكرار" لتغيير الرقم المرجعي إلى رقم جديد
        """
        default = dict(default or {})
        # توليد رقم مرجعي جديد عند التكرار باستخدام التسلسل
        default['reference_number'] = self.env['ir.sequence'].next_by_code('prop_sequence') or _('new')
        return super(PropertyItems, self).copy(default)

    def action_set_available(self):
        self.state = 'available'

    def action_set_rented(self):
        self.state = 'rented'

    def action_set_sold(self):
        for record in self:
            if record.state != 'sold':
                record.state = 'sold'
                record.message_post(body="The deal has been marked as sold.")
                return {
                        'effect': {
                                'fadeout': 'slow',
                                'message': 'The deal has been marked as sold.',
                                'type'   : 'rainbow_man',
                        }
                }

    def action_set_closed(self):
        for record in self:
            if record.state != 'closed':
                record.state = 'closed'
                record.message_post(body="The deal has been cancelled.")

    # إضافة قيود لمنع القيم السالبة
    @api.constrains('selling_price', 'rental_price', 'size')
    def _check_positive_values(self):
        for record in self:
            if record.selling_price < 0 or record.rental_price < 0 or record.size < 0:
                raise ValidationError("Values for selling_price, Rental Price, and Size must be positive.")

    # حساب المساحة الكلية بناءً على عدد الغرف
    @api.depends('number_of_rooms')
    def _compute_total_size(self):
        for record in self:
            record.size = record.number_of_rooms * 20  # مثال: كل غرفة مساحتها 20 متر مربع

    @api.onchange('number_of_rooms')
    def _onchange_number_of_rooms(self):
        if self.number_of_rooms > 5:
            # عرض إشعار تنبيه في الواجهة
            # إظهار تحذير
            return {'warning':
                {
                        'title'  : "warning",
                        'message': "number of rooms is too big ! are you sure ?",
                        "type"   : "notification",  # "sticky" : False,
                },
            }

    # ,  دالة لحساب الفرق بين تاريخ اليوم وتاريخ البيع المتوقع وعمل corn ليهم
    def check_selling_date(self):
        today = fields.Date.today()
        properties = self.search([('expected_selling_date', '<', today), ('state', '!=', 'sold')])
        if not properties:
            return  # إذا لم يكن هناك سجلات، لا تقوم بأي شيء

        users = self.env['res.users'].search([])  # البحث عن جميع المستخدمين

        for record in properties:
            for user in users:
                record.message_post(
                        body=f"Dear {user.name}, the property '{record.name}' has an expired selling date - {record.expected_selling_date}.",
                )

    #   تنفيذ cron_check_selling_date بشكل دوري
    # لما اعمل corn لازم اضيف فوق داله @api.model
    @api.model
    def cron_check_selling_date(self):
        self.check_selling_date()

    @api.depends('expected_selling_date')
    def _compute_is_past(self):
        # الحصول على تاريخ اليوم
        today = fields.Date.today()  # استخدم fields.Date.today() بدلاً من date.today() لضمان التوافق مع Odoo
        # المرور على كل سجل في المجموعة
        for record in self:
            # تحقق مما إذا كان تاريخ البيع المتوقع موجودًا وتحقق إذا كان قد مر
            if record.expected_selling_date:
                record.is_past = record.expected_selling_date < today
            else:
                record.is_past = False

    @api.onchange('expected_selling_date')
    def _onchange_expected_selling_date(self):
        if self.expected_selling_date and self.expected_selling_date < date.today():
            return {
                    'warning': {
                            'title'  : "Warning",
                            'message': "attention! The expected selling date enter is has passed.",
                            'type'   : 'warning'
                    }
            }

    def get_price_statistics(self):
        all_properties = self.search([])
        total_price = sum(property.selling_price for property in all_properties)
        average_price = total_price / len(all_properties) if all_properties else 0
        return {
                'total_price'  : total_price,
                'average_price': average_price,
        }

    # استخدام الدالة في زر:
    def action_get_statistics(self):
        statistics = self.get_price_statistics()
        return {
                'type'  : 'ir.actions.client',
                'tag'   : 'display_notification',
                'params': {
                        'title'  : 'Price Statistics',
                        'message': f"Total Price: {statistics['total_price']}, Average Price: {statistics['average_price']}",
                        'type'   : 'info',  # نوع الإشعار (يمكن أن يكون 'info', 'warning', 'success', أو 'danger')

                }
        }

    def action_open_change_state_wizard(self):
        if len(self) > 1:
            raise UserError("You can only perform this action on one record at a time.")
        self.ensure_one()  # التأكد من أن الدالة تُستدعى على سجل واحد فقط

        # تحقق من أن الحالة الحالية تسمح بتغييرها
        # if self.state != 'closed' and self.state != 'sold':  # استخدمت _ لجعل رسالة الخطأ قابلة للترجمة، مما يعزز توافق الكود مع الأنظمة متعددة اللغات.
        if self.state != 'closed':  # استخدمت _ لجعل رسالة الخطأ قابلة للترجمة، مما يعزز توافق الكود مع الأنظمة متعددة اللغات.
            raise UserError(_('can not open wizard in current state'))

        # فتح الويدجت
        else:
            return {
                    'name'     : 'change state property to another state',
                    'type'     : 'ir.actions.act_window',
                    'res_model': 'change.state.wizard',
                    'view_mode': 'form',
                    'target'   : 'new',
                    # تمرير المعرف الخاص بالعنصر العقاري إلى الويدجت
                    'context'  : {'default_property_items_id': self.id},
            }

    # اخفاء سجل بناء علي مجموعه معينه من سكيورتي
    # selling_price_visible = fields.Boolean(compute='_compute_selling_price_visible', store=False)
    #
    # def _compute_selling_price_visible(self):
    #     for record in self:
    #         record.selling_price_visible = record.env.user.has_group('real_estate.group_property_item_admin')

    #  دالة تُستخدم لحساب مدة بيع العقار بناءً على تاريخ إدراج العقار وتاريخ بيعه
    @api.depends('listing_date', 'selling_date')
    def _compute_selling_duration_text(self):
        for record in self:
            if record.listing_date and record.selling_date:
                selling_duration_text = (record.selling_date - record.listing_date).days
                if selling_duration_text == 1:
                    record.selling_duration_text = "1 day"
                else:
                    record.selling_duration_text = f"{selling_duration_text} days"
            else:
                record.selling_duration_text = "0 days"

    # قيد يتحقق من أن تاريخ البيع (selling_date) لا يمكن أن يكون قبل تاريخ الإدراج (listing_date).
    @api.constrains('listing_date', 'selling_date')
    def _check_dates(self):
        for record in self:
            if record.selling_date and record.selling_date < record.listing_date:
                raise ValidationError(_("Selling date cannot be earlier than listing date."))

    # استخدام check_access_rule للتحكم في الوصول بدلًا من check_access_rights، لتجنب حدوث الاستدعاءات المتكررة.
    @api.model
    def check_access_rule(self, operation):
        # التحقق من كل سجل على حدة
        for record in self:
            if record.state in ['sold', 'closed']:
                # التحقق من العملية
                if operation in ['write', 'unlink'] and not self.env.user.has_group('real_estate.group_property_item_admin'):
                    raise AccessError(_("You cannot modify or delete a sold or closed property unless you are an admin."))

        # استدعاء الدالة الأصلية للتحقق من القواعد
        return super(PropertyItems, self).check_access_rule(operation)

    # يمنع حذف العقارات التي تم بيعها أو إغلاقها إلا إذا كان المستخدم مديرًا.
    # def unlink(self):
    #     for record in self:
    #         if record.state in ['sold', 'closed'] and not self.env.user.has_group('real_estate.group_property_item_admin'):
    #             raise AccessError(_("Only managers can delete sold or closed properties."))
    #     return super(PropertyItems, self).unlink()

    # جعل العقارات قابله للقراءه فقط في حاله محموعه معينه وحالات معينه
    state_readonly = fields.Boolean(compute='_compute_state_readonly', store=False)

    @api.depends('state')  # تشير إلى أن الدالة تعتمد على حقل 'state'
    def _compute_state_readonly(self):
        # تبدأ حلقة لتكرار كل سجل في الكائن الحالي
        for record in self:
            # إذا كانت الحالة "مباع" أو "مغلق"
            if record.state in ['sold', 'closed']:
                # تحقق مما إذا كان المستخدم لا ينتمي إلى مجموعة 'group_property_item_admin'
                if not self.env.user.has_group('real_estate.group_property_item_admin'):
                    # إذا كان المستخدم ليس في المجموعة، اجعل الحقل readonly
                    record.state_readonly = True
                else:
                    # إذا كان المستخدم في المجموعة، اجعل الحقل editable
                    record.state_readonly = False
            else:
                # إذا لم تكن الحالة "مباع" أو "مغلق"، اجعل الحقل editable
                record.state_readonly = False

    # داله لانشاء تمبلت وبعته للعميل
    # def send_mail_to_customer(self):
    #     for record in self:
    #         if not record.res_partner_id or not record.res_partner_id.email:
    #             raise UserError(f"لا يوجد بريد إلكتروني لهذا العميل: {record.res_partner_id.name if record.res_partner_id else '(بدون عميل)'}")
    #
    #         template_id = self.env.ref('real_estate.email_template_example')
    #         if template_id:
    #             template_id.send_mail(record.id, force_send=True)
    #         else:
    #             raise UserError("لم يتم العثور على قالب البريد الإلكتروني.")
