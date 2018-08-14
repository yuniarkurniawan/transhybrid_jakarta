from odoo import api, fields, models, tools, _
from datetime import datetime, date

class TranshybridCustomerModel(models.Model):

	_name     = "res.partner"
	_inherit  = "res.partner"

	is_registered		=	fields.Boolean('Is Registered',default=False)
	customer_code		= 	fields.Char('Customer Code')



	@api.model
	def create(self,vals):

		if(vals['customer']):
			vals['customer_code'] = self.generate_customer_number()
		
		return super(TranshybridCustomerModel, self).create(vals)


	@api.multi
	def generate_customer_number(self):

		now = datetime.now()
		generatedNumberModel = self.env['transhybrid.generated.number']
		listPoNumber = []

		tmpYear = now.year
		tmpYear = str(tmpYear)
		tmpYear = tmpYear[2:4]

		tmpMonth = now.month 
		dataPool = generatedNumberModel.search([('is_cust','=',True),('year','=',int(tmpYear)),('month','=',int(tmpMonth))])


		listPoNumber.append("C")
		listPoNumber.append(str(tmpYear))
		listPoNumber.append(str(tmpMonth).zfill(2))

		if(len(dataPool)==0):
			
			# data kosong
			dataGenerateValue = {
				'is_cust' : True,
				'year'  : int(tmpYear),
				'month' : int(tmpMonth),
				'last_number' : 1
			}
			
			listPoNumber.append(str(1).zfill(5))
			generatedNumberModel.create(dataGenerateValue)
		
		else:

			# data tidak kosong
			tmpOutNumber = 0
			for outData in dataPool:
				tmpOutNumber = outData.last_number

				tmpOutNumber+=1	
				listPoNumber.append(str(tmpOutNumber).zfill(5))
				outData.last_number = tmpOutNumber

		
		return ''.join(listPoNumber) 
	