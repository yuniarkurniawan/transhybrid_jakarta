from odoo import models, fields, api,  _
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, date, timedelta
import re
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time
import dateutil.parser
import os

class TranshybridSurveyNews(models.Model):

	_name     = "transhybrid.survey.news"
	_order = "id asc"


	# SALE ORDER
	name 					=	fields.Char('BAS Number')
	name_show 				=	fields.Char('BAS Number')
	sale_order 				=	fields.Many2one('sale.order',required=True)
	sale_order_line			=	fields.Many2one('sale.order.line',string='Order Products',
									required=True)
	sale_order_line_service =	fields.Many2one('sale.order.line.service.model',required=True)

	state    				=   fields.Selection([
                                    (1,'Draft'),
                                    (2,'Signed')],'State',default=1)

	# PEMBBUAT ORDER
	name_pembuat_order      =   fields.Char('Nama Pembuat Order')
	nik_pembuat_order		=	fields.Char('NIK Pembuat Order')
	telp_pembuat_order		=	fields.Char('Telp. Pembuat Order')
	alamat_pembuat_order	=	fields.Text('Alamat Pembuat Order')


	# JENIS LAYANAN
	is_internet				=	fields.Boolean('Is Internet')
	is_voice				=	fields.Boolean('Is Voice')
	is_local_loop			=	fields.Boolean('Is Local Loop')
	
	is_sip_trunk			=	fields.Boolean('Is SIP Trunk')
	is_metro_e				=	fields.Boolean('Is Metro E')
	is_tdm					=	fields.Boolean('Is TDM')

	is_vsat					=	fields.Boolean('Is VSAT')
	is_dw_dm				=	fields.Boolean('Is DWDM')


	# DATA PELANGGAN
	nama_pelanggan 			=	fields.Char('Nama Pelanggan')
	alamat_pelanggan		=	fields.Text('Alamat Survey')
	telp_pelanggan			=	fields.Char('Telp. Pelanggan')
	email_pelanggan			=	fields.Char('Email Pelanggan')
	akses_permit_pelanggan	=	fields.Char('Akses Permit Lapangan')
	catatan_pelanggan		=	fields.Text('Catatan Pelanggan')


	# NAMA MITRA
	nama_mitra 				=	fields.Char('Nama Mitra')
	alamat_mitra			=	fields.Text('Alamat Mitra')
	telp_mitra				=	fields.Char('Telp. Mitra')


	# MEDIA TRANSMISI
	is_fiber_optic			=	fields.Boolean('Is Fiber Optic')
	is_wire_less			=	fields.Boolean('Is Wire Less')
	is_ethernet				=	fields.Boolean('Is Ethernet')
	is_radio				=	fields.Boolean('Is Radio')
	is_vsat_2				=	fields.Boolean('Is VSAT')


	# KONDISI TEMPAT
	longitude 				=	fields.Float('Longitude',digits=(0,6),default=0.0)
	latitude 				=	fields.Float('Latitude',digits=(0,6),default=0.0)
	nama_tempat 			=	fields.Char('Nama Tempat')

	penangkal_petir			=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											],'Penangkal Petir',required=True,default=2)


	air_conditione			=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											],'Air Condition',required=True,default=2)


	grouding				=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											],'Grounding',required=True,default=2)


	sumber_power			=	fields.Selection([(1,'PLN'),
											(2,'Genset'),
											(3,'Baterai'),
											(4,'UPS'),
											],'Sumber Power',required=True,default=1)

	kabel_tray				=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											],'Kabel Tray',required=True,default=2)


	tipe_power				=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											],'Tipe Power',required=True,default=2)

	pondasi					=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											],'Pondasi',required=True,default=2)

	rack					=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											],'Rack',required=True,default=2)


	kabel_outdoor			=	fields.Selection([(1,'RG6'),
											(2,'Fiber Optic'),
											(3,'RJ45'),
											(4,'E1'),
											],'Penangkal Petir',required=True,default=2)

	kabel_indoor			=	fields.Selection([(1,'RG6'),
											(2,'Fiber Optic'),
											(3,'RJ45'),
											(4,'E1'),
											],'Penangkal Petir',required=True,default=2)

	panjang_kabel_power		=	fields.Float('Panjang Kabel Power',default=0.0)
	panjang_kabel_grounding	=	fields.Float('Panjang Kabel Grounding',default=0.0)
	jenis_kunci				=	fields.Char('Jenis Kunci')

	pemilik_kunci			=	fields.Char('Pemilik Kunci')
	kesiapan_perangkat		=	fields.Selection([(1,'Siap'),
											(2,'Tidak Siap'),
											],'Kesiapan Perangkat',required=True,default=2)

	kesiapan_rack			=	fields.Selection([(1,'Siap'),
											(2,'Tidak Siap'),
											],'Kesiapan Rack',required=True,default=2)

	catatan_kondisi_tempat	=	fields.Text('Catatan Kondisi Tempat')


	def get_month_converter(self, paramMonth):

		tmpOut = ""
		if(int(paramMonth)==1):
			tmpOut = "I"
		elif(int(paramMonth)==2):
			tmpOut = "II"
		elif(int(paramMonth)==3):
			tmpOut = "III"
		elif(int(paramMonth)==4):
			tmpOut = "IV"
		elif(int(paramMonth)==5):
			tmpOut = "V"
		elif(int(paramMonth)==6):
			tmpOut = "VI"
		elif(int(paramMonth)==7):
			tmpOut = "VII"
		elif(int(paramMonth)==8):
			tmpOut = "VIII"
		elif(int(paramMonth)==9):
			tmpOut = "IX"
		elif(int(paramMonth)==10):
			tmpOut = "X"
		elif(int(paramMonth)==11):
			tmpOut = "XI"
		else:
			tmpOut = "XII"

		return tmpOut


	@api.onchange('sale_order_line_service')
	def get_bas_number(self):

		tmpLoanNumber = []
		val = {}

		now = datetime.now()
		tmpYear = now.year
		tmpYear = str(tmpYear)

		tmpMonth = now.month
		tmpMonth = self.get_month_converter(tmpMonth)


		if(self.sale_order_line_service):
			serviceCode = self.sale_order_line_service.service_id.service_code
			serviceCode = str(serviceCode).lower()
			serviceCode = 'bas.'+ serviceCode

			nextNumber = self.env['ir.sequence'].get(str(serviceCode))
			nextNumber = str(nextNumber)

			tmpOutNumber = ""
			if(len(nextNumber)<=3):
				tmpOutNumber = str(nextNumber).zfill(3)
				tmpLoanNumber.append(tmpOutNumber)
			else:
				tmpOutNumber = str(nextNumber)
				tmpLoanNumber.append(tmpOutNumber)


			tmpLoanNumber.append("/BAS-PROJECT/")
			tmpLoanNumber.append(str(self.sale_order_line_service.service_id.product_id.code))
			tmpLoanNumber.append("/")
			tmpLoanNumber.append(tmpMonth)
			tmpLoanNumber.append("/")
			tmpLoanNumber.append(tmpYear)

			outNumber = ''.join(tmpLoanNumber)
						
			val = {
				'name' : outNumber,
				'name_show' : outNumber,
			}
			

		return {
			'value' : val,
		}

	
	@api.model
	def create(self, values):

		print " +++++++++++++++++++ "
		values['name'] = values['name_show']

		return super(TranshybridSurveyNews, self).create(values)
  

	@api.onchange('sale_order')
	def onchange_sale_order_survey_news(self):

		val = {}

		if(self.sale_order):

			val = {
				'nama_pelanggan' : self.sale_order.partner_id.name,				
			}

		return {
			'value': val
		}

	@api.onchange('sale_order_line_service')
	def onchange_sale_order_line_service_survey_news(self):

		val = {}

		if(self.sale_order_line_service):
			val = {
				'alamat_pelanggan'  : self.sale_order_line_service.address,
				'telp_pelanggan'	: self.sale_order_line_service.assign_to.user_phone,				
			}


		return {
			'value' : val
		}