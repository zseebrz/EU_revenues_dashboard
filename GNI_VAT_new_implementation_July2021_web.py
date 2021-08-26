#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 15:25:17 2021

@author: zseebrz
"""

#needs the py36 environment to run (because of pdfminer)
import pandas as pd
#import numpy as np
#import math
#import re
import datetime

from audit_revenues_2021_july_website import query_ECB_forex_API, query_ECB_forex_API_exact_date#, subdelegation_check
from audit_revenues_2021_july_website import SAP_accounts, budget_lines#, months, eurozone_countries, all_currencies, non_eurozone_currencies
#from audit_revenues_2020_basic import ECB_penultimate_working_day_of_month, query_ECB_forex_API_exact_date, get_Ares_date
#from audit_revenues_2020_basic import ECB_first_working_day_after_19th_of_month
#from audit_revenues_2021_july_website import ECB_working_days_between_dates
from audit_revenues_2021_july_website import add_Excel_formattting, VAT_GNI_sections, VAT_GNI_conditionals
#from price_parser import Price
#from audit_revenues_2020_basic import sent_tokenize

#from operator import concat
from audit_revenues_2021_july_website import rename_dupes_with_number, make_hyperlink, GetWorkFlowData

import time
from sqlitedict import SqliteDict
config_dict = SqliteDict('./config/config_db.sqlite', autocommit=True)

SUBDELEGATION_FILE = config_dict['SUBDELEGATION_FILE']
SAP_FILE = config_dict['SAP_FILE']
#TOR_extract = 'df_TOR_statement_extract_2020_new_w_textract.xlsx'
RO_extract = config_dict['RO_extract']
CFF_FILE = config_dict['CFF_FILE']
RESULT_FILE = config_dict['RESULT_FILE']

#TODO: implement regular saving of the state of checks into the persistent storage

def run_checks():
        #----------------------------
        #load all the required files
        config_dict['checks_progress_state'] = 5
        config_dict['status_message'] = 'Merging and joining data tables'
        
        
        df_subdelegation = pd.read_excel(SUBDELEGATION_FILE, index_col=0)
        
        df_SAP = pd.read_excel(SAP_FILE)
        
        df_SAP.loc[df_SAP.Account == 70601300, 'transaction_type'] = "GNI"
        df_SAP.loc[df_SAP.Account == 70601400, 'transaction_type'] = "VAT"
        
        #need to multiply by minus one to match the Call for Funds and RO
        df_SAP['Amount in local currency'] = df_SAP['Amount in local currency'] * -1
        df_SAP['Amount in doc. curr.'] = df_SAP['Amount in doc. curr.'] * -1
        
        #the Vendor field is not always present in the SAP report, but we don't need it in any case
        try:
            df_SAP.drop(columns=['Vendor'], inplace=True)
        except:
            pass    
        
        
        df_SAP.columns = (['Account', 'Company Code', 'Document Number', 'Document Type',
        'Doc. Date', 'Posting Date', 'Value Date', 'Posting Key',
        'Amount in local cur.', 'Amount in doc. curr.', 'Local Currency',
        'Profit Center', 'Text', 'Offsett.account type',
        'Offsetting acct no.', 'transaction_type'])
        
        #loading the RO ABAC export and merging the sheets
        df_recovery_extract_positions = pd.read_excel(RO_extract, sheet_name='RO Positions')
        df_recovery_extract_headers = pd.read_excel(RO_extract, sheet_name='RO Headers')
        df_recovery_extract_workflow = pd.read_excel(RO_extract, sheet_name='RO Workflows')
        
        
        df_recovery_extract_GNI_positions = df_recovery_extract_positions[ df_recovery_extract_positions['RO SubNature of Recovery Desc']=='REVENUES GNI' ]
        
        df_recovery_extract_VAT_positions = df_recovery_extract_positions[ df_recovery_extract_positions['RO SubNature of Recovery Desc']=='REVENUES VAT' ]
        
        df_recovery_extract_VAT_GNI_positions = df_recovery_extract_GNI_positions.append(df_recovery_extract_VAT_positions)
        
        
        df_recovery_extract_VAT_GNI_positions = df_recovery_extract_VAT_GNI_positions[['RO Local Key', 'RO Position Local Key', 'Central Appropriation Key',
               'GL Account Id', 'GL Account Short Desc',
               'RO SubNature of Recovery Desc',
               'RO Carried Forward Amount (Cur)', 'RO Carried Forward Amount (Eur)',
               'RO Cashed Amount (Eur)', 'RO Cashed Payment Amount (Eur)',
               'RO Initial Accepted Amount (Eur)',
               'RO Open Amount (Eur)', 'RO Year Init Accepted Amt (Eur)',
               'RO Year Init Accepted Amt (Cur)']].merge(df_recovery_extract_headers[['RO Local Key',
                                                                                      'LE Country Code',
                                                                                      'RO Due Date',
                                                                                      'RO Document Date',
                                                                                      'RO Cashing Cashed Date',
                                                                                      'RO Carried Forward Amount (Cur)',
                                                                                      'RO Carried Forward Amount (Eur)',
                                                                                      'RO Cashed Amount (Eur)',
                                                                                      'RO Cashed Payment Amount (Eur)',
                                                                                      'RO Initial Accepted Amount (Eur)',
                                                                                      'RO Open Amount (Eur)',
                                                                                      'RO Year Init Accepted Amt (Cur)',
                                                                                      'RO Year Init Accepted Amt (Eur)',
                                                                                      'RO Justification', 
                                                                                      'RO Contract or File nr']], on='RO Local Key', suffixes=('_pos', '_hdr'))
        
        
                                                                                     
        #we try to mark the duplicates instead of just dropping them
        
        temp = df_recovery_extract_VAT_GNI_positions.copy()
        temp['RO Position Local Key'] = rename_dupes_with_number(temp, 'RO Position Local Key')                                                              
        #now let's join the whole thing together, documents with the RO position data
        #so all stuff will be in the same row as the filename and content, so positions
        #will be duplicated, but it is easier to process this way, it will disaggregated at the end
        if len(temp) > len(df_recovery_extract_VAT_GNI_positions):
            df_full = temp
        else:
            df_full = df_recovery_extract_VAT_GNI_positions 
            
        #preparing for merge, first 50 chars of the contract number field, and euro amount, as SAP bookings are in EUR
        df_SAP['SAP_merge'] = df_SAP['Text'].apply(lambda x: str(x)[:49]).astype(str)
        df_full['SAP_merge'] = df_full['RO Contract or File nr'].apply(lambda x: str(x)[:49]).astype(str)
        df_full['transaction_type'] =  df_full['RO SubNature of Recovery Desc'].apply(lambda x: str(x)[-3:]).astype(str)
        df_full[ 'Amount in local cur.'] =  df_full['RO Cashed Amount (Eur)_pos']
        
        #only reset index if we want to check for duplicates easily
        #df_full.reset_index(inplace=True)
        #df_full_with_SAP = df_full.merge(df_SAP, how='left', on=['transaction_type','SAP_merge', 'Amount in local cur.'], suffixes=('_RO','_SAP'))
        #no left join/merge, because the SAP report may contain extra rows from previous and next years, as is the case for 2020
        #somehow Giovanni's reports have SAP transactions referring to the 2021 January CFF
        
        df_full_with_SAP = df_full.merge(df_SAP, on=['transaction_type','SAP_merge', 'Amount in local cur.'], suffixes=('_RO','_SAP'))
        
        config_dict['checks_progress_state'] = 15
        config_dict['status_message'] = 'Filtering and re-arranging data'
        
        
  
        #now we have all the RO data and the SAP merged together for GNI and VAT
        
        #get the workflow data
        df_workflow = GetWorkFlowData(df=df_full_with_SAP, df_recovery_extract_workflow=df_recovery_extract_workflow, df_subdelegation=df_subdelegation)
        
        df_check = df_full_with_SAP.join(df_workflow)
        
        process_mining_df = df_recovery_extract_workflow.groupby(['RO Local Key']).count()
        process_mining_df = process_mining_df.reset_index()
        process_mining_df = process_mining_df[['RO Local Key', 'Workflow Action Code']]
        process_mining_df.columns = ['RO Local Key', 'Workflow actions']
        process_mining_df['Avg workflow actions'] =  process_mining_df['Workflow actions'].mean().astype(int)
        
        df_check = df_check.merge(process_mining_df, how='left', on='RO Local Key')
        
        #calculating and adding the country average amounts
        country_means = df_full.groupby(['LE Country Code']).mean()['RO Cashed Amount (Eur)_hdr'].reset_index()
        country_means.columns = ['LE Country Code', 'cashed_EUR_average_for_MS']
        df_check = df_check.merge(country_means, how='left', on='LE Country Code')
        
        #calculating and adding the number of refusals/rejections in the approval process
        refusals = df_recovery_extract_workflow[df_recovery_extract_workflow['Workflow Action Code']=='SC'].groupby(['RO Local Key']).count()['Workflow Action Code'].reset_index()
        refusals.columns = ['RO Local Key', 'Number_of_refusals']
        df_check = df_check.merge(refusals, how='left', on='RO Local Key')
        df_check['Number_of_refusals'].fillna(0, inplace=True)
        #df_check.to_pickle('df_check_14_april_GNI_VAT.pickle')
        
        df_check['workflow_days_under_30'] = df_check['processing_days'].apply(lambda x: x.days <= 30)
        
        df_check['budget_line_correct'] = df_check.apply(lambda x: 
        (x['transaction_type'] == 'GNI' and budget_lines['GNI'] in x['Central Appropriation Key']) |
        (x['transaction_type'] == 'VAT' and budget_lines['VAT'] in x['Central Appropriation Key']), axis=1)
                                                                                     
        df_check['SAP_accounting_class'] = df_check.apply(lambda x:                                                  
        (x['transaction_type'] == 'GNI' and SAP_accounts['GNI'] in str(int(x['GL Account Id'])))|
        (x['transaction_type'] == 'VAT' and SAP_accounts['VAT'] in str(int(x['GL Account Id']))), axis=1)
        
            
        config_dict['checks_progress_state'] = 35
        config_dict['status_message'] = 'Downloading exchange rates from the European Central Bank Web API'
        """
        #need to load up the CFF data separately here from the cff_processor_Feb2021.py file
        cff_data = pd.read_excel(CFF_FILE)
        #loading a preprocessed cff file, that has the manually added dates. the exchange info is not reliable in the file
        df_all_calls = cff_data
        """
        df_all_calls = pd.read_excel(CFF_FILE)
        #we need to replace EL with GR, otherwise it won't find the country key
        df_all_calls['MS'] = df_all_calls['MS'].replace('EL', 'GR')
        
        import itertools
        #import timeit        
        #start = timeit.default_timer()      
        
        #use a lookup table instead of querying everything one by one
        
        def query_lookup_table(lookup_table, column1, columnvalue1, column2, columnvalue2, query_column):
            if column2 == None or columnvalue2 == None:
                return lookup_table[lookup_table[column1]==columnvalue1][query_column].iloc[0]
            else:
                return lookup_table[(lookup_table[column1]==columnvalue1) & (lookup_table[column2]==columnvalue2)][query_column].iloc[0]

        config_dict['checks_progress_state'] = 65
        config_dict['status_message'] = 'Calculating field values and running the audit checks'
            
        penultimate_days = df_all_calls['penultimate_working_day'].unique()
        countries = df_all_calls['MS'].unique()

        lookup_table = pd.DataFrame(list(itertools.product(countries,penultimate_days)),columns=['MS','penultimate_working_day'])
        lookup_table['ECB_rate_penultimate_working_day'] = lookup_table.apply(lambda x: query_ECB_forex_API(x['penultimate_working_day'], country=x['MS'])  , axis=1)

        last_day_of_year = '2019-12-31 00:00:00'
        year_end_df = pd.DataFrame(countries, columns=['MS'])
        year_end_df['ECB_rate_end_of_year'] = year_end_df.apply(lambda x: query_ECB_forex_API_exact_date(last_day_of_year, country=x['MS'])  , axis=1)
 
        df_all_calls['ECB_rate_penultimate_working_day'] = df_all_calls.apply(lambda x: query_lookup_table(lookup_table, 'MS', x['MS'], 'penultimate_working_day', x['penultimate_working_day'], 'ECB_rate_penultimate_working_day')  , axis=1)

        #df_all_calls.apply(lambda x: query_lookup_table(lookup_table, 'MS', x['MS'], 'penultimate_working_day', x['penultimate_working_day'], 'ECB_rate_end_of_year')  , axis=1)

        df_all_calls['ECB_rate_end_of_year'] = df_all_calls.apply(lambda x: query_lookup_table(year_end_df, 'MS', x['MS'], None, None, 'ECB_rate_end_of_year')  , axis=1)
 
        
        #lambda functions to get calendar information from the ECB
        #using the days where no EUR/CHR exchange rate was quoted as proxies for bank holidays
        #df_all_calls['ECB_rate_penultimate_working_day'] = df_all_calls.apply(lambda x: query_ECB_forex_API(x['penultimate_working_day'], country=x['MS'])  , axis=1)

        #commented out, not correct, we only need the calendar days (and optionally the preceeding working day)
        #df_all_calls['days_between_call_and_first_wk_day'] = df_all_calls.apply(lambda x: ECB_working_days_between_dates(x['date'], x['first_wk_day_next_month']), axis=1)
        
        df_all_calls['days_between_call_and_first_wk_day'] = df_all_calls['first_wk_day_next_month'] - df_all_calls['date']
        
        #last_day_of_year = '2019-12-31 00:00:00'
        #df_all_calls['ECB_rate_end_of_year'] = df_all_calls.apply(lambda x: query_ECB_forex_API_exact_date(last_day_of_year, country=x['MS'])  , axis=1)
        #df_all_calls['ECB_rate_end_of_year-1'] = df_all_calls.apply(lambda x: query_ECB_forex_API(last_day_of_year, country=x['MS'])  , axis=1)
        

        
        df_all_calls['ECB_rate_end_of_year_CFF_rate_diff'] = df_all_calls['ECB_rate_end_of_year'] - df_all_calls['rate']
        #df_all_calls['ECB_rate_end_of_year-1_CFF_rate_diff'] = df_all_calls['ECB_rate_end_of_year-1'] - df_all_calls['rate']
        
        #let's try to match the cff with the RO positions
        # on country, transaction type and month, month is the month of the 'first_wk_day_next_month' field
        # 'LE Country Code':memberstate, transaction_type:type, 'RO Document Date' or 'Doc. Date': 'first_wk_day_next_month'
        
        df_check['month'] = df_check['Doc. Date'].apply(lambda x: x.month)
        
        #need to cast it into a float, because there are nan values in the RO data
        #line commented out, because it doesn't work with the new format cff data, and asserts there is a separate cff for each month
        #df_all_calls['month'] = df_all_calls['first_wk_day_next_month'].apply(lambda x: float(x.month))
        df_all_calls['month'] = df_all_calls['cff_month'].apply(lambda x: float(x[0:2]))
        
        df_all_calls['LE Country Code'] = df_all_calls['MS']
        df_all_calls['transaction_type'] = df_all_calls['type']
        
        df_check = df_check.merge(df_all_calls, how='left', on=['LE Country Code','transaction_type', 'month'], suffixes=('_RO','_CFF'))
        
        df_check['local_currency_amount_in_EUR'] = df_check.apply(lambda row: row['payment'] / row['ECB_rate_penultimate_working_day'], axis=1)
        
        df_check['recovery_order_position_amount_in_local_curr_matches_call'] = df_check['RO Cashed Payment Amount (Eur)_pos'] == df_check['local_currency_amount_in_EUR']
        df_check['recovery_order_amount_in_local_curr_matches_call_diff'] = abs(df_check['RO Cashed Payment Amount (Eur)_pos'] - df_check['local_currency_amount_in_EUR'])
        df_check['amount_diff_within_tolerance'] = df_check['recovery_order_amount_in_local_curr_matches_call_diff'] < 0.05
        
        df_check['CFF_rate_matches_ECB_year_end_rate'] = df_all_calls['ECB_rate_end_of_year'] == df_all_calls['rate']
        df_check['CFF_rate_diff_within_tolerance'] = abs(df_check['ECB_rate_end_of_year_CFF_rate_diff'])  < 0.05
        
        #df_check['days_between_call_and_first_wk_day'] = df_check.apply(lambda x: ECB_working_days_between_dates(x['date'], x['first_wk_day_next_month']), axis=1)
                
        #need to convert to days for comparison
        #df_check['amount_requested_in_time'] = df_check['days_between_call_and_first_wk_day'] <= 15
        
        df_check['amount_requested_in_time'] = df_check['days_between_call_and_first_wk_day'].apply(lambda x: x.days) >= 14
        df_check['days_between_cashing_and_deadline'] = df_check['RO Due Date'] -df_check['RO Cashing Cashed Date']
        df_check['cashing deadline_observed'] = df_check['days_between_cashing_and_deadline'].apply(lambda x :x.days >= 0)
                
        #the checks taken over from the TOR script
        #Flagging anomalies
        #df_check['Amount exceeds country average'] = df_check['RO Cashed Amount (Eur)_hdr'] > df_check['cashed_EUR_average_for_MS']
        #this one is not needed for GNI/VAT according to the auditors
        df_check['Rejection in workflow'] = df_check['Number_of_refusals'] > 0
        df_check['Workflow steps exceed average'] = df_check['Workflow actions'] > df_check['Avg workflow actions']
        
        df_check['Avg workflow days'] = df_check['processing_days'].mean().days
        df_check['Workflow duration longer than average'] = df_check['processing_days'].apply(lambda x: x.days) > df_check['Avg workflow days']
        df_check['One-day-approval'] = df_check['processing_days'].apply(lambda x: x.days < 1)
        
        df_check['Missing SAP data'] = df_check['Text'].apply(pd.notna)
        
        #creating the lists
        df_check['Risk flags'] = df_check[['Rejection in workflow', #'Amount exceeds country average', 
                                                            'Workflow steps exceed average', 'Avg workflow days', 
                                                            'Workflow duration longer than average', 'One-day-approval'
                                                            ]].apply(lambda row: list(row[row == True].index), axis=1)
        
        df_check['Errors'] = df_check[['amount_requested_in_time', 'cashing deadline_observed', 'amount_diff_within_tolerance',
                                                         'workflow_days_under_30','budget_line_correct', 'SAP_accounting_class', 'subdelegation_found'
                                                         ]].apply(lambda row: list(row[row == False].index), axis=1)
        
        df_check['Matches'] = df_check[['amount_requested_in_time', 'cashing deadline_observed', 'amount_diff_within_tolerance',
                                                         'workflow_days_under_30','budget_line_correct', 'SAP_accounting_class', 'subdelegation_found'
                                                         ]].apply(lambda row: list(row[row == True].index), axis=1)
        
        df_check['Warnings'] = df_check[['Missing SAP data', 'CFF_rate_diff_within_tolerance'
                                                         ]].apply(lambda row: list(row[row == False].index), axis=1)
        
        
        df_check['Errors'] = df_check['Errors'].apply(lambda row: ['NOT_' + x for x in row])
        
        #df_check['Warnings'] = df_check['Warnings'].apply(lambda row: ['NOT_' + x for x in row if x != 'Missing SAP data'])
        df_check['Warnings'] = df_check['Warnings'].apply(lambda row: ['NOT_' + x if x != 'Missing SAP data' else x for x in row])
        
        df_check['CFF_file_link'] = df_check['filename'].apply(lambda x: make_hyperlink(x))

        config_dict['checks_progress_state'] = 85
        config_dict['status_message'] = 'Generating the Excel sheets containing the audit check results'
        
        #aligning the columns
        df_check = df_check[['RO Local Key', #RO
                               'RO Position Local Key',
                               'Central Appropriation Key',
                               'GL Account Id', 
                               'GL Account Short Desc',
                               'RO SubNature of Recovery Desc',
                               'RO Carried Forward Amount (Cur)_pos',
                               'RO Carried Forward Amount (Eur)_pos',
                               'RO Cashed Amount (Eur)_pos',
                               'RO Cashed Payment Amount (Eur)_pos',
                               'RO Initial Accepted Amount (Eur)_pos',
                               'RO Open Amount (Eur)_pos',
                               'RO Year Init Accepted Amt (Eur)_pos',
                               'RO Year Init Accepted Amt (Cur)_pos',
                               'LE Country Code', 
                               'RO Due Date',
                               'RO Document Date',
                               'RO Cashing Cashed Date',
                               'RO Carried Forward Amount (Cur)_hdr',
                               'RO Carried Forward Amount (Eur)_hdr',
                               'RO Cashed Amount (Eur)_hdr',
                               'RO Cashed Payment Amount (Eur)_hdr',
                               'RO Initial Accepted Amount (Eur)_hdr', 
                               'RO Open Amount (Eur)_hdr',
                               'RO Year Init Accepted Amt (Cur)_hdr',
                               'RO Year Init Accepted Amt (Eur)_hdr', 
                               'RO Justification',
                               'RO Contract or File nr',
                               
                               'month', #CFF
                               'memberstate',
                               'MS', 
                               'whole_year',
                               'per_12',
                               'payment', 
                               'currency', 
                               'rate', 
                               'type', 
                               'date', 
                               'CFF_file_link',
                               'first_wk_day_next_month', 
                               'penultimate_working_day',
                               'ECB_rate_penultimate_working_day',
                               'ECB_rate_end_of_year',
                               'days_between_call_and_first_wk_day',
                               #'SAP_merge', 
                               'transaction_type', #SAP report
                               'Amount in local cur.', 
                               'Account', 
                               'Company Code', 
                               'Document Number',
                               'Document Type', 
                               'Doc. Date', 
                               'Posting Date',
                               'Value Date',
                               'Posting Key', 
                               'Amount in doc. curr.', 
                               'Local Currency',
                               'Profit Center', 
                               'Text', 
                               #'Offsett.account type',
                               #'Offsetting acct no.',
                               'authorisation_date', 
                               'authorising_officer',
                               'processing_days',
                               'subdelegation_found',
                               'subdelegation_person',
                               'subdelegation_text',
                               'Workflow actions',
                               'Avg workflow actions',
                               'Number_of_refusals', 
        
                               'Avg workflow days',
                               
                               'Rejection in workflow',
                               'Workflow steps exceed average',
                               'Workflow duration longer than average', 
                               'One-day-approval',
        
                               'workflow_days_under_30', 
                               'budget_line_correct',
                               'SAP_accounting_class', 
        
                               'recovery_order_position_amount_in_local_curr_matches_call',
        
                               'Missing SAP data',
                               'amount_diff_within_tolerance',
                               'amount_requested_in_time',
                               'days_between_cashing_and_deadline', 
                               'cashing deadline_observed',
                               #'Amount exceeds country average',
                               'CFF_rate_diff_within_tolerance',
                               
                               'cashed_EUR_average_for_MS',
                               'recovery_order_amount_in_local_curr_matches_call_diff',
                               'local_currency_amount_in_EUR',
                               
                               'Risk flags',
                               'Warnings',
                               'Errors', 
                               'Matches']]
            
            
        
        #TODO: there's a fuckup with June and December, will have to investigate
        
        #df_check.to_excel('GNI_VAT_check_15april.xlsx')
        df_regular = df_check.copy()
        #restrict the transactions to "normal" VAT and GNI, that is the budget lines 1300 and 1400
        df_regular = df_regular[df_regular['Central Appropriation Key'].str.contains('1300') | df_regular['Central Appropriation Key'].str.contains('1400')]
        df_regular.sort_values(by=['LE Country Code','RO Document Date'], inplace=True)
        #df_regular_transposed = df_regular.transpose()
        
        df_others = df_check.copy()
        df_others = df_others[~df_others['Central Appropriation Key'].str.contains('1300') & ~df_others['Central Appropriation Key'].str.contains('1400')]
        df_others.sort_values(by=['LE Country Code','RO Document Date'], inplace=True)
        
        df_others['Errors'] = df_others[['amount_requested_in_time', 'cashing deadline_observed', 'amount_diff_within_tolerance',
                                                         'workflow_days_under_30','SAP_accounting_class', 'subdelegation_found'
                                                         ]].apply(lambda row: list(row[row == False].index), axis=1)
        
        
        df_others['Warnings'] = df_others[['Missing SAP data','budget_line_correct', 'CFF_rate_diff_within_tolerance'
                                                         ]].apply(lambda row: list(row[row == False].index), axis=1)
        
        
        df_others['Errors'] = df_others['Errors'].apply(lambda row: ['NOT_' + x for x in row])
        
        #df_others['Warnings'] = df_others['Warnings'].apply(lambda row: ['NOT_' + x for x in row if x != 'Missing SAP data'])
        df_others['Warnings'] = df_others['Warnings'].apply(lambda row: ['NOT_' + x if x != 'Missing SAP data' else x for x in row])
        
        # AND &, NOT ~
        
        #df_regular[df_regular['transaction_type'] == 'VAT']
        #df_regular[df_regular['transaction_type'] == 'GNI']
        
        config_dict['checks_progress_state'] = 100
        config_dict['status_message'] = 'Saving the result files'
        
        #saving the df with each transaction type to a different excel sheet
        with pd.ExcelWriter(RESULT_FILE) as writer:  
            df_regular[df_regular['transaction_type'] == 'VAT'].to_excel(writer, sheet_name='VAT', index=False)
            df_regular[df_regular['transaction_type'] == 'VAT'].transpose().to_excel(writer, sheet_name='VAT_transposed')
            df_regular[df_regular['transaction_type'] == 'GNI'].to_excel(writer, sheet_name='GNI', index=False)
            df_regular[df_regular['transaction_type'] == 'GNI'].transpose().to_excel(writer, sheet_name='GNI_transposed')
            
            df_others[df_others['transaction_type'] == 'VAT'].to_excel(writer, sheet_name='VAT_other', index=False)
            df_others[df_others['transaction_type'] == 'VAT'].transpose().to_excel(writer, sheet_name='VAT_other_transposed')
            df_others[df_others['transaction_type'] == 'GNI'].to_excel(writer, sheet_name='GNI_other', index=False)
            df_others[df_others['transaction_type'] == 'GNI'].transpose().to_excel(writer, sheet_name='GNI_other_transposed')
        
            
        #TODO: re-arrange columns by source (RO, CFF, SAP) and function (derived values, atomic checks), done
        #TODO: create the warnings, errors and matches lists, done
        #TODO: deal with 3203 and 3103 budget lines, outside the scope of the current project
        #TODO: fix cff processing to get the exchange rates properly from relevant columns of the cff files, done
        #TODO: deal with december differences, done it was due to an SAP join bug, changed from left merge to regular pandas merge
        #TODO: link CFF files (excel and pdf), done for excel
        #TODO: add other budget lines in separate tabs, done
        #TODO: indicate if SAP data is missing, done
        #TODO: incorrect budget line should be only warning for the others df, done
        
        with pd.ExcelWriter(RESULT_FILE) as writer:  
            df_regular[df_regular['transaction_type'] == 'VAT'].to_excel(writer, sheet_name='VAT', index=False)
            df_regular[df_regular['transaction_type'] == 'VAT'].transpose().to_excel(writer, sheet_name='VAT_transposed')
            add_Excel_formattting(writer, VAT_GNI_sections, VAT_GNI_conditionals,  sheetname='VAT_transposed', transaction_type = 'VAT/GNI')
            df_regular[df_regular['transaction_type'] == 'GNI'].to_excel(writer, sheet_name='GNI', index=False)
            df_regular[df_regular['transaction_type'] == 'GNI'].transpose().to_excel(writer, sheet_name='GNI_transposed')
            add_Excel_formattting(writer, VAT_GNI_sections, VAT_GNI_conditionals,  sheetname='GNI_transposed', transaction_type = 'VAT/GNI')
            
            df_others[df_others['transaction_type'] == 'VAT'].to_excel(writer, sheet_name='VAT_other', index=False)
            df_others[df_others['transaction_type'] == 'VAT'].transpose().to_excel(writer, sheet_name='VAT_other_transposed')
            add_Excel_formattting(writer, VAT_GNI_sections, VAT_GNI_conditionals,  sheetname='VAT_other_transposed', transaction_type = 'VAT/GNI')
            df_others[df_others['transaction_type'] == 'GNI'].to_excel(writer, sheet_name='GNI_other', index=False)
            df_others[df_others['transaction_type'] == 'GNI'].transpose().to_excel(writer, sheet_name='GNI_other_transposed')
            add_Excel_formattting(writer, VAT_GNI_sections, VAT_GNI_conditionals,  sheetname='GNI_other_transposed', transaction_type = 'VAT/GNI')
        
        now = datetime.datetime.now().strftime("on %Y-%m-%d at %H:%M:%S")
        
        
        config_dict['status_message'] = 'Running the audit checks and saving the of results completed ' + now
        
        config_dict['last_checks_datetime'] = datetime.datetime.now().strftime("%Y-%m-%d__%Hh%Mm%Ss")
        
        time.sleep(2)
        
        #config_dict['status_message'] = ''
        
        return df_check