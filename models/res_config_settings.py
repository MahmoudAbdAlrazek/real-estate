from odoo import models, fields


class PropertyItemsSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    property_type_filter = fields.Selection(
            [
                    ('all', 'All Types'),
                    ('residential_only', 'Residential Only'),
                    ('commercial_only', 'Commercial Only'),
            ], string="Filter Property Types", default='all')

    reminder_days = fields.Integer(string="Reminder Days for Expected Selling Date", default=7)

    def get_values(self):
        res = super(PropertyItemsSettings, self).get_values()
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        res.update(
                property_type_filter=IrConfigParam.get_param('property_items.property_type_filter', default='all'),
                reminder_days=int(IrConfigParam.get_param('property_items.reminder_days', default=7)),
        )
        return res

    def set_values(self):
        super(PropertyItemsSettings, self).set_values()
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        IrConfigParam.set_param('property_items.property_type_filter', self.property_type_filter)
        IrConfigParam.set_param('property_items.reminder_days', self.reminder_days)
