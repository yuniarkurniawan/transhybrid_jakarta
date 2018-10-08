from odoo import models, fields, api,  _
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError
import time
import dateutil.parser

class TranshybridTestingNews(models.Model):

	_name   = "transhybrid.testing.news"
	_id 	= "id asc"

	# SALE ORDER
	sale_order 				=	fields.Many2one('sale.order',required=True)
	sale_order_line			=	fields.Many2one('sale.order.line',string='Order Products',
									required=True)
	sale_order_line_service =	fields.Many2one('sale.order.line.service.model',required=True)

	state    				=   fields.Selection([
                                    (1,'Draft'),
                                    (2,'Signed')],'State',default=1)


	# DATA PELANGGAN
	nama_pelanggan 			=	fields.Char('Nama Pelanggan')
	alamat_pelanggan		=	fields.Text('Alamat Survey')
	longitude 				=	fields.Float('Longitude',digits=(0,6),default=0.0)
	
	latitude 				=	fields.Float('Latitude',digits=(0,6),default=0.0)
	eta 					=	fields.Char('Waktu Tempuh')
	alamat_pengetesan		=	fields.Char('Alamat Instalasi A')
	
	pic_pelanggan			=	fields.Char('PIC Pelanggan')
	jabatan_pic_pelanggan	=	fields.Char('Jabatan PIC Pelanggan')
	telp_pic_pelanggan		=	fields.Char('Telp. PIC Pelanggan')
	
	email_pic_pelanggan		=	fields.Char('Email PIC Pelanggan')
	

	#AKSES LOKASI 			
	autorisasi 				=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											(3,'Lainnya')
											],'Akses Lokasi',required=True,default=3)

	surat_izin				=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											(3,'Lainnya')
											],'Surat Izin',required=True,default=3)

	waktu_izin				=	fields.Selection([(1,'1 X 24 Jam'),
											(2,'Tidak Ada'),
											(3,'Lainnya')
											],'Waktu Izin',required=True,default=3)

	alur_perizinan			=	fields.Selection([(1,'Security'),
											(2,'BM'),
											(3,'Lainnya')
											],'Alur Perizinan',required=True,default=3)

	emergency_call			=	fields.Char('Emergency Call')
	catatan_akses_lokasi	=	fields.Text('Catatan Akses Lokasi')


	#KONDISI LOKASI
	ruang_server			=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											],'Ruang Server',required=True,default=2)

	air_conditioner			=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											],'Air Conditioner',required=True,default=2)

	cable_shaft 			=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											],'Cable Shaft',required=True,default=2)

	label_perangkat			=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											],'Label perangkat',required=True,default=2)


	ac_power				=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											],'AC Power',required=True,default=2)


	rack					=	fields.Selection([(1,'Ada'),
											(2,'Tidak Ada'),
											],'Rack',required=True,default=2)


	#PEKERJAAN
	ping_test 				=	fields.Boolean('Ping Test')
	bert_test 				=	fields.Boolean('Bert Test')
	otdr_test 				=	fields.Boolean('OTDR Test')
	bandwith_test 			=	fields.Boolean('Bandwith Test')
	rfc_test 				=	fields.Boolean('RFC Test')
	core_test 				=	fields.Boolean('Core Test')
	boom_trafic 			=	fields.Boolean('Boom Trafic')
	tfgen 					=	fields.Boolean('TFGEN')


	#MEDIA
	is_fiber_optic			=	fields.Boolean('Fiber Optic')
	is_ethernet				=	fields.Boolean('Is Ethernet')
	is_wire_less			=	fields.Boolean('Is Wire Less')
	is_sip					=	fields.Boolean('Is SIP')
	is_tdm					=	fields.Boolean('Is TDM')
	is_vsat					=	fields.Boolean('Is VSAT')
	is_cooper 				=	fields.Boolean('Is Cooper')
	is_e1					=	fields.Boolean('Is E1')
	lastmile_cpe 			=	fields.Char('Lastmile CPE')
	bandwith				=	fields.Char('Bandwith')
	hasil_test				= 	fields.Selection([(1,'Ok'),
											(2,'Not OK'),
											],'Hasil Test',required=True,default=2)
	catata_hasil_test		=	fields.Text('Catatan Hasil Test')
	catatan_media			=	fields.Text('Catatan Media')


	#PELAKSANA
	nama_pelaksana			=	fields.Char('Pelaksana')
	jabatan_pelaksana		=	fields.Char('Jabatan Pelaksana')
	telp_pelaksana			=	fields.Char('Telp. Pelaksana')
	email_pelaksana			=	fields.Char('Email Pelaksana')




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