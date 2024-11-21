from odoo import fields, models, _
from odoo.exceptions import ValidationError


class ChangeStateWizard(models.TransientModel):
    _name = 'change.state.wizard'
    _description = 'Change State Wizard'
    # خطوه اولي لانشاء ويزرد
    new_state = fields.Selection(
            [
                    ('available', 'available'),
                    ('rented', 'rented'),
                    ('sold', 'sold')
            ], string='New State', required=True)

    reason = fields.Text(string='Reason', required=True)

    def change_state(self):
        # الحصول على معرف العنصر النشط من سياق التنفيذ
        active_id = self.env.context.get('active_id')
        # البحث عن العنصر العقاري باستخدام المعرف الذي تم الحصول عليه
        property_item = self.env['property.items'].browse(active_id)

        # تحقق مما إذا كان العنصر العقاري موجودًا
        if not property_item.exists():
            raise ValidationError(_('the property item does not exist.'))

        # تحقق من الحالة الحالية
        if property_item.state != 'closed':
            raise ValidationError(_('you can only change the state of a closed property item.'))

        # خطوه حامسه لتخزين اسباب تغيير
        # تخزين اسم عقار وسبب وتاريخ ووقت وحاله جديده وحاله  قديمه التغيير عند تغيير
        # الحالة في نموذج property.state.change.reason
        self.env['property.state.change.reason'].create(
                {
                        'property_id'  : property_item.id,
                        'change_reason': self.reason,
                        'change_date'  : fields.Datetime.now(),  #
                        'old_state'    : property_item.state,
                        'new_state'    : self.new_state,
                })

        # تغيير الحالة إلى الحالة الجديدة
        property_item.state = self.new_state
