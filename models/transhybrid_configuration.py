from odoo import api, fields, models, tools, _

class TranshybridConfiguration(models.Model):
	
	_name = "transhybrid.configuration"
	_description = "Transhybrid Configuration"
	_order = "id asc"

	# ----- begin email configuration
	email_user      	=   fields.Char('User Email',size=100)
	email_sender    	=   fields.Char('Pengririm Email',size=100)

	email_password  	=   fields.Char('Password Pengirim Email',size=100)
	is_email_server_configuration  =   fields.Boolean('Is Email Server Configuration')
	email_host      	=   fields.Char('Host Email',size=100)
	
	email_port      	=   fields.Char('Port Email',size=100)
	email_server_description = fields.Text('Description')
	# ---- end email configuration



	# ----- begin time token expired configuration
	time_expired 		=	fields.Integer('Time  Token Expired')
	is_time_token_configuration = fields.Boolean('Is Time Token')
	time_token_description = fields.Text('Description')
	# ----- end time token expired configuration


	# ----- begin email send to configuration
	email_send_to		=	fields.Char('Penerima Email',size=100)
	is_email_send_to	=	fields.Boolean('Is Email Send to')
	email_send_to_description = fields.Text('Description')