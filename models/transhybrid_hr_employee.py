from odoo import models, fields, api
from odoo import tools, _
from odoo.modules.module import get_module_resource
from odoo.exceptions import ValidationError
from string import capwords
import datetime

class TranshybridHREmployee(models.Model):
    
    _inherit = 'hr.employee'
    _order = 'nik asc'


    nik = fields.Char(string="NIK")
    birthday = fields.Date('Date of Birth')
    place_of_birth = fields.Char('Place of Birth')

    bank_name = fields.Char(string="Nama Bank")
    bank_account_number = fields.Char(string="Nomor Rekening Bank")
    blood_group = fields.Selection([('a', 'A'),('b', 'B'),('o', 'O'),('ab', 'AB')], string="Golongan Darah")


    gender = fields.Selection([('male','Pria'),
        ('female','Wanita'),
        ('other','Lainnya')
        ],string="Jenis Kelamin")

    marital = fields.Selection([('single','Belum Kawin'),
        ('married','Kawin'),
        ('widower','Janda/Duda'),
        ('divorced','Cerai')])

    last_education = fields.Selection([('sd', 'SD'),
                    ('smp', 'SMP'),
                    ('sma', 'SMA'),
                    ('d1d2', 'D1-D2'),
                    ('d3', 'D3'),
                    ('s1', 'S1'),
                    ('s2', 'S2'),
                    ('s3', 'S3')
                ], string="Pendidikan Terakhir")

    religion = fields.Many2one('transhybrid.hr.employee.religion',string="Agama")
    country_id = fields.Many2one('res.country', default=101, string="Kewarganegaraan")

    category = fields.Selection([('karyawan_tetap', "Karyawan Tetap"), 
        ('karyawan_kontrak', "Karyawan Kontrak"),
        ('karyawan_magang', "Karyawan Magang"), 
        ('karyawan_paruh_waktu', "Karyawan Paruh Waktu")
    ], default='karyawan_tetap', string="Kategori")


    category_employee = fields.Many2one('hr.employee.category',string="Kategori Karyawan")

    employee_family_ids = fields.One2many('transhybrid.hr.employee.family', 'empl_id', string="Data Keluarga")
    nomor_kk = fields.Char(string="Nomor Kartu Keluarga")
    nomor_ktp = fields.Char(string="Nomor KTP")

    file_cv = fields.Binary(string='File CV',)
    file_cv_filename = fields.Char("File Name")
    manager_id = fields.Many2one('hr.employee', string="Nama Atasan Langsung", readonly=True, compute='_set_manager_id')

    


    @api.depends('job_id')
    def _set_manager(self):
        for row in self:
            if row.job_id and not row.job_id.top_level:
                manager = self.env['hr.employee'].search([('job_id','=',row.job_id.parent_id.id)])
                if manager:
                    row.parent_id = manager and manager[0] or None
                    man_one_job_id = manager[0].job_id
                    job = self.env['hr.job'].search([('id', '=', man_one_job_id.id)])
                    if job.parent_id:
                        employee = self.env['hr.employee'].search([('job_id', '=', job.parent_id.id)])
                        row.coach_id = employee and employee[0] or None
                    else:
                        row.coach_id = None
                else:
                    row.parent_id = None
                    row.coach_id = None

            else:
                row.parent_id = None
                row.coach_id = None

    @api.model
    def _get_default_job(self):
        job_id = self.env['hr.job'].search([
            ('name', 'like', 'Karyawan'),
            ('company_id', '=', self.env.user.company_id.id)
        ])
        if job_id:
            return job_id.id

    @api.one
    @api.depends('job_id')
    def _set_manager_id(self):
        if self.job_id:
            self.parent_id = self.job_id.manager_id.id

    def del_empl_wizard(self):
        return {
            'name': 'Hapus Departemen',
            'type': 'ir.actions.act_window',
            'res_model': 'transhybrid.hr.employee.delete.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context':{'default_empl_id': self.id}
        }


    @api.multi
    @api.depends('name', 'nik')
    def name_get(self):
        result = []
        for employee in self:
            if employee.nik:
                name = employee.nik + ' ' + employee.name
            else:
                name = employee.name
            result.append((employee.id, name))
        return result

    
    def edit_position(self):
        return {
            'name': 'Edit Posisi',
            'type': 'ir.actions.act_window',
            'res_model': 'transhybrid.hr.employee.dept.job',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context':{'default_employee_id': self.id}
        }

    
    def deactivate(self):
        partner = self.user_id.partner_id
        partner.write({'employee': True})
        return {
            'name': 'Terminasi',
            'type': 'ir.actions.act_window',
            'res_model': 'transhybrid.hr.employee.resign',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context':{'employee_id': self.id}
        }

    
    @api.model
    def _default_image(self):
        image_path = get_module_resource('transhybrid_jakarta', 'static/src/img', 'placeholder.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    
    def to_title(self, value):
        string = value.split(' ')
        new_string = []
        for x in string:
            if x.islower():
                x = capwords(x)
            new_string.append(x)
        new_string = ' '.join(new_string)
        return new_string


    @api.one
    def _contract_expired_date(self):
        date = datetime.date.today() + datetime.timedelta(days=30)
        expired_contract_date = date.strftime("%Y-%m-%d")

        self.one_month_from_now_date = expired_contract_date
    


    @api.model
    def create(self,vals):


        tmpMobilePhone = vals['mobile_phone']
        if(tmpMobilePhone.isdigit()==False):
            raise ValidationError(_('Information :  Mobile phone is not number.'))

        self = self.with_context(client_mode=True)
        self = self.with_context(group_type='client')

        groups = self.env['res.groups'].search([
                ('name', 'like', 'Karyawan'),
            ])


        vals['nik'] = vals['identification_id']
        res = super(TranshybridHREmployee, self).create(vals)
        
        return res


    @api.one
    def get_lower_employee(self, depth = 0):
        depth += 1
        list_employee_ids = []
        for employee_id in self.search([('parent_id','=',self.id)]):
            if len(self.search([('parent_id','=',employee_id.id)])):
                for deep_employee_id in employee_id.get_lower_employee(depth):
                    list_employee_ids.append(deep_employee_id[0])
            else :
                list_employee_ids.append(employee_id.id)
        return list_employee_ids

    @api.one
    def get_clean_lower_employee(self):
        return self.ids + self.get_lower_employee()[0]

    
    def get_child_ids(self):
        list_employee_ids = []
        if self.child_ids:
            for child in self.child_ids:
                list_employee_ids += self.ids
                list_employee_ids += child.get_child_ids()
        else:
            return self.ids
        return list_employee_ids