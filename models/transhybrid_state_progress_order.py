from odoo import models, fields, api,  _
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, date

class TranshybridStateProgressOrderModel(models.Model):

	_name="transhybrid.state.progress.order"
	_description = "Transhybrid State Progress Order"
	_order = "id asc"

	name			=	fields.Char('State Name',required=True)
	percentage		=	fields.Float('State Percentage',required=True)
	description		=	fields.Text(string='Field Label')