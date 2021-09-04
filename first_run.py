#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 21:16:46 2021

@author: zseebrz
"""
from sqlitedict import SqliteDict
import os


# Create persistent storage of config variables and semaphors if it doesn't yet exists
def InitializeConfig():
    if not os.path.exists('./config/'):
        os.makedirs('./config/')
    if not os.path.exists('./config/config_db.sqlite'):
        config_dict = SqliteDict('./config/config_db.sqlite', autocommit=True)
        
        config_dict['UPLOAD_DIRECTORY'] = "./uploads"
        
        config_dict['SUBDELEGATION_UPLOAD_DIRECTORY'] = "./uploads/subdelegations"
        config_dict['DW_UPLOAD_DIRECTORY'] = "./uploads/dw"
        config_dict['CFF_EXCEL_UPLOAD_DIRECTORY'] = "./uploads/cff_excel"
        config_dict['CFF_PDF_UPLOAD_DIRECTORY'] = "./uploads/cff_pdf"
        config_dict['SAP_UPLOAD_DIRECTORY'] = "./uploads/sap"
        
        config_dict['CFF_DATE_TABLE'] = './processed/cff_pdf_dates.xlsx'
        
        config_dict['UPLOAD_FOLDERS'] = [config_dict['SUBDELEGATION_UPLOAD_DIRECTORY'], config_dict['DW_UPLOAD_DIRECTORY'], 
                          config_dict['CFF_EXCEL_UPLOAD_DIRECTORY'], config_dict['CFF_PDF_UPLOAD_DIRECTORY'],
                          config_dict['SAP_UPLOAD_DIRECTORY']]
        
        config_dict['SUBDELEGATION_FILE'] = './processed/df_subdelegation.xlsx'
        config_dict['SAP_FILE'] = './processed/df_SAP.xlsx'
        #config_dict['TOR_extract'] = 'df_TOR_statement_extract_2020_new_w_textract.xlsx'
        config_dict['RO_extract'] = './uploads/dw/RO_2020_w_txt_fields.xlsx'
        config_dict['CFF_FILE'] = 'df_all_calls_2020_working_days.xlsx'
        config_dict['RESULT_FILE'] = 'GNI_VAT_check_results_july_formatted_2021_web.xlsx'
        
        config_dict['CHECKS_LOCK_FILE'] = './lockfiles/check_lock.txt'
        config_dict['PREPROCESS_LOCK_FILE'] = './lockfiles/preprocess_lock.txt'
        config_dict['CFF_DATES_LOCK_FILE'] = './lockfiles/cff_dates_lock.txt'
        config_dict['UPLOADS_LOCK_FILE'] = './lockfiles/uploads_lock.txt'
        
        config_dict['LOCKFILES'] = [config_dict['PREPROCESS_LOCK_FILE'], config_dict['CFF_DATES_LOCK_FILE'], 
        				config_dict['UPLOADS_LOCK_FILE']]
        config_dict['LOCKFILE_DIRECTORY'] = './lockfiles/'
        
        
        config_dict['CFF_DATE_TABLE'] = './processed/cff_pdf_dates.xlsx'
        config_dict['CFF_PDF_FOLDER'] = './uploads/cff_pdf/'
        config_dict['CFF_XLSX_FOLDER'] = './uploads/cff_excel/'
        
        config_dict['UPLOAD_DIRECTORY'] = "./uploads"
        
        config_dict['SUBDELEGATION_UPLOAD_DIRECTORY'] = "./uploads/subdelegations"
        config_dict['DW_UPLOAD_DIRECTORY'] = "./uploads/dw"
        config_dict['CFF_EXCEL_UPLOAD_DIRECTORY'] = "./uploads/cff_excel"
        config_dict['CFF_PDF_UPLOAD_DIRECTORY'] = "./uploads/cff_pdf"
        config_dict['SAP_UPLOAD_DIRECTORY'] = "./uploads/sap"
        
        config_dict['CFF_DATE_TABLE'] = './cff_dates/cff_pdf_dates.xlsx'
        
        config_dict['PROCESSED_DIRECTORY'] = "./processed"
        config_dict['RESULT_DIRECTORY'] = "./results"
        
        config_dict['PREPROCESS_FOLDERS'] = [config_dict['PROCESSED_DIRECTORY'], config_dict['RESULT_DIRECTORY']]
        
        config_dict['RESULTS_FOLDER'] = './results/'
        config_dict['UPLOADS_DW_FOLDER'] = './uploads/dw/'
        
        config_dict['VERIFIED_DATE_EXCEL_FILE'] = 'cff_pdf_dates.xlsx'
        config_dict['OUTPUT_EXCEL_FILE'] = 'df_all_calls_2020_working_days.xlsx'
        
        config_dict['SUBDELEGATION_FILE'] = './processed/df_subdelegation.xlsx'
        config_dict['SAP_FILE'] = './processed/df_SAP.xlsx'
        #config_dict['TOR_extract'] = 'df_TOR_statement_extract_2020_new_w_textract.xlsx'
        config_dict['RO_extract'] = './uploads/dw/RO_2020_w_txt_fields.xlsx'
        config_dict['CFF_FILE'] = './processed/cff_data.xlsx'
        config_dict['RESULT_FILE'] = './results/GNI_VAT_check_results_july_formatted_2021_web.xlsx'
        
        config_dict['upload_lock'] = False
        config_dict['cff_date_lock'] = False
        config_dict['preprocessing_lock'] = False
        
        config_dict['checks_lock'] = False
        config_dict['date_of_last_checks'] = None
        
        config_dict['first_check_run'] = False
        config_dict['checks_first_display'] = False
        
        config_dict['checks_progress_state'] = 0
        config_dict['preprocessing_progress_state'] = 0
        
        config_dict['status_message'] = ""
        config_dict['preprocessing_status_message'] = ""
        
        config_dict['preprocessing_tab'] = 'date_verify'
        
        config_dict['last_checks_datetime'] = ''
        
        config_dict['last_zipfile_name'] = ''
        
        #for key, value in config_dict.iteritems():
        #    print(key, value)
        config_dict.close()