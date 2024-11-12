from odoo import models, fields


class LuxuryProperty(models.Model):
    # لازم لما اعمل وراثه   delegation اعمل علاقة many2one مع النموذج اللي هغمل معاه وراثه
    # بعد كدااضيف الحقل اللي  عملت معاه وراثه ك value للنموذج اللي ورثته وهو هي property_id
    # بعد كدا اي حقل  required موجود في النموذج اللي هورثه لازم اضيفو في xml عندي
    # كدا اقدر اوصل لكل الحقول اللي موجوده في النموذج اللي ورثتها
    # واقدر اضيف اي حاجه محتاجاها منهم من غير ما اعيد كتابة الحقول  من الاول

    _name = 'luxury.property'
    _inherits = {'property.items': 'property_id', }

    property_id = fields.Many2one(
            'property.items',
            string='Property',
            required=True,
            ondelete='cascade',
    )
    luxury_features = fields.Text(string="Luxury Features")
    is_vip = fields.Boolean(string="VIP Access")
