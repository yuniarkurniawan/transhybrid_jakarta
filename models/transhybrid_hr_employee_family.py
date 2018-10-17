from odoo import models, fields, api

class TranshybridHREmployeeFamily(models.Model):
    
    _name = 'transhybrid.hr.employee.family'

    name            = fields.Char(string="Nama",required=True)
    empl_id         = fields.Many2one('hr.employee',ondelete='cascade')
    f_relationship  = fields.Selection([
                        ('husband', 'Suami'),
                        ('wife', 'Istri'),
                        ('father', 'Ayah'),
                        ('mother', 'Ibu'),
                        ('children', 'Anak'),
                        ('brother', 'Kakak'),
                        ('sister', 'Adik'),
                    ], string="Hubungan")

    f_birth_place   = fields.Char(string="Tempat Lahir")
    f_birth_date    = fields.Date(string="Tanggal Lahir")
    
    f_last_edu      = fields.Selection([('sd', 'SD'),
                        ('smp', 'SMP'),
                        ('sma', 'SMA'),
                        ('d1d2', 'D1-D2'),
                        ('d3', 'D3'),
                        ('s1', 'S1'),
                        ('s2', 'S2'),
                        ('s3', 'S3')
                    ], string="Pendidikan Terakhir")
    
    f_job           = fields.Char(string="Pekerjaan")
    f_phone         = fields.Char(string="No. HP")

    description     =   fields.Text('Family Description')