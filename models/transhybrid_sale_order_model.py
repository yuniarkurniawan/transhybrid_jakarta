from odoo import models, fields, api,  _
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, date, timedelta
import re
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time
import dateutil.parser
import os

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

import email
import email.encoders
import smtplib


API_KEY = "AIzaSyB22AKzqTK5SNaVcKasEyrtXhMLiGn5UUM"

class TranshybridSaleOrderModel(models.Model):

    _name     = "sale.order"
    _inherit  = "sale.order"

    name_order          =   fields.Char('Sale Order Name')

    
    assign_to_choise    =   fields.Selection([
                                    (1,'Internal'),
                                    (2,'Vendor')],'Assign To',default=1)
    

    vendor_name_order   =   fields.Char('Vendor PO Number')
    
    
    vendor_assign_order =   fields.Many2one('res.partner',domain=[('supplier', '=', 1)])
    assign_to_by_vendor =   fields.Many2one('res.users',string='Assign To')
    

    #user_company        =   fields.Integer(related='assign_to_by_vendor.user_company')
    
    
    is_manager_other_company = fields.Selection([
                                    (1,'Yes'),
                                    (2,'No')],'Is Manager',related="assign_to_by_vendor.is_manager_other_company")
    
    
    
    assign_to           =   fields.Many2one('res.users',string='Assign To')
    

    state_new           =   fields.Selection([(1,'Prospect'),
                                            (2,'Deal'),
                                            (3,'In Progress'),
                                            (4,'Closing'),
                                            (5,'Cancel'),
                                            ],'State', default=1)

    rfs_date            =   fields.Datetime('RFS Date',default=fields.Datetime.now)
    

    deal_date           =   fields.Date('Deal Date')
    in_progres_date     =   fields.Date('Progress Date')
    monitoring_date     =   fields.Datetime('Monitoring Date')

    percentage_task     =   fields.Float('Progress',compute='_compute_total_progress')
    spelled_out         =   fields.Text('Spelled Out',compute='_compute_spelled_out')
    long_days_work_order  = fields.Char('Work Order Days')

    _sql_constraints = [('po_number_unique', 'unique(name_order)', 'Purchase Order Name Can Not Be Same.')]



    def calculate_working_days(self,paramDateAwal,paramDateAkhir):

        listOut = []

        dateSatu = dateutil.parser.parse(paramDateAwal)
        dateDua = dateutil.parser.parse(paramDateAkhir)

        akhir = dateDua - dateSatu
        days, hours, minutes = akhir.days, akhir.seconds // 3600, akhir.seconds // 60 % 60

        listing = []
        if(days!=0):
            
            if(days>=1):
                listing.append(str(days))
                listing.append(" days / ")
            

        if(hours!=0):
            listing.append(str(hours))
            if(hours>1):
                listing.append(" hours ")
            else:
                listing.append(" hour ")

        if(minutes!=0):
            listing.append(str(minutes))
            listing.append(" minutes")

        return ''.join(listing)


    def push_pyfcm_multi(self, to_regids, message_title, message_body, data=False):
        
        push_service = FCMNotification(api_key=API_KEY)
        result = push_service.notify_multiple_devices(registration_ids=to_regids, 
        message_title=message_title,
        message_body=message_body)


    @api.model
    def get_deadline_purchase_order(self):

        saleOrderModel = self.env['sale.order']
        poolData = saleOrderModel.search([('state_new','in',(2,3))])
        transhybridPurchaseOrderNotificationModel = self.env['transhybrid.purchase.order.notification']

        for outData in poolData:

            now = datetime.now()
            piss = datetime.strftime(now,'%Y-%m-%d %H:%M:%S')

            order_date = dateutil.parser.parse(outData.date_order)
            rfsDate = dateutil.parser.parse(outData.rfs_date)
            hariIni = dateutil.parser.parse(datetime.strftime(now,'%Y-%m-%d %H:%M:%S')) 
            
            akhir = rfsDate - hariIni 
            days = akhir.days
            
            print "Days : ", days
            if(days<=3):

                descriptionDays = ""
                if(days<0):
                    descriptionDays = "more than " + str(days * (-1)) + " days"
                elif(days==1):
                    descriptionDays = str(days) + " day left"
                else:
                    descriptionDays = str(days) + " days left"
                

                listDescription = []

                listDescription.append("Purchase Order Of ")
                listDescription.append(str(outData.name))
                listDescription.append(" Is Now Deadline")

                valueNotification = {
                    'name'          : outData.name, 
                    'order_date'    : outData.date_order,
                    'customer_name' : outData.partner_id.name,
                    'duration'      : descriptionDays,
                    'rfs_date'      : outData.rfs_date,
                    'amount_total'  : outData.amount_total,
                    'description'   : ''.join(listDescription), 
                }

                transhybridPurchaseOrderNotificationModel.create(valueNotification)

                
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


    @api.onchange('vendor_assign_order')
    def get_vendor_pic(self):

        listUserUnderPic = []
        resUserModel = self.env['res.users']

        if(self.vendor_assign_order):

            dataUserPic = resUserModel.search([('user_condition','=',2),('user_company','=',self.vendor_assign_order.id),('is_manager_other_company','=',1)])
            for dataUser in dataUserPic:
                listUserUnderPic.append(dataUser.id)

        return {'domain': {'assign_to_by_vendor': [('id', 'in', listUserUnderPic)]}}


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
        


    def get_email_server_configuration(self):

        listEmailConfiguration = []
        configurationModel = self.env['transhybrid.configuration']
        configurationPool = configurationModel.search([('is_email_server_configuration','=',True)])

        if(configurationPool):
            for outData in configurationPool:

                new_dict={}
                new_dict['email_host'] = outData.email_host
                new_dict['email_port'] = outData.email_port
                new_dict['email_sender'] = outData.email_sender

                new_dict['email_password'] = outData.email_password
                listEmailConfiguration.append(new_dict)

        return listEmailConfiguration


    def get_email_send_to_configuration(self):

        listEmailConfiguration = []
        configurationModel = self.env['transhybrid.configuration']
        configurationPool = configurationModel.search([('is_email_send_to','=',True)])

        if(configurationPool):
            for outData in configurationPool:

                new_dict={}
                new_dict['email_send_to'] = outData.email_send_to
                
                listEmailConfiguration.append(new_dict)

        return listEmailConfiguration


    @api.multi
    def action_deal(self):

        kondisi = False
        listServiceItem = []
        if(self.id):
            
            
            self.write({
                'state_new':2,
                'deal_date':date.today().strftime('%Y-%m-%d')
            })
            
            
            number = 1
            for outData in self.order_line:
                outData.state_new = 2

                for outDataService in outData.sale_order_line_service_ids:
                    if(outDataService.service_id.need_email_notif==2):

                        kondisi = True
                        listServiceItem.append("")
                        listServiceItem.append(str(number) +". ")
                        listServiceItem.append(str(outDataService.service_id.name))
                        listServiceItem.append("\n")
                        
                        listServiceItem.append("    ")
                        listServiceItem.append("Item ")
                        listServiceItem.append(str(outDataService.item_service_id.name))
                        listServiceItem.append("\n")

                        listServiceItem.append("    ")
                        listServiceItem.append("Worker ")
                        listServiceItem.append(str(outDataService.assign_to.name))
                        listServiceItem.append("\n")

                        listServiceItem.append("    ")
                        listServiceItem.append("Customer PIC ")
                        listServiceItem.append(str(outDataService.pic))
                        listServiceItem.append("\n")

                        listServiceItem.append("    ")
                        listServiceItem.append("Customer PIC Address ")
                        listServiceItem.append(str(outDataService.address))
                        listServiceItem.append("\n")

                        listServiceItem.append("    ")
                        listServiceItem.append("Rp. ")
                        listServiceItem.append(str(outDataService.price_service))
                        listServiceItem.append("\n")
                        listServiceItem.append("\n")

                        number+=1



                    
        
        if(kondisi):

            tmpHostEmail = ""
            tmpPortEmail = ""
            tmpPengirimEmail = ""

            tmpPasswordEmail = ""
            listEmailconfiguration = []
            listEmailconfiguration = self.get_email_server_configuration()
            
            if(len(listEmailconfiguration)<=0):
                raise ValidationError(_('Information :  You Have Not Set Email Sender Configuration.'))
            else:

                for outDataEmail in listEmailconfiguration:
                    tmpHostEmail = outDataEmail['email_host']
                    tmpPortEmail = outDataEmail['email_port']
                    tmpPengirimEmail = outDataEmail['email_sender']
                    tmpPasswordEmail = outDataEmail['email_password']

                if(tmpHostEmail==False or tmpPortEmail==False or tmpPengirimEmail==False or tmpPasswordEmail==False):
                    raise ValidationError(_('Information :  You Have Not Set Email Sender Configuration.'))



            tmpSendTo = ""
            listEmailSendToConfiguration = []
            listEmailSendToConfiguration = self.get_email_send_to_configuration()
            if(len(listEmailSendToConfiguration)<=0):
                raise ValidationError(_('Information :  You Have Not Set Email Sender Configuration.'))
            else:
                for outDataEmailSendTo in listEmailSendToConfiguration:
                    tmpSendTo = outDataEmailSendTo['email_send_to']

                if(tmpSendTo==False):
                    raise ValidationError(_('Information :  You Have Not Set Email Sender Configuration.'))



            listBodyEmail = []
                        
            listBodyEmail.append(str(self.partner_id.customer_code))
            listBodyEmail.append(" - ")
            listBodyEmail.append(str(self.partner_id.name))
            listBodyEmail.append("\n")

            listBodyEmail.append("Order Date ")
            listBodyEmail.append(self.date_order)
            listBodyEmail.append("\n")

            listBodyEmail.append("RFS Date ")
            listBodyEmail.append(self.rfs_date)
            listBodyEmail.append("\n")
            listBodyEmail.append("\n")

            listBodyEmail.append("Detail Services")
            listBodyEmail.append("\n")

            listBodyEmail.append(str(''.join(listServiceItem)))
            listBodyEmail.append("\n\n")
            listBodyEmail.append("Best Regards,")

            listBodyEmail.append("\n\n\n")
            listBodyEmail.append("THC Administrator")


            #tmpMessageEmail = "TEST AHH\nLAGIIII"
            tmpMessageEmail = ''.join(listBodyEmail)

            msg = MIMEMultipart()
            msg['From'] = tmpPengirimEmail
            msg['To'] = ''.join(tmpSendTo)
            msg['Date'] = email.Utils.formatdate(localtime=True)
            msg['Subject'] = "Notification Manage CPE " + self.name
            msg.attach(MIMEText(tmpMessageEmail))

            try:
                server = smtplib.SMTP_SSL(tmpHostEmail, int(tmpPortEmail))
                server.ehlo()
                server.login(tmpPengirimEmail, tmpPasswordEmail)

                server.sendmail(tmpPengirimEmail, tmpSendTo, msg.as_string())
                server.quit()

            except (smtplib.SMTPException), e:
                raise ValidationError(_('Information :  Email Is Failed To Be Sent'))


        


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


    def get_address_base_progress_image(self):
        
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        path = path.split('/')
        panjang = len(path)

        listAddres = []
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        
        listAddres.append(str(base_url))
        listAddres.append("/")
        listAddres.append(str(path[panjang-2]))
        listAddres.append("/static/upload_progress_image/")

        return ''.join(listAddres)


    def get_base_path_image_data(self):

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        path = path.split('/')
        panjang = len(path)


        listAddres = []     
        for out in path:
    
            if(str(out) == path[-1]):
                break

            listAddres.append(str(out))
            listAddres.append("/")


        listAddres.append("static/upload_progress_image/")

        return ''.join(listAddres)



    @api.multi
    def action_monitoring(self):

        if(self.id):

            tmpWorkingDays = self.calculate_working_days(self.date_order,date.today().strftime('%Y-%m-%d'))
            tmpBaseDirImage = self.get_base_path_image_data()

            
            self.write({
                'state_new':4,
                'monitoring_date':date.today().strftime('%Y-%m-%d'),
                'long_days_work_order': tmpWorkingDays,
            })
            

            for outData in self.order_line:
                outData.state_new = 4
                
                for outDataInOne in outData.sale_order_line_service_ids:
                    for outDataInTwo in outDataInOne.sale_order_line_service_detail_ids:
                        for outDataInThree in outDataInTwo.sale_order_line_serive_image_ids:
                            tmpBaseDirImage = tmpBaseDirImage + str(outDataInThree.address_image_name)
                                                        
                            try:
                                os.remove(tmpBaseDirImage)
                            except:
                                pass
                            
                            



