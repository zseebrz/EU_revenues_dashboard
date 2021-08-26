#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 13:04:26 2020

@author: zseebrz
"""
import pandas as pd
#import numpy as np
#import time
#import math
#import re
import datetime
import requests, io, os

#import pandas as pd
#import time
#import os
import textract
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize

#from audit_revenues_2020 import query_ECB_forex_API, subdelegation_check, ECB_working_days_between_dates, save_xls_dict
#from audit_revenues_2020 import SAP_accounts, budget_lines, months#, eurozone_countries, all_currencies, non_eurozone_currencies
#from audit_revenues_2020 import ECB_penultimate_working_day_of_month, query_ECB_forex_API_exact_date, get_Ares_date
#from audit_revenues_2020 import ECB_first_working_day_after_19th_of_month, 
from audit_revenues_2021_july_website import last_day_of_month, get_Ares_date, get_esignature_date, get_cff_pdf_date #, preprocess_recovery_extract
#from audit_revenues_2020_basic import process_SAP_statement2, batch_check_recovery_orders


from sqlitedict import SqliteDict
config_dict = SqliteDict('./config/config_db.sqlite', autocommit=True)
  
VERIFIED_DATE_EXCEL_FILE = config_dict['VERIFIED_DATE_EXCEL_FILE']
OUTPUT_EXCEL_FILE = config_dict['OUTPUT_EXCEL_FILE']

def findColumn_first(df, pattern):
    #returns the first columname where the column values contain the pattern
    for col in df.columns:
        if len(df[df[col].str.contains(pattern, na=False)]) > 0:
            print ('Found col: ', col, ' for pattern: ', pattern)
            return col
        
def findColumn_exact_first(df, pattern):
    #returns the first columname where the column values contain the exact pattern
    for colname in df.columns:
        if pattern in df[colname].values:
            return colname
#       for row in df[col]:
#            #print (row)
#            if row == pattern:
#                print("Pattern: ", pattern, " Row: ", row)
#                return col

def getdate_CFF_xlsx(call_for_funds_file):
    df = pd.read_excel(call_for_funds_file)
    df.dropna(how='all', inplace=True)
    df.dropna(how='all', axis='columns', inplace=True)
    df.reset_index(inplace=True, drop=True)

    df.fillna('Empty', inplace = True)

    #get the month of the call
    # na=False is needed, because NAs confuse pandas
    # so take the first column, look for the cell containing "OUVRABLE", get the string out
    #getting the string out is getting the first position from the pandas series
    #and then split and take the second part of the split
    try: 
        month_of_cff = df[df.iloc[:,0].str.contains("OUVRABLE", na=False)].iloc[:,0].values[0].split('OUVRABLE DE ')[1]
    except IndexError:
        #Annex A - Monthly Call 06-2020
        #dirty trick to read the right sheet of the June xlsx file
        try:
            df = pd.read_excel(call_for_funds_file, sheet_name='Annex A - Monthly Call 06-2020')
            df.dropna(how='all', inplace=True)
            df.dropna(how='all', axis='columns', inplace=True)
            df.reset_index(inplace=True, drop=True)
            df.fillna('Empty', inplace = True)
            month_of_cff = df[df.iloc[:,0].str.contains("OUVRABLE", na=False)].iloc[:,0].values[0].split('OUVRABLE DE ')[1]
        #except XLRDError: #if sheet not found
        except:
                    if "CALCUL D'UN DOUZIEME SELON LE BR 5/2020 ADOPTE" in df.to_string():
                        month_of_cff = '10/2020'        
        
    print(call_for_funds_file)
    print(month_of_cff)
    return month_of_cff

def process_call_for_funds_xlsx(call_for_funds_file, cff_dates_from_pdf_dataframe):
    """
    

    Parameters
    ----------
    The filename for the call for funds excel file

    Returns
    -------
    A dataframe containing the amounts and countries related to each type of transaction.
    It currently extrascts data for VAT, GNI, UK Rebate and DA, NL, SE GNI-based correction.
    The current audit check scripts only use the VAT and GNI values, but this could be extended later.
    This is the part of the pre-processing that will need to be checked each year, because of formatting issues in the originals

    """

#    call_for_funds_file = './cff/Copy of appel 01-2020 PB2020.xlsx'
#    call_for_funds_file = './cff/Copy of appel 02-2020 B2020.xls'
#    call_for_funds_file = './cff/Copy of appel 06-2020 with summary.xlsx'
#    call_for_funds_file = '//home//vargaz//Dropbox//Ch5_GUI_demo_revenue//ch5_automation_sample_documents//Call for Funds 2019//12.pdf'
#    call_for_funds_file = 'C://Users//admin//Dropbox//Ch5_GUI_demo_revenue//2020//cff//Copy of appel 01-2020 PB2020.xlsx'
#    call_for_funds_file = 'd:/Working//working_docs//53_Ch5_revenues_2020//2020_full//cff//Copy of appel 06-2020 with summary.xlsx'

    
    #call_for_funds_file = 'd:/Working//working_docs//53_Ch5_revenues_2020//2020_full//cff//Copy of appel +10-2020 AB5.xlsx'
    #call_for_funds_file = './/2020_full//cff//Copy of appel 11-2020 AB7.xlsx'

    #call_for_funds_file = './/2020_full//cff/Copy of appel +10-2020 AB5.xlsx'

    df = pd.read_excel(call_for_funds_file)
    df.dropna(how='all', inplace=True)
    df.dropna(how='all', axis='columns', inplace=True)
    df.reset_index(inplace=True, drop=True)

    df.fillna('Empty', inplace = True)

    #get the month of the call
    # na=False is needed, because NAs confuse pandas
    # so take the first column, look for the cell containing "OUVRABLE", get the string out
    #getting the string out is getting the first position from the pandas series
    #and then split and take the second part of the split
    try: 
        month_of_cff = df[df.iloc[:,0].str.contains("OUVRABLE", na=False)].iloc[:,0].values[0].split('OUVRABLE DE ')[1]
    except IndexError:
        #Annex A - Monthly Call 06-2020
        #dirty trick to read the right sheet of the June xlsx file
        try:
            df = pd.read_excel(call_for_funds_file, sheet_name='Annex A - Monthly Call 06-2020')
            df.dropna(how='all', inplace=True)
            df.dropna(how='all', axis='columns', inplace=True)
            df.reset_index(inplace=True, drop=True)
            df.fillna('Empty', inplace = True)
            month_of_cff = df[df.iloc[:,0].str.contains("OUVRABLE", na=False)].iloc[:,0].values[0].split('OUVRABLE DE ')[1]
        #except XLRDError: #if sheet not found
        except:
                    if "CALCUL D'UN DOUZIEME SELON LE BR 5/2020 ADOPTE" in df.to_string():
                        month_of_cff = '10/2020'        
        
    print(call_for_funds_file)
    #print(month_of_cff)
    
    #now let's get the date of the CFF
    #temp = df[df.apply(lambda row: row.astype(str).str.contains('TAUX').any(), axis=1)]
    
      
    #get the unique values from the first column containing TAUX
    #this one is to generic enough, would fail for some months
    #date_colname = df.columns[(df.values=='TAUX\nRATE\nKURS').any(0)].tolist()
    #possible_date_values = df[str(date_colname[0])].unique()

    
    #check if the cff pdf date extraction file is in there
    #then get the dates, and take the one closest to the month of the cff document
    """
    
    try:
        possible_date_values = pd.read_excel(VERIFIED_DATE_EXCEL_FILE)
        possible_date_values = possible_date_values['date'].unique()
        

        temp_date = pd.to_datetime(month_of_cff, dayfirst=True)
        date = possible_date_values[possible_date_values < pd.Timestamp.to_datetime64(temp_date)].max()
 
        #need to convert back to timestamp from np.datetime64,the simplest method is to go through epoc time
        #even though it triggers a depreciation warning
        ts = (date - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        date = datetime.datetime.utcfromtimestamp(ts)
           
    except:
        print('No CFF date pdf file, aborting...')
        raise Exception

    """
    date = cff_dates_from_pdf_dataframe[cff_dates_from_pdf_dataframe['date_xlsx']==month_of_cff]
    date = date['date_match'].values[0]
    
    print(month_of_cff)
    #print('break')
    print(date)
    #input("Press Enter to continue...")

    
    #here we have to get the call for funds data from the verified CFF table
    #we know the month of cff from the Excel file, we just add the corresponding CFF data from the verified file
    
    call_for_funds_date = date
    
    #commented out, the CFF is not always for the next month, sometimes can be two months in advance
    #but I didn't change the variable name to save me from rewriting everywhere
    #next_month_start = call_for_funds_date.replace(day=28) + datetime.timedelta(days=4)            

    next_month_start = pd.to_datetime(month_of_cff, dayfirst=True)            


    """   
    #getting the first working day of the following month by proxy from ECB
    try:
        next_month_start = call_for_funds_date.replace(day=28) + datetime.timedelta(days=4)  
    except:
        #another dirty trick, the July cff doesn't contain a date
        #doesn't matter, because I'll have to extract them from the pdfs anyway
        call_for_funds_date = datetime.datetime(2020,1,1,0,0)
        next_month_start = call_for_funds_date.replace(day=28) + datetime.timedelta(days=4)  
    """
    
    #next_month_end = next_month_start.replace(day=28) + datetime.timedelta(days=4) - datetime.timedelta(days=1)
    next_month_end = last_day_of_month(next_month_start)
    entrypoint = 'https://sdw-wsrest.ecb.europa.eu/service/' # Using protocol 'https'
    resource = 'data'           # The resource for data queries is always'data'
    flowRef ='EXR'              # Dataflow describing the data that needs to be returned, exchange rates in this case
    key = 'D.CHF.EUR.SP00.A'    # Defining the dimension values, explained below
    parameters = {
            'startPeriod':  next_month_start.strftime('%Y')+ '-' +  next_month_start.strftime('%m')+ '-' + next_month_start.strftime('%d'),
            'endPeriod':    next_month_end.strftime('%Y')+ '-' +  next_month_end.strftime('%m')+ '-' + next_month_end.strftime('%d'),
            }
    request_url = entrypoint + resource + '/'+ flowRef + '/' + key
    response = requests.get(request_url, params=parameters, headers={'Accept': 'text/csv'})
    next_wk_month_df = pd.read_csv(io.StringIO(response.text))
    next_wk_month_df = next_wk_month_df.filter(['TIME_PERIOD', 'OBS_VALUE'], axis=1)
    next_wk_month_df['TIME_PERIOD'] = pd.to_datetime(next_wk_month_df['TIME_PERIOD'])
    next_wk_month_df = next_wk_month_df.set_index('TIME_PERIOD')
    first_wk_day_of_next_month = next_wk_month_df.index[0]

    #getting the penultimate working day of the month by proxy from ECB
    
    #commented out, the CFF is not always for the next month, sometimes can be two months in advance
    #but I didn't change the variable name to save me from rewriting everywhere
    #last_day = last_day_of_month(call_for_funds_date)
    
    #we need the last day of the month preceeding the cff month
    #it's easier to manipulate the string than to run back and forth with date formats

    if int(month_of_cff.split('/')[0])-1 == 0:
         prev_month_of_cff = '12/' + str(int(month_of_cff.split('/')[1])-1)
    else:
        prev_month_of_cff = str(int(month_of_cff.split('/')[0])-1) + '/' + month_of_cff.split('/')[1]
    last_day = last_day_of_month(pd.to_datetime(prev_month_of_cff, dayfirst=True))

    call_for_funds_date__ = pd.to_datetime(prev_month_of_cff)
    prev_month_of_cff
    
    entrypoint = 'https://sdw-wsrest.ecb.europa.eu/service/' # Using protocol 'https'
    resource = 'data'           # The resource for data queries is always'data'
    flowRef ='EXR'              # Dataflow describing the data that needs to be returned, exchange rates in this case
    key = 'D.CHF.EUR.SP00.A'    # Defining the dimension values, explained below
    parameters = {
            'startPeriod':  datetime.datetime.strftime(call_for_funds_date__, '%Y')+ '-' +  datetime.datetime.strftime(call_for_funds_date__, '%m')+ '-01',  # Start date of the time series
            'endPeriod': last_day.strftime('%Y')+ '-' +  last_day.strftime('%m')+ '-' + last_day.strftime('%d')  # End date of the time series
            #'endPeriod': forex_year + '-' + str(int( GNI_memberstates forex_month)+1) + '-01'
            }
    request_url = entrypoint + resource + '/'+ flowRef + '/' + key
    response = requests.get(request_url, params=parameters, headers={'Accept': 'text/csv'})
    ECB_df = pd.read_csv(io.StringIO(response.text))
    ECB_ts = ECB_df.filter(['TIME_PERIOD', 'OBS_VALUE'], axis=1)
    # 'TIME_PERIOD' was of type 'object' (as seen in df.info). Convert it to datetime first
    ECB_ts['TIME_PERIOD'] = pd.to_datetime(ECB_ts['TIME_PERIOD'])
    # Set 'TIME_PERIOD' to be the index
    ECB_ts = ECB_ts.set_index('TIME_PERIOD')
    penultimate_working_day = str(ECB_ts.iloc[-2:-1].index[0]) #penultimate working day of the month (last but one)

#we have the call date and the month of the call, and the penultimate working day at this point
#now we need to get the data out, but I need a coffee before that

    memberstate_colname = findColumn_first(df, "MEMBER STATE")        
    MS_colname = findColumn_first(df, "MS")        
    v1_colname = findColumn_first(df, "( V1 )")  
    v2_colname = findColumn_first(df, "( V2 )")  
    #v3_colname = findColumn_first(df, "(V3)")  
    v4_colname = findColumn_first(df, "( V4 )")  
    v5_colname = findColumn_first(df, "( V5 )")  
    currency_colname = findColumn_first(df, "Currency")
    if currency_colname == None:
        currency_colname = findColumn_first(df, "BGN")
    v6_colname = findColumn_exact_first(df, "(V6)")  
  
    g1_colname = findColumn_first(df, "( G1 )")  
    g2_colname = findColumn_first(df, "( G2 )")  
    #g3_colname = findColumn_first(df, "(G3)")  
    g4_colname = findColumn_first(df, "( G4 )")  
    g5_colname = findColumn_first(df, "( G5 )")
    g6_colname = findColumn_exact_first(df, "(G6)") 
    
    c1_colname = findColumn_first(df, "( C1 )")  
    c2_colname = findColumn_first(df, "( C2 )")  
    #c3_colname = findColumn_first(df, "(C3)")  
    c4_colname = findColumn_first(df, "( C4 )")  
    c5_colname = findColumn_first(df, "( C5 )")
    c6_colname = findColumn_exact_first(df, "(C6)") 

    r1_colname = findColumn_first(df, "( R1 )")  
    r2_colname = findColumn_first(df, "( R2 )")  
    #r3_colname = findColumn_first(df, "(R3)")  
    r4_colname = findColumn_first(df, "( R4 )")  
    r5_colname = findColumn_first(df, "( R5 )")
    r6_colname = findColumn_exact_first(df, "(R6)") 
    
    #(df[memberstate_colname]=='Belgique').idxmax()
    #df.columns.get_loc(memberstate_colname)
    
    memberstate_VAT = df.iloc[(df[memberstate_colname]=='Belgique').idxmax():(df[memberstate_colname]=='United Kingdom').idxmax()+1, df.columns.get_loc(memberstate_colname)]
    MS_VAT = df.iloc[(df[memberstate_colname]=='Belgique').idxmax():(df[memberstate_colname]=='United Kingdom').idxmax()+1, df.columns.get_loc(MS_colname)]
    V1 = df.iloc[(df[memberstate_colname]=='Belgique').idxmax():(df[memberstate_colname]=='United Kingdom').idxmax()+1, df.columns.get_loc(v1_colname)]
    V2 = df.iloc[(df[memberstate_colname]=='Belgique').idxmax():(df[memberstate_colname]=='United Kingdom').idxmax()+1, df.columns.get_loc(v2_colname)]

    #V3 = df.iloc[(df[memberstate_colname]=='Belgique').idxmax():(df[memberstate_colname]=='United Kingdom').idxmax()+1, df.columns.get_loc(v3_colname)]
    V4 = df.iloc[(df[memberstate_colname]=='Belgique').idxmax():(df[memberstate_colname]=='United Kingdom').idxmax()+1, df.columns.get_loc(v4_colname)]
    V5 = df.iloc[(df[memberstate_colname]=='Belgique').idxmax():(df[memberstate_colname]=='United Kingdom').idxmax()+1, df.columns.get_loc(v5_colname)]
    try:
        V6 = df.iloc[(df[memberstate_colname]=='Belgique').idxmax():(df[memberstate_colname]=='United Kingdom').idxmax()+1, df.columns.get_loc(v6_colname)]
    except:
        V6 = []

    CURR_VAT = df.iloc[(df[memberstate_colname]=='Belgique').idxmax():(df[memberstate_colname]=='United Kingdom').idxmax()+1, df.columns.get_loc(currency_colname)]

    #it's easier to get the start values from the MS list [0 is VAT, 1 is GNI], so that we can do it for CORR/REBATE/TOTAL
    #CORR is 2 and C; RED is 3 and R; 4 is usually, but not always the total, T
    
    #this will need to be reconsidered after 2021, with the UK gone, but the scripts will have to be revised for each year anyway
    table_start_values = sorted(list(df[memberstate_colname][df[memberstate_colname]=='Belgique'].index))
    table_end_values = sorted(list(df[memberstate_colname][df[memberstate_colname]=='United Kingdom'].index))
    
    memberstate_GNI = df.iloc[table_start_values[1]:table_end_values[1]+1, df.columns.get_loc(memberstate_colname)]
    MS_GNI = df.iloc[table_start_values[1]:table_end_values[1]+1, df.columns.get_loc(MS_colname)]
    G1 = df.iloc[table_start_values[1]:table_end_values[1]+1, df.columns.get_loc(g1_colname)]
    
    G2 = df.iloc[table_start_values[1]:table_end_values[1]+1, df.columns.get_loc(g2_colname)]
    #G3 = df.iloc[table_start_values[1]:table_end_values[1]+1, df.columns.get_loc(g3_colname)]
    G4 = df.iloc[table_start_values[1]:table_end_values[1]+1, df.columns.get_loc(g4_colname)]
    G5 = df.iloc[table_start_values[1]:table_end_values[1]+1, df.columns.get_loc(g5_colname)]
    try:
        G6 = df.iloc[table_start_values[1]:table_end_values[1]+1, df.columns.get_loc(g6_colname)]
    except:
        G6 = []
    
    CURR_GNI = df.iloc[table_start_values[1]:table_end_values[1]+1, df.columns.get_loc(currency_colname)]

    #CORRECTION

    memberstate_CORR = df.iloc[table_start_values[2]:table_end_values[2]+1, df.columns.get_loc(memberstate_colname)]
    MS_CORR = df.iloc[table_start_values[2]:table_end_values[2]+1, df.columns.get_loc(MS_colname)]
    C1 = df.iloc[table_start_values[2]:table_end_values[2]+1, df.columns.get_loc(c1_colname)]
    
    C2 = df.iloc[table_start_values[2]:table_end_values[2]+1, df.columns.get_loc(c2_colname)]
    #G3 = df.iloc[table_start_values[2]:table_end_values[2]+1, df.columns.get_loc(c3_colname)]
    C4 = df.iloc[table_start_values[2]:table_end_values[2]+1, df.columns.get_loc(c4_colname)]
    C5 = df.iloc[table_start_values[2]:table_end_values[2]+1, df.columns.get_loc(c5_colname)]
    try:
        C6 = df.iloc[table_start_values[2]:table_end_values[2]+1, df.columns.get_loc(c6_colname)]
    except:
        C6 = []
    
    CURR_CORR = df.iloc[table_start_values[2]:table_end_values[2]+1, df.columns.get_loc(currency_colname)]

    #REDUCTION
    memberstate_RED = df.iloc[table_start_values[3]:table_end_values[3]+1, df.columns.get_loc(memberstate_colname)]
    MS_RED = df.iloc[table_start_values[3]:table_end_values[3]+1, df.columns.get_loc(MS_colname)]
    R1 = df.iloc[table_start_values[3]:table_end_values[3]+1, df.columns.get_loc(r1_colname)]
    
    R2 = df.iloc[table_start_values[3]:table_end_values[3]+1, df.columns.get_loc(r2_colname)]
    #G3 = df.iloc[table_start_values[3]:table_end_values[3]+1, df.columns.get_loc(r3_colname)]
    R4 = df.iloc[table_start_values[3]:table_end_values[3]+1, df.columns.get_loc(r4_colname)]
    R5 = df.iloc[table_start_values[3]:table_end_values[3]+1, df.columns.get_loc(r5_colname)]
    try:
        R6 = df.iloc[table_start_values[3]:table_end_values[3]+1, df.columns.get_loc(r6_colname)]
    except:
        R6 = []
    
    CURR_RED = df.iloc[table_start_values[3]:table_end_values[3]+1, df.columns.get_loc(currency_colname)]


   
    #In the Feb, June, Aug and Nov CFFs the rates are listed under V6, G6 etc. But the are the rates from 31/12/2019 anyway
    #so in this version of the preprocessor, we nevertheless extract them as they are in the table
    #but for that we need to check if we're looking at the right column
    #if there is no V6 or G6, we just take V4 and G4
    #if there is V6 or G6, we take them as the rate
    
    #print(G6, V6)
    if len(G6) == 0 and len(V6) == 0:
        GNI_rates = list(G4)
        VAT_rates = list(V4)
        CORR_rates = list(C4)
        RED_rates = list(R4)
    else:
         GNI_rates = list(G6)
         VAT_rates = list(V6)  
         CORR_rates = list(C6)
         RED_rates = list(R6)


    df_GNI = pd.DataFrame()
    df_GNI['memberstate'] = list(memberstate_GNI)   #need to recast the pandas series as lists
    df_GNI['MS'] = list(MS_GNI)                     #otherwise it gets confused with the indexes  
    df_GNI['whole_year'] = list(G1)
    df_GNI['per_12'] = list(G2)
    df_GNI['payment'] = list(G5)
    df_GNI['currency'] = list(CURR_GNI)
    #df_GNI['rate'] = list(G4)
    df_GNI['rate'] = GNI_rates

    df_VAT = pd.DataFrame()
    df_VAT['memberstate'] = list(memberstate_VAT)   #need to recast the pandas series as lists
    df_VAT['MS'] = list(MS_VAT)                     #otherwise it gets confused with the indexes  
    df_VAT['whole_year'] = list(V1)
    df_VAT['per_12'] = list(V2)
    df_VAT['payment'] = list(V5)
    df_VAT['currency'] = list(CURR_VAT)
    #df_VAT['rate'] = list(V4)
    df_VAT['rate'] = VAT_rates  
       
    df_CORR = pd.DataFrame()
    df_CORR['memberstate'] = list(memberstate_CORR)   #need to recast the pandas series as lists
    df_CORR['MS'] = list(MS_CORR)                     #otherwise it gets confused with the indexes  
    df_CORR['whole_year'] = list(C1)
    df_CORR['per_12'] = list(C2)
    df_CORR['payment'] = list(C5)
    df_CORR['currency'] = list(CURR_CORR)
    #df_CORR['rate'] = list(C4)
    df_CORR['rate'] = CORR_rates  

    df_RED = pd.DataFrame()
    df_RED['memberstate'] = list(memberstate_RED)   #need to recast the pandas series as lists
    df_RED['MS'] = list(MS_RED)                     #otherwise it gets confused with the indexes  
    df_RED['whole_year'] = list(R1)
    df_RED['per_12'] = list(R2)
    df_RED['payment'] = list(R5)
    df_RED['currency'] = list(CURR_RED)
    #df_RED['rate'] = list(R4)
    df_RED['rate'] = RED_rates 

    df_GNI['type'] = 'GNI'
    df_VAT['type'] = 'VAT'
    df_CORR['type'] = 'COR'  
    df_RED['type'] = 'RED' 
    df_call = df_GNI.append(df_VAT).append(df_CORR).append(df_RED)
    
    df_call['cff_month'] = month_of_cff
    
    df_call['date'] = call_for_funds_date
    df_call['filename'] = call_for_funds_file
    df_call['first_wk_day_next_month'] = first_wk_day_of_next_month
    df_call['penultimate_working_day'] = penultimate_working_day 
    
    return df_call

def prepare_call_for_funds_for_batch_xlsx(folder):
    calls_list = []
    for dirname, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            print(os.path.join(dirname, filename))
            call_data_primary = process_call_for_funds_xlsx(os.path.join(dirname, filename))
            calls_list.append(call_data_primary)

    df_all_calls = pd.DataFrame()
    for call in calls_list:
        df_all_calls = df_all_calls.append(call)

    df_all_calls.reset_index(inplace=True, drop=True)
    """
    #remove all non-number characters
    regex = re.compile(r'[a-zA-Z]+')

    #remove dots, letters and convert to numeric
    df_all_calls[['whole_year',
               'per_12',
               'payment',
               'rate']] = df_all_calls[['whole_year',
               'per_12',
               'payment',
               'rate']].apply(lambda x: x.str.replace('.',
                        '')).apply(lambda x: x.str.replace(',',
                           '.')).apply(lambda x: x.str.replace('(',
                           '-')).apply(lambda x: x.str.replace(')',
                           '')).apply(lambda x: x.str.replace(regex,'',
                               regex=True)).apply(pd.to_numeric)
    """
    
    #convert to datetime
    df_all_calls['date'] = df_all_calls['date'].apply(lambda x: pd.to_datetime(x, dayfirst=True))

    df_all_calls['MS'] = df_all_calls['MS'].str.replace('L V', 'LV')
    df_all_calls['MS'] = df_all_calls['MS'].str.replace('OS', 'AT')
    df_all_calls['MS'] = df_all_calls['MS'].str.replace('Fl', 'FI')
    df_all_calls['MS'] = df_all_calls['MS'].str.replace('PO', 'PT')
    df_all_calls['MS'] = df_all_calls['MS'].str.replace('UK', 'GB')
        
    return df_all_calls

def prepare_call_for_funds_for_batch_xlsx_website(folder, CFF_DATE_TABLE = './processed/cff_pdf_dates.xlsx'):
    cff_dates_from_pdf_dataframe = pd.read_excel(CFF_DATE_TABLE)
    calls_list = []
    for dirname, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            print(os.path.join(dirname, filename))
            call_data_primary = process_call_for_funds_xlsx(os.path.join(dirname, filename), cff_dates_from_pdf_dataframe)
            calls_list.append(call_data_primary)

    df_all_calls = pd.DataFrame()
    for call in calls_list:
        df_all_calls = df_all_calls.append(call)

    df_all_calls.reset_index(inplace=True, drop=True)
    """
    #remove all non-number characters
    regex = re.compile(r'[a-zA-Z]+')

    #remove dots, letters and convert to numeric
    df_all_calls[['whole_year',
               'per_12',
               'payment',
               'rate']] = df_all_calls[['whole_year',
               'per_12',
               'payment',
               'rate']].apply(lambda x: x.str.replace('.',
                        '')).apply(lambda x: x.str.replace(',',
                           '.')).apply(lambda x: x.str.replace('(',
                           '-')).apply(lambda x: x.str.replace(')',
                           '')).apply(lambda x: x.str.replace(regex,'',
                               regex=True)).apply(pd.to_numeric)
    """
    
    #convert to datetime
    df_all_calls['date'] = df_all_calls['date'].apply(lambda x: pd.to_datetime(x, dayfirst=True))

    df_all_calls['MS'] = df_all_calls['MS'].str.replace('L V', 'LV')
    df_all_calls['MS'] = df_all_calls['MS'].str.replace('OS', 'AT')
    df_all_calls['MS'] = df_all_calls['MS'].str.replace('Fl', 'FI')
    df_all_calls['MS'] = df_all_calls['MS'].str.replace('PO', 'PT')
    df_all_calls['MS'] = df_all_calls['MS'].str.replace('UK', 'GB')
        
    return df_all_calls

def get_cff_dates_from_pdf_for_batch(folder):
    dates_list = []
    cff_month_list = []
    for dirname, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            print(os.path.join(dirname, filename))
            cff_date = get_Ares_date(os.path.join(dirname, filename))
            if pd.isna(cff_date):
                #if there's no Ares date found on the first page, the CFF date is after June 2020, and the e-signature is on the last page
                cff_date = get_esignature_date(os.path.join(dirname, filename))
            try:
                cff_month = get_cff_pdf_date(os.path.join(dirname, filename))
            except:
                cff_month = cff_date.replace(month = cff_date.month+1, day=1)
            dates_list.append(cff_date)
            cff_month_list.append(cff_month)
    return dates_list, filenames, cff_month_list

def get_cff_dates_from_xlsx_for_batch(folder):
    dates_list = []
    for dirname, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            print(os.path.join(dirname, filename))
            cff_date = getdate_CFF_xlsx(os.path.join(dirname, filename))
            dates_list.append(cff_date)
    return dates_list

def prepare_subdelegation_for_batch(pathname='./Sub-delegations for signing'):
    sentence_list = []
    tokens_list = []
    filenames_list = []
    for dirname, dirnames, filenames in os.walk(pathname):
        for filename in filenames:
            print(os.path.join(dirname, filename))
            #I will OCR everything, because the originals have shitty quality
            text = textract.process(os.path.join(dirname, filename), method='tesseract')
            tokens = word_tokenize(text.decode('utf-8'))
            sentences = sent_tokenize(text.decode('utf-8'))
            print (tokens, sentences)
            sentence_list.append(sentences)
            tokens_list.append(tokens)
            filenames_list.append(os.path.join(dirname, filename))
    subdelegation_df = pd.DataFrame(zip(sentence_list, tokens_list, filenames_list), columns=['sentences', 'tokens', 'filename'])
    
    return subdelegation_df 

def prepare_SAP_for_batch(pathname='./2020_full/sap'):
    df = pd.DataFrame()
    for dirname, dirnames, filenames in os.walk(pathname):
        for filename in filenames:
            print(os.path.join(dirname, filename))
            df_temp = pd.read_excel(os.path.join(dirname, filename))
            df = df.append(df_temp).reset_index(drop=True)
    df = df[df['Account'].notna()]
    df = df[(df['Value Date'] < '2021-01-01')]
    #df[(df['Value Date'] > '2021-01-01')]    
    return df


#this file is a module for the website, so no direct execution 
"""

#bloody excels do not contain the cff date, only an indicative date for the exchange rate
#i'll have to extract them from the bloody pdfs

#loading or extracting cff dates from pdf files
try:
    #the auditor will need to manually check the cff_pdf_dates.xlsx and fill in missing dates
    #so if the file already exists, we should not overwrite it
    dates = pd.read_excel('cff_pdf_dates.xlsx')
    print('CFF date Excel file exists, loading saved data')
    print(dates)
except:
    print('CFF date Excel file does NOT exist, running PDF processing')
    #get_Ares_date(pdf_file)
    dates = get_cff_dates_from_pdf_for_batch('./pdf/')
    dates_df = pd.DataFrame(dates)
    dates_df.columns = ['date']
    dates_df.to_excel(VERIFIED_DATE_EXCEL_FILE)
    
#TODO: the cff_pdf_dates is currently hard-coded, will have to change that

#the procedure is first to run the pdf date extractor, and then verify and correct the date file manually
#and then run the prepare_call_for_funds_for_batch_xlsx function to get the data out


cff_data = prepare_call_for_funds_for_batch_xlsx('.//2020_full//cff/')

CFF_DATE_TABLE = './processed/cff_pdf_dates.xlsx'

cff_data = prepare_call_for_funds_for_batch_xlsx_website('.//uploads//cff_excel/', './processed/cff_pdf_dates.xlsx')

#cff_data.to_csv('df_all_calls_2020_working_days_wrong.csv')
cff_data.to_excel(OUTPUT_EXCEL_FILE)
"""


#we save the excel file that we will re-use later in the specific processing scripts