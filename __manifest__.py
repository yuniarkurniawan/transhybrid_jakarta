{
    'name': "PT. Primedia Armoekadata",
    'version': '1.0',
    'external_dependencies': {'python': ['xlwt']},
    'depends': ['base', 'account','base_iban', 'base_vat', 'web','crm','sale'],
    'author': 'PT. Primedia Armoekadata',
    'category': '-',
    'summary': '-',
    'description': "PT. Primedia Armoekadata",
    "website": "http://www.ekadata.net.id",
    'data': [
        'views/base_view.xml',
        'menu/transhybrid_menu.xml',
        'views/transhybrid_user_view.xml',
        'views/transhybrid_access_right_management_view.xml',
        
        #'views/transhybrid_state_progress_order_view.xml',
        'views/transhybrid_customer_view.xml',
        'views/transhybrid_vendor_view.xml',
        'views/transhybrid_product_catalogue_view.xml',
        'views/transhybrid_product_catalogue_service_view.xml',
        'views/transhybrid_product_catalogue_service_progress_view.xml',
        'views/transhybrid_crm_lead_view.xml',

        'views/purchase_order_line_view.xml',
        'views/purchase_order_line_image_view.xml',
        'views/transhybrid_sale_order_view.xml',
        'views/transhybrid_sale_order_for_vendor_view.xml',

        'views/transhybrid_sale_order_line_view.xml',
        'views/transhybrid_sale_order_line_service_view.xml',
        'views/transhybrid_sale_order_line_service_detail_view.xml',
        #'views/transhybrid_sale_order_line_service_detail_report_view.xml',

        'views/transhybrid_sale_order_line_image_view.xml',
        'views/transhybrid_email_server_configuration_view.xml',
        'views/transhybrid_email_send_to_configuration_view.xml',
        
        #'views/transhybrid_time_token_expired_configuration_view.xml',
        'views/progressbar_view.xml',
        
        'views/transhybrid_sale_order_customer_report_view.xml',
        'views/transhybrid_sale_order_line_service_report_view.xml',
        'views/transhybrid_sale_order_monitoring_view.xml',
        'views/transhybrid_sale_order_line_service_assign_to_report_view.xml',

        'views/transhybrid_berita_acara_lapangan_view.xml',
        'views/transhybrid_survey_news_view.xml',



        #'views/transhybrid_web_map_templates_view.xml',
        #'views/transhybrid_res_config_views.xml',


        #'views/transhybrid_example_pivot_view.xml',
        #'views/transhybrid_sale_order_line_product_report_view.xml',

        #'wizard/transhybrid_purchase_order_excel_tmpl_view.xml',
        #'wizard/transhybrid_purchase_order_excel_wizard_view.xml',


        'data/transhybrid_time_token_expired_data.xml',
        'data/l10n_id_chart_data.xml',
        'data/account.account.template.csv',
        'data/account.chart.template.csv',
        'data/account.account.tag.csv',
        'data/account.tax.template.csv',
        'data/res.country.state.csv',
        'data/account_chart_template_data.yml',
        'data/init-data.xml',

        'report/transhybrid_po_service_item_report_pdf_template_view.xml',
        'report/transhybrid_po_service_item_report_view.xml',


        'security/security.xml',
        
    ],
    

    "qweb": [
        'static/src/xml/*.xml',
    ],
    
    'demo': [
    ],

    'installable': True,
    'application': True,
}

