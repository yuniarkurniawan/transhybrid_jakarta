import cStringIO

from odoo.report.report_sxw import report_sxw
from odoo.api import Environment
from odoo import tools

import logging
_logger = logging.getLogger(__name__)

try:
    import xlwt
except ImportError:
    _logger.debug('Can not import xls writer`.')


class ReportXls(report_sxw):

    column_widths = [] 
    workbook = None
    sheets = []
    current_sheet = None

    def create(self, cr, uid, ids, data, context=None):
        self.env = Environment(cr, uid, context)
        report_obj = self.env['ir.actions.report.xml']
        report = report_obj.search([('report_name', '=', self.name[7:])])
        if report.ids:
            self.title = report.name
            if report.report_type == 'xls':
                return self.create_xlsx_report(ids, data, report)
        # Dec 9, 2017 [Devi Handevi]: Added for ir.actions.report.xml from method returns (not report record)
        else:
            self.title = report.name
            # rml = tools.file_open(self.tmpl, subdir=None).read()
            report_type = data.get('report_type', 'pdf')
            class a(object):
                def __init__(self, *args, **argv):
                    for key, arg in argv.items():
                        setattr(self, key, arg)
            report = a(title=self.title, report_type=report_type, report_rml_content=None, name=self.title, attachment=False, header=self.header)
            return self.create_xlsx_report(ids, data, report)
        return super(ReportXls, self).create(cr, uid, ids, data, context)

    def header_style(self):
        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        border = xlwt.Borders()
        border.left = 1
        border.top = 1
        border.bottom = 1
        border.right = 1
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER
        alignment.wrap = 1
        style.font = font
        style.borders = border
        style.alignment = alignment
        return style

    def plain_border_style(self):
        style = xlwt.XFStyle()
        border = xlwt.Borders()
        border.left = 1
        border.top = 1
        border.bottom = 1
        border.right = 1
        style.borders = border
        return style

    def title_style(self):
        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.height = 18 * 20
        font.bold = True
        style.font = font
        return style

    def monetary_style(self, decimal_after_dot=0, with_borders=False):
        decimal = ""
        for i in range(0,decimal_after_dot):
            decimal += "0"
        style = xlwt.XFStyle()
        if (decimal):
            style.num_format_str = "#,###.%s" % decimal
        else:
            style.num_format_str = "#,###"
        if with_borders:
            border = xlwt.Borders()
            border.left = 1
            border.top = 1
            border.bottom = 1
            border.right = 1
            style.borders = border
        return style

    def write_row(self, row_data, styles=None):
        col = 0
        for row_datum in row_data:
            if row_datum == None:
                # menambah border di merge shell
                self.current_sheet.write(self.row, col, '', xlwt.Style.easyxf('borders: top 1, right 1, bottom 1, left 1'))
                col += 1
                continue
            if styles == None: 
                cell_style = None
            elif isinstance(styles, list):
                try:
                    cell_style = styles[col]
                    if isinstance(cell_style, (str,unicode)):
                        cell_style = xlwt.Style.easyxf(cell_style)
                except IndexError:
                    cell_style = None
            elif isinstance(styles, (str,unicode)):
                cell_style = xlwt.Style.easyxf(styles)
            else:
                cell_style = styles
            if cell_style != None:
                self.current_sheet.write(self.row, col, row_datum, cell_style)
            else:
                self.current_sheet.write(self.row, col, row_datum)
            col += 1
        self.row += 1
    
    def adjust_column_widths(self):
        if len(self.column_widths) == 0: return
        sheet_idx = 0
        for col_widths in self.column_widths:
            try:
                sheet = self.sheets[sheet_idx]
            except IndexError:
                continue
            col_idx = 0
            for width in col_widths:
                sheet.col(col_idx).width = 256 * width
                col_idx += 1
            sheet_idx += 1

    def create_xlsx_report(self, ids, data, report):
        self.parser_instance = self.parser(
            self.env.cr, self.env.uid, self.name2, self.env.context)
        objs = self.getObjects(
            self.env.cr, self.env.uid, ids, self.env.context)
        self.parser_instance.set_context(objs, data, ids, 'xls')
        file_data = cStringIO.StringIO()
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.sheets = []
        self.current_sheet = None
        self.generate_xls_report(data, objs)
        self.adjust_column_widths()
        n = cStringIO.StringIO()
        self.workbook.save(n)
        n.seek(0)
        return (n.read(), 'xls')

    def generate_xls_report(self, workbook, data, objs):
        raise NotImplementedError()
