#from openerp.osv import osv
#from openerp.report import report_sxw

from openerp import api,models


class TranshybridPOServiceItemReportPDF(models.AbstractModel):

	_name = "report.transhybrid_jakarta.po_service_item_report_pdf"


	'''
	@api.model
	def render_html(self,docids,data=None):
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('fleet_repair_management.report_fleet_job_card')
		fleet_args = {
			'doc_ids' : docids,
			'doc_model' : report.fleet_repair,
			'docs' : self,
		}

		return report_obj.render('fleet_repair_management.report_fleet_job_card')
	'''

	def get_all_data(self, docs):

		listingData = []
		for object in docs:
			listingData.append(object.name)

		listing = list(set(listingData))

		return listing

	@api.multi
	def render_html(self,docids,data=None):

		report_obj = self.env['report']
		report = report_obj._get_report_from_name('transhybrid_jakarta.po_service_item_report_pdf')

		docargs = {

			'doc_ids' : docids,
			'doc_model':report.model,
			'docs':self,
		}

		return report_obj.render("transhybrid_jakarta.po_service_item_report_pdf")
