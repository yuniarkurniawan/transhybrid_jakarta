from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import ustr

import binascii
import pytz
import logging

from ast import literal_eval

from odoo.addons.base.ir.ir_mail_server import MailDeliveryException
from odoo.addons.auth_signup.models.res_partner import SignupError, now

_logger = logging.getLogger(__name__)


class TranshybridHREmployeeResUsers(models.Model):
	_inherit = 'res.users'


	job = fields.Char('Job Position', size=100)


	def get_reset_password_data(self, user_id):
		user = self.search([('id', '=', user_id)])
		token = binascii.hexlify(user.login)

		return token

	@api.multi
	def action_reset_password(self):
		
		create_mode = False
		expiration = False if create_mode else now(days=+1)

		self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

		template = False
		if create_mode:
			try:
				template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
			except ValueError:
				pass
		if not template:
			template = self.env.ref('auth_signup.reset_password_email')
		assert template._name == 'mail.template'

	
	@api.model
	def create(self, vals):
		if not vals.has_key('tz'):
			vals['tz'] = "Asia/Jakarta"
		return super(TranshybridHREmployeeResUsers, self).create(vals)