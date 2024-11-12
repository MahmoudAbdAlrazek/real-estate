from odoo import models, fields, api


class PropertyMaintenance(models.Model):
    _name = 'property.maintenance'
    _description = 'Property Maintenance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    #  فيلد active دا بيخد نوع بيانات اما true or false
    #  دا بيعمل ارشيف للسجل مش بيبقي ظاهر وبرجعو وقت ما بحتاجو ومش بيتمسح من الداتا بيز
    # إذا كان الحقل active مضبوطًا على True، فإن السجل يُعتبر نشطًا (غير مؤرشف).
    active = fields.Boolean(default=True)
    # حقل Many2one للربط بالعقار
    # ondelete='cascade': يعني أنه إذا تم حذف العقّار، سيتم حذف جميع طلبات الصيانة المرتبطة به تلقائيًا.
    property_id = fields.Many2one('property.items', string='Property', required=True, ondelete='cascade')

    # الحقول الأخرى المتعلقة بطلب الصيانة
    maintenance_date = fields.Date(string='Maintenance Date', default=fields.Date.today, required=True, tracking=True)
    maintenance_type = fields.Selection(
            [
                    ('electrical', 'Electrical'),
                    ('plumbing', 'Plumbing'),
                    ('structural', 'Structural'),
                    ('other', 'Other'),
            ], string='Type of Maintenance', required=True, tracking=True)

    notes = fields.Text(string='Notes', required=True, tracking=True)
    state = fields.Selection(
            [
                    ('pending', 'Pending'),
                    ('in_progress', 'In Progress'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
            ], string='Status', default='pending', tracking=True)

    # المرفقات
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Attachments', domain=lambda self: [('res_model', '=', 'property.maintenance')])

    def action_pending(self):
        for rec in self:
            rec.state = 'pending'

    def action_in_progress(self):
        for rec in self:
            rec.state = 'in_progress'

    def action_completed(self):
        for rec in self:
            rec.state = 'completed'

    def action_cancelled(self):
        for rec in self:
            rec.state = 'cancelled'

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.property_id} - {record.maintenance_type} "
            result.append((record.id, name))
        return result

    # @api.onchange: يستخدم فقط لعرض تحذير للمستخدم، ولا يقوم بإرسال رسالة في Chatter.
    # @api.onchange('maintenance_type')
    # def _onchange_maintenance_type(self):
    #     if self.maintenance_type:
    #         # هنا يمكنك وضع الدالة التي تريد تنفيذها
    #         # مثلاً: عرض رسالة للمستخدم أو تعديل حقول أخرى
    #         return {
    #                 'warning': {
    #                         'title'  : "Maintenance Type Changed",
    #                             #  # الحصول علي value
    #                         # 'message': f"The maintenance type has been changed to {dict(self._fields['maintenance_type'].selection).get(self.maintenance_type)}.",
    #                        # الحصول علي key
    #                        'message': f"The maintenance type will be changed to {self.maintenance_type}.",
    #                         # 'type'   : "warning", # يمكن تغييره إلى "info" أو "error" أو "success"
    #                 }
    #         }
    # write: بعد تغيير قيمة maintenance_type، يتم استدعاء
    # message_post لإضافة رسالة في Chatter.
    # def write(self, values):
    #     res = super(PropertyMaintenance, self).write(values)
    #     if 'maintenance_type' in values:
    #         # إضافة رسالة في Chatter
    #         for record in self:
    #             record.message_post(
    #                     # الحصول علي key
    #                     body=f"The maintenance type has been changed to {record.maintenance_type}.",
    #                     # الحصول علي value
    #                     # body=f"The maintenance type has been changed to {dict(self._fields['maintenance_type'].selection).get(record.maintenance_type)}.",
    #                     subject="Maintenance Type Changed"
    #             )
    #     return res
