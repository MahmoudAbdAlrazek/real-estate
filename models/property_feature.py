import random

from odoo import fields, models


class PropertyFeature(models.Model):
    _name = 'property.feature'
    _description = 'Property Feature'

    name = fields.Char(string='Feature Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    color = fields.Integer(string='Color', default=lambda self: random.randint(0, 11))

    # color = fields.Integer(string='Color Index', default=0)  # حقل اللون
    # lambda self: هي دالة مبسطة (لامدا) تأخذ self, كمعامل لتحديد النموذج الحالي.
    # color = fields.Integer(string='Color', default=lambda self: random.randint(0, 11))
    # # حل اخر
    # color = fields.Integer(string='Color', default=0)
    #
    # @api.model
    # def create(self, vals):
    #     # تعيين لون عشوائي إذا لم يتم تحديده
    #     if not vals.get('color'):
    #         vals['color'] = random.randint(1, 10)  # اختيار رقم عشوائي بين 1 و 10 للألوان
    #     return super(PropertyFeature, self).create(vals)
