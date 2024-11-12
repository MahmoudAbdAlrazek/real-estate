from odoo import fields, models, _, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_ids = fields.One2many(
            'property.items',
            'res_partner_id',
            tracking=True,
            string='Property',
            domain="[('res_partner_id', '=', False)]",  # يعرض فقط العقارات غير المرتبطة بعملاء آخرين    )

    )
    property_count = fields.Integer(
            compute='_compute_property_count',
            string='Number of Properties',
            store=True
    )

    @api.depends('property_ids')
    def _compute_property_count(self):
        for partner in self:
            # partner.property_count = len(partner.property_ids)
            partner.property_count = len(partner.property_ids.ids)

    # الداله دي بتعرض ف chatter  لو ف تعديلات اضافت في العقارات للعميل دا
    def write(self, vals):
        # جمع أسماء العقارات قبل التحديث
        property_names_before = ', '.join(self.property_ids.mapped('name'))
        res = super(ResPartner, self).write(vals)
        # جمع أسماء العقارات بعد التحديث
        property_names_after = ', '.join(self.property_ids.mapped('name'))

        # التأكد إذا تم تغيير العقارات ثم إرسال الرسالة
        if property_names_before != property_names_after:
            self.message_post(body=f"Properties have been updated. New properties: {property_names_after}")

        return res

    # def action_view_properties(self):
    #     self.ensure_one()
    #     action = self.env.ref('real_estate.property_items_action').read()[0]
    #     action['domain'] = [('res_partner_id', '=', self.id)]
    #     return action

    def action_view_properties(self):
        """
        Opens a window showing related properties.
        :return: dict for the action
        """
        self.ensure_one()
        recs = self.mapped('property_ids')
        return {
                'type'     : 'ir.actions.act_window',
                'res_model': 'property.items',
                'name'     : _('Properties'),
                'view_mode': 'tree,form',
                'context'  : {
                        # دا لما اعمل عميل جديد واكون داخل من سمارت بتون بيجيب قيمه العميل الافتراضي للي داخل منه
                        # res_partner_id : - دا اسم الحقل اللي موجود في العميل الافتراضي
                        'default_res_partner_id': self.id,
                        # دي بتخلي العميل للقراءه فقط لما ادخل من سمارت بتون عندما انشا عميل جديد او ادخل علي العميل نفسه
                        'partner_readonly'      : True,

                        # 'create'                  : False,
                        # 'edit'  : False,
                },  # Pass the current partner ID in context
                'domain'   : [('id', 'in', recs.ids)],
                'views'    : [(False, 'tree'), (False, 'form')]
                # 'views'    : [(self.env.ref('real_estate.view_property_items_tree').id, 'tree'),
                #               (self.env.ref('real_estate.view_property_items_form').id, 'form')],
        }
