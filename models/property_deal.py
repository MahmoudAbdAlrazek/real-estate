from odoo import models, fields, api
from odoo.api import ondelete

from odoo.exceptions import ValidationError


class PropertyDeal(models.Model):
    _name = 'property.deal'
    _description = 'Property Deals Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # الوحدة تتيح التنبيهات والتنشيطات للمستخدمين على السجلات

    deal_id = fields.Char(string='Deal ID', required=True, unique=True)
    property_id = fields.Many2one('property.items', string='Property', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', readonly=True, string='Customer', related='property_id.partner_id')
    date = fields.Date(string='Deal Date', required=True, tracking=True, default=fields.Date.today)
    active = fields.Boolean(string="Archive", default=True, )

    # معلومات التواصل المرتبطة بالعميل
    phone = fields.Char(related='partner_id.phone', string='Phone', readonly=False)
    mobile = fields.Char(related='partner_id.mobile', string='Mobile', readonly=True)
    email = fields.Char(related='partner_id.email', string='Email', readonly=True)

    # الحقول المرتبطة بسعر وايجارالعقار
    sale_price = fields.Float(related='property_id.selling_price', string='Sale Price', readonly=True)
    rent_price = fields.Float(related='property_id.rental_price', string='Rent Price', readonly=True)

    # الحقول المرتبطة بالموقع الجغرافي للعقار
    city = fields.Char(related='property_id.city', string='City', readonly=True)
    state_id = fields.Many2one(related='property_id.state_id', comodel_name='res.country.state', string='State', readonly=True)
    country_id = fields.Many2one(related='property_id.country_id', comodel_name='res.country', string='Country', readonly=True)

    # إضافة الحقول Location و Address
    location = fields.Char(related='property_id.location', string='Location', readonly=True)
    address = fields.Char(related='property_id.address', string='Address', readonly=True)

    property_type = fields.Selection(related='property_id.property_type', string='Property Type', readonly=True)
    size = fields.Float(related='property_id.size', string='Size (in sq. meters)', readonly=True)

    # معلومات عن المشتري
    buyer_name = fields.Char(string='Buyer Name', required=True)
    buyer_phone = fields.Char(string='Buyer Phone', required=True)
    buyer_email = fields.Char(string='Buyer Email')
    notes = fields.Text(string='Notes')
    state = fields.Selection(
            [
                    ('available', 'Available'),
                    ('rented', 'Rented'),
                    ('sold', 'Sold'),
                    ('cancelled', 'Cancelled'),
            ],
            string='Deal State', compute='_compute_state',
            store=True, readonly=True, default='available')

    @api.constrains('buyer_phone')
    def _check_buyer_phone(self):
        for record in self:
            if record.buyer_phone and not record.buyer_phone.isdigit():
                raise ValidationError("Buyer Phone must contain only numbers.")

    @api.constrains('date')
    def _check_date(self):
        for record in self:
            if record.date and record.date > fields.Date.today():
                raise ValidationError('The deal date cannot be in the future.')

    @api.depends('property_id', 'property_id.state')
    def _compute_state(self):
        for record in self:
            if record.property_id:
                # Update the deal state based on the property state
                if record.property_id.state == 'available':
                    record.state = 'available'
                elif record.property_id.state == 'rented':
                    record.state = 'rented'  # Handle rented state
                elif record.property_id.state == 'sold':
                    record.state = 'sold'
                elif record.property_id.state == 'closed':
                    record.state = 'cancelled'
            else:
                record.state = 'available'

    @api.model
    def create(self, vals):
        # البحث عن صفقة موجودة للعقار المعني
        existing_deal = self.search([('property_id', '=', vals['property_id'])], limit=1)
        # إذا كانت هناك صفقة موجودة، يتم رفع استثناء
        if existing_deal:
            raise ValidationError('A deal already exists for this property. You cannot create another deal for the same property.')

        # استدعاء الدالة الأصلية لإنشاء السجل
        return super(PropertyDeal, self).create(vals)

    def write(self, vals):
        for record in self:
            # Check if the property_id is being changed
            if 'property_id' in vals:
                raise ValidationError('You cannot change the property of an existing deal.')
        return super(PropertyDeal, self).write(vals)

    # active = fields.Boolean(string="Archive", default=True,compute='_compute_active')
    # @api.depends('state')
    # def _compute_active(self):
    #     for record in self:
    #         if record.state in ['sold', 'cancelled']:
    #             record.active = False
    #         else:
    #             record.active = True
