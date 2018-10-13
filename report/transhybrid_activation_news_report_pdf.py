from openerp import api,models

class TranshybridPOServiceItemReportPDF(models.AbstractModel):

	_name = "report.transhybrid_jakarta.activation_news_report_pdf"


	def get_all_data(self, docs):

		listingData = []
		for object in docs:
			listingData.append(object.name)

		listing = list(set(listingData))

		return listing

	    
	@api.multi
	def render_html(self,docids,data=None):

		report_obj = self.env['report']
		report = report_obj._get_report_from_name('transhybrid_jakarta.activation_news_report_pdf')

		docargs = {

			'doc_ids' : docids,
			'doc_model':report.model,
			'docs':self,
		}

		return report_obj.render("transhybrid_jakarta.activation_news_report_pdf")