class TranshybridSaleOrderLineModel(models.Model):
    
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'


    @api.model
    def _get_default_partner(self):

        vendor = self.env.context.get('vendor')
        return vendor
        

    state_new   =   fields.Selection([(1,'Prospect'),
                                            (2,'Deal'),
                                            (3,'In Progress'),
                                            (4,'Monitoring'),
                                            ],'State', default=1)

    po_order_date                   =   fields.Datetime(related="order_id.date_order",string="Order Date")
    po_default_vendor               =   fields.Many2one("res.partner", default=lambda self: self._get_default_partner(),string="Default Partner")
    po_rfs_date                     =   fields.Datetime(related="order_id.rfs_date",string="Order Date")
    po_customer_name                =   fields.Many2one(related="order_id.partner_id",string="Customer Name")

    po_state                    =     fields.Selection([('draft','Quotation'),
                                            ('sent','Quotation Sent'),
                                            ('sale','Sales Order'),
                                            ('done','Locked'),
                                            ('cancel','Cancelled')
                                            ],'State',related="order_id.state")

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
                        'pic_phone':outData.pic_phone,

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

                vendor = self.env.context.get('vendor')
                tmpChoise = 1
                if(vendor):
                    tmpChoise = 2

                index = 1
                while(index<=self.total_service):

                    listDetailServicePickup.append((0,0,{
                            'service_id' : self.service_id.id,
                            'assign_to_choise':tmpChoise,
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



    @api.model
    def _get_default_choise(self):

        vendor = self.env.context.get('vendor')
        
        if(vendor):
            return 2
        else:
            return 1


    @api.model
    def _get_filter_user(self):

        vendor = self.env.context.get('vendor') 
        listUserUnderPic = []
        resUserModel = self.env['res.users']

        if(vendor):

            dataUserPic = resUserModel.search([('user_condition','=',2),('user_company','=',vendor),('is_manager_other_company','=',2)])
            for dataUser in dataUserPic:
                listUserUnderPic.append(dataUser.id)
            
        else:
            
            dataUserPic = resUserModel.search([('user_condition','=',1)])
            for dataUser in dataUserPic:
                listUserUnderPic.append(dataUser.id)

                    
        return [
            ('id','in',listUserUnderPic)
        ]


    sale_order_line_id          =   fields.Many2one('sale.order.line','Sale Order Line',ondelete='cascade',required=True)
    product_order_line          =   fields.Many2one(related="sale_order_line_id.product_id",string="Product")


    service_id                  =   fields.Many2one('product.thc.service',required=True)
    item_service_id             =   fields.Many2one('product.thc.service.detail',required=True)
    item_service_progress       =   fields.Many2one('product.thc.service.detail.progress')

    progress_bar_percentage     =   fields.Integer(related='item_service_progress.progress_percentage',string="Progress")

    po_id                       =   fields.Integer(related="sale_order_line_id.order_id.id",store=True)
    po_name                     =   fields.Char(related="sale_order_line_id.order_id.name_order",string="Po Number",store=True)
    
    company_name                =   fields.Many2one(related="sale_order_line_id.order_id.partner_id",string="Customer")
    company_address             =   fields.Char(related="company_name.street")
    company_phone               =   fields.Char(related="company_name.phone")
    company_fax                 =   fields.Char(related="company_name.fax")

    po_order_date               =   fields.Datetime(related="sale_order_line_id.order_id.date_order",string="Order Date")
    rsf_date                    =   fields.Datetime(related="sale_order_line_id.order_id.rfs_date",string="RFS Date")
    
    po_state                    =     fields.Selection([('draft','Quotation'),
                                            ('sent','Quotation Sent'),
                                            ('sale','Sales Order'),
                                            ('done','Locked'),
                                            ('cancel','Cancelled')
                                            ],'State',related="sale_order_line_id.order_id.state")


    assign_to_choise    =   fields.Selection([
                                    (1,'Internal'),
                                    (2,'Vendor')],'Assign To',
                                    domain=_get_default_choise)


    is_customer_sign    =   fields.Selection([
                                    (1,'Not Signed'),
                                    (2,'Signed'),                                    
                                    ],'Signature',default=1)


    longitude               =   fields.Float('Longitude',digits=(0,6),required=True,default=0.0)
    latitude                =   fields.Float('Latitude',digits=(0,6),required=True,default=0.0)
    long_lat_address        =   fields.Text('Signature Address')
    google_map              =   fields.Char(string="Map")

    assign_to           =   fields.Many2one('res.users',string='Assign To',
                                domain=_get_filter_user,required=True)


    assign_to_phone     =   fields.Char(related="assign_to.user_phone",string="User Phone")

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
                                            (4,'Closing'),
                                            ],'State',related="sale_order_line_id.state_new")

    percentage                  =   fields.Float('Percentage')
    progress_bar                =   fields.Float(related='percentage')
    sale_order_line_service_detail_ids =    fields.One2many('sale.order.line.service.detail.model','sale_order_line_service_id','Sale Order Line Service',required=True)
    
    is_balap                    =   fields.Selection([(1,'Belum Dibuat'),
                                            (2,'Sudah Dibuat'),
                                            ],'State',default=1)

    is_bas                      =   fields.Selection([(1,'Belum Dibuat'),
                                            (2,'Sudah Dibuat'),
                                            ],'State',default=1)


    is_baa                      =   fields.Selection([(1,'Belum Dibuat'),
                                            (2,'Sudah Dibuat'),
                                            ],'State',default=1)



    is_bat                      =   fields.Selection([(1,'Belum Dibuat'),
                                            (2,'Sudah Dibuat'),
                                            ],'State',default=1)


    is_bai                      =   fields.Selection([(1,'Belum Dibuat'),
                                            (2,'Sudah Dibuat'),
                                            ],'State',default=1)



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

            #listName.append(str(record.sale_order_line_id.product_id.name))
            #listName.append(" | ")
            listName.append(str(record.service_id.name))
            listName.append(" | ")
            listName.append(str(record.item_service_id.name))
            #listName.append(" | PIC : ")
            #listName.append(str(record.pic))
            

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
    upload_date = fields.Date('Upload Date')
    
    #po_name = fields.Char(related="sale_order_line_service_id.sale_order_line_id.order_id.name_order",string="Po Number")
    #po_order_date               =   fields.Datetime(related="sale_order_line_service_id.sale_order_line_id.order_id.date_order",string="Order Date")
    #rsf_date                    =   fields.Datetime(related="sale_order_line_service_id.sale_order_line_id.order_id.rfs_date",string="RFS Date")

    upload_id    = fields.Char('Upload Random Id')
    service_name = fields.Char(related="sale_order_line_service_id.service_id.name")
    item_service_name = fields.Char(related="sale_order_line_service_id.item_service_id.name")
    company_name  =   fields.Many2one(related="sale_order_line_service_id.sale_order_line_id.order_id.partner_id",string="Customer")
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


