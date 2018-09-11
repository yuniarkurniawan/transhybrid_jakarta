#from openerp.osv import osv
#from openerp.report import report_sxw

from openerp import api,models


class TranshybridPOServiceItemReportPDF(models.AbstractModel):

	_name = "report.transhybrid_jakarta.po_service_item_report_pdf"


	def get_all_data(self, docs):

		listingData = []
		for object in docs:
			listingData.append(object.name)

		listing = list(set(listingData))

		return listing

	'''
	@api.model
    def render_html_from_odoo_test(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': account_res,
        }
        return self.env['report'].render('account.report_trialbalance', docargs)
	'''

    
	@api.multi
	def render_html_haduh(self,docids,data=None):

		report_obj = self.env['report']
		report = report_obj._get_report_from_name('transhybrid_jakarta.po_service_item_report_pdf')

		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_ids', []))

		print "DOCS ::::: ", docs

		docargs = {

			'doc_ids' : docids,
			'doc_model':report.model,
			'docs':docs,
		}

		return report_obj.render("transhybrid_jakarta.po_service_item_report_pdf")



	@api.multi
	def render_html(self,docids,data=None):

		report_obj = self.env['report']
		report = report_obj._get_report_from_name('transhybrid_jakarta.po_service_item_report_pdf')

		#print " DOCIDS :: ", docids

		#docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
		#print " ------------------ ", docs

		
		docargs = {

			'doc_ids' : docids,
			'doc_model':report.model,
			'docs':self,
		}

		return report_obj.render("transhybrid_jakarta.po_service_item_report_pdf")
