from odoo import models, fields, api,  _, exceptions
#from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import time
from datetime import datetime, date
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import xlsxwriter
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class TranshybridSaleOrderReport(models.TransientModel):

	_name = 'transhybrid.sale.order.report'
	_description = "Transhybrid Sale Order Report"
	
	
	purchase_order_id 	= fields.Many2one('sale.order',string='Purchase Order')
	dateFrom  	      	= fields.Date('Date From',default=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),required=True)
	dateTo  	      	= fields.Date('Date To',default=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),required=True)
    


	def generate_sale_order_report(self,data):

		context = self._context

		datas = {'ids': context.get('active_ids', [])}
		datas['model'] = 'transhybrid.sale.order.report'
		datas['form'] = self.read()[0]

		return {

			'type': 'ir.actions.report.xml',
			'report_name': 'purchase_order_detail.xlsx',
			'datas': datas,
			'name': 'Purchase Order'

			}



class TranshybridSaleOrdertGenerateExcel(ReportXlsx):

	def generate_xlsx_report(self, workbook, data, lines):
		
		saleOrderModel = self.env['sale.order']

		worksheet = workbook.add_worksheet("Purchase Order")
		
		worksheet.set_column(0, 0, 10) # A:A = 10
		worksheet.set_column(1, 1, 20)
		worksheet.set_column(2, 2, 20)
		worksheet.set_column(3, 3, 30)
		worksheet.set_column(4, 4, 30)
		worksheet.set_column(5, 5, 30)
		worksheet.set_column(6, 6, 30)

		
		no = 1
		curr_row = 1

		cell_format = workbook.add_format({'bg_color': 'gray', 'align':'center'})
		cell_format2 = workbook.add_format({'bg_color': 'white', 'align':'left'})
		cell_format3 = workbook.add_format({'bg_color': 'white', 'align':'right','num_format': '#,##0.00'})

		cell_format.set_border(1)
		cell_format2.set_border(1)
		cell_format3.set_border(1)
		
		
		dataPurchaseOrder = ""
		if(data['form']['purchase_order_id']!=False):
			tmpPurchaseOrderId = data['form']['purchase_order_id'][0]
			dataPurchaseOrder = saleOrderModel.search([('id','=',int(tmpPurchaseOrderId)),('date_order','>=',data['form']['dateFrom']),('date_order','<=',data['form']['dateTo'])])
		else:
			dataPurchaseOrder = saleOrderModel.search([('date_order','>=',data['form']['dateFrom']),('date_order','<=',data['form']['dateTo'])])


		for outData in dataPurchaseOrder:


			worksheet.write(curr_row,0,"PO. Number")
			worksheet.write(curr_row,1,str(outData.name))
			curr_row+=1

			worksheet.write(curr_row,0,"Order Date")
			worksheet.write(curr_row,1,str(outData.create_date))
			curr_row+=1

			worksheet.write(curr_row,0,"Customer")
			worksheet.write(curr_row,1,str(outData.partner_id.name))
			curr_row+=1

			worksheet.write(curr_row,0,"Assign To")
			worksheet.write(curr_row,1,str(outData.assign_to.name))
			curr_row+=1			

			worksheet.write(curr_row,0,"Confirmation Date")
			if(outData.confirmation_date!=False):
				worksheet.write(curr_row,1,str(outData.confirmation_date))
			else:
				worksheet.write(curr_row,1,"-")

			curr_row+=2

			# ============ BEGIN HEADER
			worksheet.write(curr_row, 0, "No.", cell_format)
			worksheet.write(curr_row, 1, "Porduct", cell_format)
			worksheet.write(curr_row, 2, "Description", cell_format)
			worksheet.write(curr_row, 3, "Ordered Qty", cell_format)
			worksheet.write(curr_row, 4, "Unit Price", cell_format)
			worksheet.write(curr_row, 5, "Taxes", cell_format)
			worksheet.write(curr_row, 6, "Sut Total", cell_format)
			
			curr_row+=1

			indexNumber = 1
			for outDataLine in outData.order_line:

				worksheet.write(curr_row, 0, indexNumber, cell_format2)
				worksheet.write(curr_row, 1, outDataLine.product_id.name, cell_format2)
				worksheet.write(curr_row, 2, outDataLine.product_id._description, cell_format2)

				worksheet.write(curr_row, 3, outDataLine.product_uom_qty, cell_format3)
				worksheet.write(curr_row, 4, outDataLine.price_unit, cell_format3)
				worksheet.write(curr_row, 5, outDataLine.tax_id.amount, cell_format3)
				
				worksheet.write(curr_row, 6, outDataLine.price_subtotal, cell_format3)
				
				curr_row+=1
				indexNumber+=1

			curr_row+=2




		# ========== BEGIN DETAIL PURCHASE ORDER
		curr_row = 1
		
		worksheetDetail = workbook.add_worksheet("Detail Purchase Order")
		worksheetDetail.set_column(0, 0, 10) # A:A = 10
		worksheetDetail.set_column(1, 1, 25)
		worksheetDetail.set_column(2, 2, 30)
		worksheetDetail.set_column(3, 3, 40)
		worksheetDetail.set_column(4, 4, 20)

		for outData in dataPurchaseOrder:


			worksheetDetail.write(curr_row,0,"PO. Number")
			worksheetDetail.write(curr_row,1,str(outData.name))
			curr_row+=1

			worksheetDetail.write(curr_row,0,"Order Date")
			worksheetDetail.write(curr_row,1,str(outData.create_date))
			curr_row+=1

			worksheetDetail.write(curr_row,0,"Customer")
			worksheetDetail.write(curr_row,1,str(outData.partner_id.name))
			curr_row+=1

			worksheetDetail.write(curr_row,0,"Assign To")
			worksheetDetail.write(curr_row,1,str(outData.assign_to.name))
			curr_row+=1			

			worksheetDetail.write(curr_row,0,"Confirmation Date")
			if(outData.confirmation_date!=False):
				worksheetDetail.write(curr_row,1,str(outData.confirmation_date))
			else:
				worksheetDetail.write(curr_row,1,"-")

			curr_row+=2

			for outDataLine in outData.order_line:
				worksheetDetail.write(curr_row,0,"Product")
				worksheetDetail.write(curr_row,1,str(outDataLine.product_id.name))
				curr_row+=1

				# ============ BEGIN HEADER
				worksheetDetail.write(curr_row, 0, "No.", cell_format)
				worksheetDetail.write(curr_row, 1, "Service Name", cell_format)
				worksheetDetail.write(curr_row, 2, "PIC", cell_format)
				worksheetDetail.write(curr_row, 3, "Address", cell_format)
				worksheetDetail.write(curr_row, 4, "State", cell_format)
				curr_row+=1

				indexNumber = 1
				for outDataLineService in outDataLine.sale_order_line_service_ids:
					
					worksheetDetail.write(curr_row, 0, indexNumber, cell_format2)
					worksheetDetail.write(curr_row, 1, outDataLineService.service_id.name, cell_format2)
					worksheetDetail.write(curr_row, 2, outDataLineService.pic, cell_format2)

					worksheetDetail.write(curr_row, 3, outDataLineService.address, cell_format2)
					worksheetDetail.write(curr_row, 4, outDataLineService.state, cell_format2)
					curr_row+=1
					indexNumber+=1

				curr_row+=2

			curr_row+=2

TranshybridSaleOrdertGenerateExcel('report.purchase_order_detail.xlsx', 'transhybrid.sale.order.report')
