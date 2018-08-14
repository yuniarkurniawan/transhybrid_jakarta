from odoo import models, fields, api,  _
from odoo.tools.safe_eval import safe_eval

class TranshybridCRMModel(models.Model):

	_name     = "crm.lead"
	_inherit  = "crm.lead"

	description		=	fields.Text('Description')

	@api.multi
	def create_order(self):

		form_view_id = (self.env['ir.ui.view'].search([('name','=','sale.order.thc.form.view')])[0].id)
		tree_view_id = (self.env['ir.ui.view'].search([('name','=','sale.order.thc.tree.view')])[0].id)

		'''
		return {
            'name'              : 'Purchase Order',
            'res_model'         : 'sale.order',
            "views"             : [[tree_view_id, "tree"], [form_view_id, "form"]],
            'view_mode'         : 'tree,form',
            'search_view_id'    : form_view_id,
            'target'            : 'current',
            'context'           : {},
            'domain'            : [('payment_type','!=', payment_type_ids[0])],
            'type'              : 'ir.actions.act_window',
            'help'              : 'Di sini anda dapat menambahkan, merubah, dan menghapus Pembayaran Pembelian.'
        }
        '''



		return {
            'name'              : 'Purchase Order',
            'res_model'         : 'sale.order',
            'views'             : [(form_view_id, "form")],
            'view_mode'         : 'form',
            'view_type'			: 'form',
            'search_view_id'    : form_view_id,
            'target'            : 'current',
            'context'           : {},
            'domain'            : [],
            'type'              : 'ir.actions.act_window',
            'help'              : ''
        }