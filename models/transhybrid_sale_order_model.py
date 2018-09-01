from odoo import models, fields, api,  _
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, date, timedelta
import re
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time

API_KEY = "AIzaSyB22AKzqTK5SNaVcKasEyrtXhMLiGn5UUM"

class TranshybridSaleOrderModel(models.Model):

    _name     = "sale.order"
    _inherit  = "sale.order"

    name_order          =   fields.Char('Sale Order Name')

    '''
    assign_to_choise    =   fields.Selection([
                                    (1,'Internal'),
                                    (2,'Vendor')],'Assign To',default=1)
    '''

    vendor_name_order   =   fields.Char('Vendor PO Number')
    
    '''
    vendor_assign_order =   fields.Many2one('res.partner',domain=[('supplier', '=', 1)])
    assign_to_by_vendor =   fields.Many2one('res.users',string='Assign To')
    '''

    #user_company        =   fields.Integer(related='assign_to_by_vendor.user_company')
    
    '''
    is_manager_other_company = fields.Selection([
                                    (1,'Yes'),
                                    (2,'No')],'Is Manager',related="assign_to_by_vendor.is_manager_other_company")
    '''
    
    '''
    assign_to           =   fields.Many2one('res.users',string='Assign To')
    '''

    state_new           =   fields.Selection([(1,'Prospect'),
                                            (2,'Deal'),
                                            (3,'In Progress'),
                                            (4,'Monitoring'),
                                            (5,'Cancel'),
                                            ],'State', default=1)

    rfs_date            =   fields.Datetime('RFS Date',default=fields.Datetime.now)
    

    deal_date           =   fields.Date('Deal Date')
    in_progres_date     =   fields.Date('Progress Date')
    monitoring_date     =   fields.Date('Monitoring Date')

    percentage_task     =   fields.Float('Progress',compute='_compute_total_progress')
    spelled_out         =   fields.Text('Spelled Out',compute='_compute_spelled_out')

    _sql_constraints = [('po_number_unique', 'unique(name_order)', 'Purchase Order Name Can Not Be Same.')]



    def push_pyfcm_multi(self, to_regids, message_title, message_body, data=False):
        
        push_service = FCMNotification(api_key=API_KEY)
        result = push_service.notify_multiple_devices(registration_ids=to_regids, 
        message_title=message_title,
        message_body=message_body)


    @api.multi
    def action_confirm(self):

        res = super(TranshybridSaleOrderModel, self).action_confirm()
        fcm_regids = [self.partner_id.fcm_regid]
        message_title = "SO Confirm"
        
        message_body  = "SO %s need action" % self.name
        data = {'model':'sale_order', 'id': self.id}
        self.push_pyfcm_multi(fcm_regids, message_title, message_body, data)
        
        return res


    @api.depends('order_line')
    def _compute_total_progress(self):

        for row in self:
            tmpProgresBar = 0
            tmpTotalSevice = 0
            for rowOrderline in row.order_line:
                for rowService in rowOrderline.sale_order_line_service_ids:
                    tmpTotalSevice+=1
                    #tmpProgresBar+=rowService.percentage
                    tmpProgresBar+=rowService.progress_bar_percentage


            if(tmpTotalSevice!=0):
                row.percentage_task = tmpProgresBar/tmpTotalSevice
            else:
                row.percentage_task = 0


    @api.multi
    def generate_po_number(self):

        now = datetime.now()
        generatedNumberModel = self.env['transhybrid.generated.number']
        listPoNumber = []

        tmpYear = now.year
        tmpYear = str(tmpYear)
        tmpYear = tmpYear[2:4]

        tmpMonth = now.month 
        dataPool = generatedNumberModel.search([('is_po','=',True),('year','=',int(tmpYear)),('month','=',int(tmpMonth))])


        listPoNumber.append("PO-CUST")
        listPoNumber.append(str(tmpYear))
        listPoNumber.append(str(tmpMonth).zfill(2))

        if(len(dataPool)==0):
            
            # data kosong
            dataGenerateValue = {
                'is_po' : True,
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



    @api.model
    def create(self, values):

        values['name_order'] = self.generate_po_number()
        values['name'] = values['name_order']
        values['state'] = 'sale'

        return super(TranshybridSaleOrderModel, self).create(values)



    @api.depends('amount_total')
    def _compute_spelled_out(self):

        tmpOutTerbilang = ""
        for row in self:
            tmpOutTerbilang = self._get_terbilang(int(row.amount_total))

            row.spelled_out = tmpOutTerbilang + "Rupiah"


    def _get_terbilang(self,n):

        k = ['','satu','dua','tiga','empat','lima','enam','tujuh','delapan','sembilan']
        a = [1000000000000000,1000000000000,1000000000,1000000,1000,100,10,1]
        s = ['kuadriliun','trilyun','milyar','juta','ribu','ratus','puluh','']

        i=0
        x=""
        n = int(n)

        while n>0 :

            b = a[i]
            c = n//b

            if c>=10 :
                x += self._get_terbilang(c) + s[i] + " "
            elif c>0 and c < 10 :
                x += k[c] + " "+ s[i] + " "
            else:
                x += ""

            i = i + 1
            n -= b * c
            x = re.sub(r'satu (ribu|ratus|puluh)',r'se\1',x)
            x = re.sub(r'sepuluh (\w+)',r'\1 belas',x)
            x = x.replace('satu belas','sebelas')

        return x.title()
        

    @api.multi
    def action_deal(self):

        if(self.id):
            self.write({
                'state_new':2,
                'deal_date':date.today().strftime('%Y-%m-%d')
            })

            for outData in self.order_line:
                outData.state_new = 2


    @api.multi
    def action_progress(self):

        if(self.id):
            self.write({
                'state_new':3,
                'in_progres_date':date.today().strftime('%Y-%m-%d')
            })

            for outData in self.order_line:
                outData.state_new = 3

    @api.multi
    def action_cancel(self):

        if(self.id):
            self.write({
                'state_new':5,
                'state':'cancel'
                })


    @api.multi
    def action_monitoring(self):

        if(self.id):
            self.write({
                'state_new':4,
                'monitoring_date':date.today().strftime('%Y-%m-%d'),
            })

            for outData in self.order_line:
                outData.state_new = 4

    '''
    @api.multi
    def write(self, vals):

        if(self):
            print " :::::::: "

        return super(TranshybridSaleOrderModel, self).write(vals) 
    '''


class TranshybridSaleOrderLineModel(models.Model):
    
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'


    state_new   =   fields.Selection([(1,'Prospect'),
                                            (2,'Deal'),
                                            (3,'In Progress'),
                                            (4,'Monitoring'),
                                            ],'State', default=1)

    total_service                   =   fields.Integer('Total Service')
    service_id                      =   fields.Many2one('product.thc.service')
    sale_order_line_service_ids     =   fields.One2many('sale.order.line.service.model','sale_order_line_id')
    sale_order_line_image_ids       =   fields.One2many('sale.order.line.image.model','sale_order_line_id','Sale Order Line Image')
    price_unit_compute              =   fields.Float('Price Unit Compute',compute='_compute_price_unit')
    


    @api.depends('sale_order_line_service_ids')
    def _compute_price_unit(self):

        tmpNewPrice = 0
        for row in self:
            for outData in row.sale_order_line_service_ids:
                tmpNewPrice+=outData.price_service


            row.price_unit_compute = tmpNewPrice
            row.price_unit = tmpNewPrice


    @api.onchange('total_service')
    def onchange_total_core(self):

        val = {}
        listDetailServicePickup = []


        # JIKA SUDAH ADA ORDER LINE SEBELUMNYA
        if(self.sale_order_line_service_ids):
            
            for outData in self.sale_order_line_service_ids:
                
                listDetailServicePickup.append((0,0,{
                        'service_id' : outData.service_id.id,
                        'item_service_id' : outData.item_service_id.id,
                        'assign_to_choise' : outData.assign_to_choise,

                        'price_service':outData.price_service,

                        'assign_to':outData.assign_to.id,
                        'price_service':outData.price_service,
                        'address':outData.address,
                        'pic':outData.pic,  
                                          
                    }))


            index = 1
            while(index<=self.total_service):

                listDetailServicePickup.append((0,0,{
                        'service_id' : self.service_id.id,
                        #'total_item_service' : 1,   
                                          
                    }))

                index+=1

            
        else:

            if(self.service_id):

                index = 1
                while(index<=self.total_service):

                    listDetailServicePickup.append((0,0,{
                            'service_id' : self.service_id.id,
                            #'total_item_service' : 1,   
                                             
                        }))

                    index+=1
                

        val = {
            'sale_order_line_service_ids':listDetailServicePickup,
            'total_service' : 0,
        }


        return {
            'value': val            
        }



class TranshybridSaleOrderLineServiceModel(models.Model):

    _name="sale.order.line.service.model"
    _description = "Sale Order Line Service Model"
    _order = "id asc"


    sale_order_line_id          =   fields.Many2one('sale.order.line','Sale Order Line',ondelete='cascade',required=True)
    
    service_id                  =   fields.Many2one('product.thc.service',required=True)
    item_service_id             =   fields.Many2one('product.thc.service.detail',required=True)
    item_service_progress       =   fields.Many2one('product.thc.service.detail.progress')

    progress_bar_percentage     =   fields.Integer(related='item_service_progress.progress_percentage',string="Progress")

    po_name                     =   fields.Char(related="sale_order_line_id.order_id.name_order",string="Po Number")
    company_name                =   fields.Many2one(related="sale_order_line_id.order_id.partner_id",string="Customer")
    po_order_date               =   fields.Datetime(related="sale_order_line_id.order_id.date_order",string="Order Date")
    rsf_date                    =   fields.Datetime(related="sale_order_line_id.order_id.rfs_date",string="RFS Date")

    assign_to_choise    =   fields.Selection([
                                    (1,'Internal'),
                                    (2,'Vendor')],'Assign To',default=1,required=True)

    assign_to           =   fields.Many2one('res.users',string='Assign To',required=True)
    price_service       =   fields.Float('Price Service',required=True)

    # fields.Float(related='substation.longitude',string='Longitude',readonly=True)
    product_product             =   fields.Many2one(related="service_id.product_product",string="Product")
    address                     =   fields.Text('Address',required=True)

    pic                         =   fields.Char('PIC')
    pic_phone                   =   fields.Char('PIC Phone')
    total_item_service          =   fields.Float('Total')

    state                       =   fields.Selection([(1,'New'),
                                            (2,'PO Start'),
                                            (3,'Survey'),
                                            (4,'OTW Ke Lokasi'),
                                            (5,'Persiapan Installasi'),
                                            (6,'Sedang Dikerjakan T1'),
                                            (7,'Sedang Dikerjakan T2'),
                                            (8,'Selesai Installasi'),
                                            (9,'Testing'),
                                            (10,'Link UP'),
                                            ],'State', default=1,required=True)
    


    #state                      =   fields.Many2one('transhybrid.state.progress.order',string='State')

    state_parent                =   fields.Selection([(1,'Prospect'),
                                            (2,'Deal'),
                                            (3,'In Progress'),
                                            (4,'Monitoring'),
                                            ],'State',related="sale_order_line_id.state_new")

    percentage                  =   fields.Float('Percentage')
    progress_bar                =   fields.Float(related='percentage')
    sale_order_line_service_detail_ids =    fields.One2many('sale.order.line.service.detail.model','sale_order_line_service_id','Sale Order Line Service',required=True)
    

    @api.onchange('item_service_id')
    def onchange_price_service_item(self):

        val = {}

        tmpPriceService = 0

        if(self.item_service_id):
            tmpPriceService = self.item_service_id.price

            val = {
                'price_service' : tmpPriceService
            }


        return {
            'value': val            
        }
            


    @api.onchange('item_service_progress')
    def onchange_progress_task(self):

        val = {}
        tmpPercentage = 0

        if(self.item_service_progress):
            
            for outData in self.item_service_progress:
                tmpPercentage = outData.progress_percentage
            
            val = {
                'percentage':tmpPercentage,
                'progress_bar':tmpPercentage,
            }
            

        return {
            'value': val            
        }



    '''
    @api.onchange('state')
    def onchange_percentage_task(self):

        val = {}

        statePercentageModel = self.env['transhybrid.state.progress.order']
        
        if(self.state.id):
            
            dataStatePercentage = statePercentageModel.search([('id','=',self.state.id)])
            tmpPercentage = 0
            for outData in dataStatePercentage:
                tmpPercentage = outData.percentage

            val = {
                'percentage':tmpPercentage,
                'progress_bar':tmpPercentage,
            }

        return {
            'value': val            
        }
    '''


    @api.multi
    def name_get(self):
        
        res = []
        
        for record in self:
            listName = []

            listName.append(str(record.sale_order_line_id.product_id.name))
            listName.append(" | ")
            listName.append(str(record.service_id.name))
            listName.append(" | PIC : ")
            listName.append(str(record.pic))
            

            res.append((record.id, ''.join(listName)))

        return res

    @api.onchange('state')
    def onchange_percentage_task(self):

        val = {}

        if(self.state):
            
            
            tmpPercentage = 0

            if(self.state==1):
                tmpPercentage = 0

            elif(self.state==2):
                tmpPercentage = 10
            
            elif(self.state==3):
                tmpPercentage = 20
            
            elif(self.state==4):
                tmpPercentage = 25
            
            elif(self.state==5):
                tmpPercentage = 30
            
            elif(self.state==6):
                tmpPercentage = 45
            
            elif(self.state==7):
                tmpPercentage = 60
            
            elif(self.state==8):
                tmpPercentage = 80
            
            elif(self.state==9):
                tmpPercentage = 90
            
            else:
                tmpPercentage = 100

            
            val = {
                'percentage':tmpPercentage,
                'progress_bar':tmpPercentage,
            }
            

        return {
            'value': val            
        }



class TranshybridSaleOrderLineServiceDetailModel(models.Model):
    
    _name = 'sale.order.line.service.detail.model'
    _description = 'Sale Order Line Service Detail Model'
    _order = 'id asc'

    
    sale_order_line_service_id = fields.Many2one('sale.order.line.service.model',ondelete="cascade")
    
    #po_name = fields.Char(related="sale_order_line_service_id.sale_order_line_id.order_id.name_order",string="Po Number")
    #po_order_date               =   fields.Datetime(related="sale_order_line_service_id.sale_order_line_id.order_id.date_order",string="Order Date")
    #rsf_date                    =   fields.Datetime(related="sale_order_line_service_id.sale_order_line_id.order_id.rfs_date",string="RFS Date")

    service_name = fields.Char(related="sale_order_line_service_id.service_id.name")
    item_service_name = fields.Char(related="sale_order_line_service_id.item_service_id.name")
    #company_name  =   fields.Many2one(related="sale_order_line_service_id.sale_order_line_id.order_id.partner_id",string="Customer")
    #progress_bar_percentage = fields.Integer(related="sale_order_line_service_id.progress_bar_percentage",string="Percentage")

    description = fields.Text('Description')
    progress =  fields.Many2one('product.thc.service.detail.progress')
    progress_bar = fields.Integer(related="progress.progress_percentage")
    sale_order_line_serive_image_ids    =   fields.One2many('sale.order.line.service.image.model','sale_order_line_service_detail_id','Sale Order Line Service Image')


    @api.multi
    def name_get(self):
        
        res = []
        
        for record in self:
            listName = []

            listName.append(str(record.service_name))
            listName.append(" - ")
            listName.append(str(record.item_service_name))
            listName.append(" - ")
            listName.append(str(record.company_name.name))

            res.append((record.id, ''.join(listName)))

        return res


class TranshybridSaleOrderLineServiceImageModel(models.Model):

    _name = 'sale.order.line.service.image.model'
    _description = 'Sale Order Line Serive Image Model'
    _order = 'id asc'

    sale_order_line_service_detail_id  =   fields.Many2one('sale.order.line.service.detail.model',ondelete="cascade") 
    name                        =   fields.Char('Name')
    image                       =   fields.Binary('Image',attachment=True)
    filename                    =   fields.Char('Filename')
    address_image_name          =   fields.Char('Address File')
    





















class TranshybridSaleOrderLineImageModel(models.Model):
    
    _name = 'sale.order.line.image.model'
    _description = 'Sale Order Line Image Model'
    _order = 'id asc'

    sale_order_line_id  =   fields.Many2one('sale.order.line',ondelete="cascade")   
    name                =   fields.Char('Name')
    
    upload_date         =   fields.Date('Approved Date',default=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))   
    address             =   fields.Text('Address')

    image               =   fields.Binary('Image',attachment=True)
    filename            =   fields.Char('Filename')
    description         =   fields.Text('Description')
    order_line_service  =   fields.Many2one('sale.order.line.service.model',ondelete="cascade")


