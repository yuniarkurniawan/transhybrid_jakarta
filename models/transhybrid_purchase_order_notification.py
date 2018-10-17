from odoo import models, fields, api

class TranshbridPurchaseOrderNotificationNotification(models.Model):
    
    _name = "transhybrid.purchase.order.notification"
    _description = "Transhybrid Notification"
    _order = "id desc"
    _inherit = ['ir.needaction_mixin']


    name	         = 	fields.Char('Purchase Order Number', required=True)
    customer_name    =  fields.Char('Customer Name')
    order_date       =  fields.Datetime('Purchase Order Date')
    rfs_date         =  fields.Datetime('RFS Date')
    duration         =  fields.Char('Duration')

    amount_total     =  fields.Float('Amount Total')
    description		 =	fields.Text('Description')
    state            =  fields.Selection([(1,'Not Confirmed'),
                                            (2,'Confirmed'),
                                            ],'State',readonly=True, default=1)


    @api.model
    def _needaction_domain_get(self):
        
        return [('state', '=', 1)]

    @api.multi
    def action_notification(self):

        if(self.id):

            self.write({
                'state':2,
            })