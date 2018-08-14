from odoo import models, fields, api,  _
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, date

class TranshybridWorkerPurchaseOrderReportModel(models.Model):

	_name="transhybrid.worker.purchase.order.report"
	_description = "Transhybrid Worker Purchase Order Report Model"
	_order = "id asc"

	worker_id				=	fields.Many2one('res.users',string='Assign To',required=True)
	worker_name				=	fields.Char(related='worker_id.name',string="User Name")

	purchase_order_lie_ids	=	fields.One2many('transhybrid.worker.purchase.order.line.report','worker_purchase_id','Purchase Order Line')
	


class TranshybridWorkerPurchaseOrderReportModel(models.Model):

	_name="transhybrid.worker.purchase.order.line.report"
	_description = "Transhybrid Worker Purchase Order Line Report Model"
	_order = "id asc"


	worker_purchase_id	=	fields.Many2one('transhybrid.worker.purchase.order.report')
	order_id 			=	fields.Many2one('sale.order')
	order_name 			=	fields.Char(related='order_id.name','Purchase Order Name')
	