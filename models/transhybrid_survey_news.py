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
	sale_order 				=	fields.Many2one('sale.order',required=True,domain=[('state_new','=',4)])
	sale_order_line			=	fields.Many2one('sale.order.line',string='Order Products',
									required=True)
	sale_order_line_service =	fields.Many2one('sale.order.line.service.model',required=True)

	state    				=   fields.Selection([
                                    (1,'Draft'),
                                    (2,'Signed'),
                                    (3,'Cancel')],'State',default=1)

	sign_date 				=	fields.Date('Signed Date')
	tanggal 				=	fields.Char('Tanggal')
	hari_spell 				=	fields.Char('Hari')
	bulan_spell 			=	fields.Char('Bulan')
	tahun_spell 			=	fields.Char('Tahun')

	# PEMBBUAT ORDER
	name_pembuat_order      =   fields.Char('Nama Pembuat Order')
	nik_pembuat_order		=	fields.Char('NIK Pembuat Order')
	telp_pembuat_order		=	fields.Char('Telp. Pembuat Order')
	alamat_pembuat_order	=	fields.Text('Alamat Pembuat Order')
	email_pembuat_order		=	fields.Char('Email Pembuat Order')


	# JENIS LAYANAN
	is_internet				=	fields.Boolean('Is Internet')
	is_voice				=	fields.Boolean('Is Voice')
	is_local_loop			=	fields.Boolean('Is Local Loop')
	
	is_sip_trunk			=	fields.Boolean('Is SIP Trunk')
	is_metro_e				=	fields.Boolean('Is Metro E')
	is_tdm					=	fields.Boolean('Is TDM')

	is_vsat					=	fields.Boolean('Is VSAT')
	is_dw_dm				=	fields.Boolean('Is DWDM')
	keterangan_lainnya		=	fields.Char('Keterangan Lainnya')


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
	is_lainnya				=	fields.Boolean('Is Lainnya')
	


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

	def get_day_data(self,paramDay):

		
		tmpOutDay =  ""

		paramDay = paramDay.upper()
		if(paramDay=='SATURDAY'):
			tmpOutDay = "Sabtu"
		elif(paramDay=='SUNDAY'):
			tmpOutDay = "Minggu"
		elif(paramDay=='MONDAY'):
			tmpOutDay = "Senin"
		elif(paramDay=='TUESDAY'):
			tmpOutDay = "Selasa"
		elif(paramDay=='WEDNESDAY'):
			tmpOutDay = "Rabu"
		elif(paramDay=='THURSDAY'):
			tmpOutDay = "Kamis"
		else:
			tmpOutDay = "Jumat"
		
		return tmpOutDay


	def get_month_data(self,paramMonth):

		tmpParamMonth = int(paramMonth)
		tmpOutMonth =  ""

		if(tmpParamMonth==1):
			tmpOutMonth = "Januari"
		elif(tmpParamMonth==2):
			tmpOutMonth = "Februari"
		elif(tmpParamMonth==3):
			tmpOutMonth = "Maret"
		elif(tmpParamMonth==4):
			tmpOutMonth = "April"
		elif(tmpParamMonth==5):
			tmpOutMonth = "Mei"
		elif(tmpParamMonth==6):
			tmpOutMonth = "Juni"
		elif(tmpParamMonth==7):
			tmpOutMonth = "Juli"
		elif(tmpParamMonth==8):
			tmpOutMonth = "Agustus"
		elif(tmpParamMonth==9):
			tmpOutMonth = "September"
		elif(tmpParamMonth==10):
			tmpOutMonth = "Oktober"
		elif(tmpParamMonth==11):
			tmpOutMonth = "Nopember"
		else:
			tmpOutMonth = "Desember"

		return tmpOutMonth


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

		# MERUBAH STATUS MODEL SALE.ORDER.LINE.SERVICE.MODEL
		saleOrderLineServiceModel = self.env['sale.order.line.service.model']
		dataPool = saleOrderLineServiceModel.search([('id','=',int(values['sale_order_line_service']))])
		for dataOut in dataPool:
			dataOut.is_bas = 2


		values['name'] = values['name_show']

		return super(TranshybridSurveyNews, self).create(values)
  

	@api.multi
	def action_signed(self):

		if(self.id):

			tmpYear = datetime.now().strftime("%Y")
			

			tmpMonth = datetime.now().strftime("%m")
			
			tmpMonth = self.get_month_data(int(tmpMonth))
			tmpDay = datetime.now().strftime("%d")
			tmpDaySpell = datetime.now().strftime("%A")

			
			'''
			new_dict_up['hari'] = self.get_day_data(tmpDaySpell)
			new_dict_up['tanggal'] = tmpDay
			new_dict_up['bulan'] = tmpMonth
			
			new_dict_up['tahun'] = tmpYear

			sign_date 				=	fields.Datetime('Signed Date')
			hari_spell 				=	fields.Char('Hari')
			bulan_spell 			=	fields.Char('Bulan')
			tahun_spell 			=	fields.Char('Tahun')
			'''

			self.write({
                'state':2,
                'sign_date':date.today().strftime('%Y-%m-%d'),
                'tanggal':tmpDay,
                'hari_spell':self.get_day_data(tmpDaySpell),
                'bulan_spell':tmpMonth,
                'tahun_spell':tmpYear,
            })

			for out in self:
				
				saleOrderLineServiceModel = self.env['sale.order.line.service.model']
				dataPool = saleOrderLineServiceModel.search([('id','=',int(out.sale_order_line_service.id))])
				for dataOut in dataPool:
					dataOut.is_bas = 2

			

	@api.multi
	def action_cancel(self):

		if(self.id):

			self.write({
                'state':3
            })

			for out in self:
				
				saleOrderLineServiceModel = self.env['sale.order.line.service.model']
				dataPool = saleOrderLineServiceModel.search([('id','=',int(out.sale_order_line_service.id))])
				for dataOut in dataPool:
					dataOut.is_bas = 1
	

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