from odoo import models, fields, api,  _
import time
from datetime import datetime, date

class TranshybridUserModel(models.Model):

	_name     = "res.users"
	_inherit  = "res.users"

	user_phone			=	fields.Char('User Phone',required=True)
	user_address		=	fields.Text('User Addres')
	avatar 				= 	fields.Many2one('transhybrid.avatar',string="Avatar",compute="get_avatar",compute_sudo=True,store=True)
	
		
	user_condition 	= 	fields.Selection([
									(1,'Internal'),
									(2,'Others')],'Company',default=1)

	user_company		=	fields.Many2one('res.partner',domain=[('supplier', '=', 1)])
	is_manager_other_company = fields.Selection([
									(1,'Yes'),
									(2,'No')],'Is Manager',default=1)


	@api.one
	@api.depends('image_medium')
	def get_avatar(self):

		if self.avatar:
			self.avatar.image = self.image_medium
		else:
			avatar_id = self.env['transhybrid.avatar'].create({'user_id':self.id,'image': self.image_medium})
			self.avatar = avatar_id 
			
		

class TranshybridUserManagementToken(models.Model):

	_name = "res.users.token"
	_description = 'List Token'
	_order = "id desc"

	res_id		=	fields.Many2one('res.users',string='Token')
	token_data	=	fields.Char('Token')
	time_token	=	fields.Datetime('Token Time',default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
	

	
class TranshybridAvatar(models.Model):

	_name = "transhybrid.avatar"
	_description = 'List Avatar'
	_order = 'id desc'

	image = fields.Binary(string='Image') 
	user_id 	=	fields.Many2one('res.users',string='Users') 