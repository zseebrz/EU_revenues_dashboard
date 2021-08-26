#AUDIT FUNCTIONS MODULE
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 10:25:05 2020

@author: vargaz
"""

#TODO: remove references to global variables!!!!!!! (transaction type, bank statement data, SAP statement data!!!!!)
#TODO: remove references to unused libraries and procedures

#from io import StringIO
#import sys
#import os
#import time
#if os.name == 'posix':
#    import PySimpleGUIQt as sg
#else:
#   import PySimpleGUI as sg

#import PySimpleGUI as sg

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter#, XMLConverter, HTMLConverter
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import resolve1
import pdfminer


import io
import re
import datetime
#import sqlite3
import pandas as pd
#from pathlib import Path
import numpy as np
import requests#, json
#from nltk.corpus import stopwords

#import fitz
#import tkinter as tk
#from PIL import Image, ImageTk

#import textract
#from fuzzywuzzy import fuzz
#from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize

import unicodedata
#from babel.numbers import format_decimal, parse_decimal

from pandas import ExcelWriter

import math

from price_parser import Price

from operator import concat

from collections import defaultdict
from itertools import count

#general data dicts
#member state name dictionary for call for funds
months =	{
  "1": "January",
  "2": "February",
  "3": "March",
  "4": "April",
  "5": "May",
  "6": "June",
  "7": "July",
  "8": "August",
  "9": "September",
  "10": "October",
  "11": "November",
  "12": "December"
}

ms_dict =	{
  "BE": "Belqique",
  "BG": "Bălgarija",
  "CZ": "Česká Republika",
  "DK": "Danmark",
  "DE": "Deutschland",
  "EE": "Eesti Vabariik",
  "IE": "Ireland",
#we replace EL with GR to spare the effort
#  "EL": "Ellas",
  "GR": "Ellas",
  "ES": "España",
  "FR": "France",
  "HR": "Hrvatska",
  "IT": "Italia",
  "CY": "Kýpros",
  "LV": "Latvija",
  "LT": "Lietuva",
  "LU": "Luxembourg",
  "HU": "Magyarország",
  "MT": "Malta",
  "NL": "Nederland",
  "OS": "Österreich",
  "PL": "Polska",
  "PO": "Portugal",
#  "RO": "Romania"
  "RO": "România",
  "SI": "Slovenija",
  "SK": "Slovensko",
  "FI": "Suomi",
  "SE": "Sverige",
  "UK": "United Kingdom"
}

ms_dict_SAP =	{
  "BE": "belqique",
  "BG": "bulgarie",
  "CZ": "tcheque",
  "DK": "danemark",
  "DE": "allemagne",
  "EE": "estonie",
  "IE": "irlande",
  "GR": "grece",
  "ES": "espagne",
  "FR": "france",
  "HR": "croatie",
  "IT": "italie",
  "CY": "chypre",
  "LV": "lettonie",
  "LT": "lituanie",
  "LU": "luxembourg",
  "HU": "hongrie",
  "MT": "malte",
  "NL": "pay-pas",
  "OS": "autriche",
  "PL": "pologne",
  "PO": "portugal",
  "RO": "romanie",
  "SI": "slovenie",
  "SK": "slovaquie",
  "FI": "finlande",
  "SE": "suede",
  "UK": "royaume-uni"
}

eurozone_countries = ['AT', 'BE', 'CY', 'EE', 'FI', 'FR', 'DE', 'GR', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PT', 'SK', 'SI', 'ES']

non_eurozone_currencies = {
    'BG': 'BGN',
    'CZ': 'CZK', 
    'DK' : 'DKK',
    'UK' : 'GBP',
    'GB' : 'GBP',
    'HR' : 'HRK',
    'HU' : 'HUF',
    'PL' : 'PLN',
    'RO': 'RON',
    'SE' : 'SEK',
    "CH" : 'CHF'
    } 

all_currencies = {
        'AT': 'EUR',
        'BE': 'EUR',
        'CY': 'EUR',
        'EE': 'EUR',
        'FI': 'EUR',
        'FR': 'EUR',
        'DE': 'EUR',
        'GR': 'EUR',
        'IE': 'EUR',
        'IT': 'EUR',
        'LV': 'EUR',
        'LT': 'EUR',
        'LU': 'EUR',
        'MT': 'EUR',
        'NL': 'EUR',
        'PT': 'EUR',
        'SK': 'EUR',
        'SI': 'EUR',
        'ES': 'EUR',
        'BG': 'BGN',
        'CZ': 'CZK', 
        'DK': 'DKK',
        'UK': 'GBP',
        'GB': 'GBP',
        'HR': 'HRK',
        'HU': 'HUF',
        'PL': 'PLN',
        'RO': 'RON',
        'SE': 'SEK',
        "CH": 'CHF'
    } 

SAP_accounts = {
    'GNI': '70601300',
    'VAT': '70601400', 
    'TOR_customs' : '70601203',
    'TOR_sugar' : '70601205',
    'CORR' : '70601500',
    'REDUCTION' : '70601510',
    'GNI_balance': '70601300',
    'VAT_balance': '70601400',
    'netting': '70601800'
    } 

budget_lines = {
    'GNI': '1400',
    'VAT': '1300', 
    'TOR_customs' : '1200',
    'TOR_sugar' : '1100',
    'CORR' : '1500',
    'REDUCTION' : '1600',
    'GNI_balance': '3203',
    'VAT_balance': '3103', 
    'netting': '3300'
    } 

hitlist_dic = {
            #type of matches with descriptions:	
        	'A' : 'Full RO EUR amount',
            'E' : 'Full RO EUR amount, format diff.',
            'F' : 'Full RO curr.amount, format diff.',
        	'I' : 'Full RO curr.amount',
        	'J' : '125% of RO curr., rounded up',
        	'K' : '125% of RO curr., rounded up, format diff.',
        	'O' : '133% of RO curr., rounded up, format diff.',
        	'P' : '133% of RO curr., rounded up, format diff.',
        	'Q' : '133% of RO curr., rounded, format diff.',
        	'QQ' : '133% of RO curr., rounded, format diff.',
        	'QQQ' : '125% of RO curr., rounded, format diff.',
        	'R' : '133% of RO curr., rounded down, format diff.',
        	'RR' : '133% of RO curr., rounded up, format diff.',
        	'RRR' : '125% of RO curr., rounded up, format diff.',
        	'S' : '125% of RO curr., rounded up, format diff.',
        	'T' : '125% of RO curr., rounded down',
        	'U' : '125% of RO curr., rounded more down',
        	'V' : '125% of RO curr., rounded more down',
            'X' : '125% of of RO curr., rounded up, format diff.',
            'Y' : 'RO local currency amount',
            'Z' : 'RO local currency amount',
            'AA' : 'RO local currency amount, format change',
            'DD' : 'RO local currency amount, format change',
            'EE' : 'RO local currency amount, format change',
            'GG' : 'RO local currency amount, format change',
            'HH' : 'RO local currency amount, format change',
            'II' : 'RO local currency amount, format change',
            'JJ' : 'RO local currency amount, format change, X',
            'JJJ' : 'RO local currency amount, format change, X',
            'HU' : 'RO local currency amount, format change, X',
            'IT' : 'RO local currency amount, format change, X',
            'N': '75% of RO curr, round up'
            }


#formatting settings for the final Excel result files
VAT_GNI_sections = {'RO_data':'A2:A29',
            'CFF_data':'A30:A40',
            'SAP_data': 'A41:A59',
            'workflow_data': 'A60:A69',
            'atomic_checks': 'A70:A83',
            'calculated_values' : 'A84:A86', 
            'results': 'A87:A90'}

VAT_GNI_conditionals = {'good': 'B87:OO89',
                'warning': 'B87:OO88',
                'error': 'B88:OO89'}

TOR_sections = {'RO_data':'A2:A29',
            'CFF_data':'A30:A38',
            'SAP_data': 'A39:A56',
            'workflow_data': 'A57:A65',
            'atomic_checks': 'A66:A89',
            'calculated_values' : 'A90:A108', 
            'results': 'A109:A113'}

#replace order of warnings and errors
TOR_conditionals = {'good': 'B109:OO112',
                'warning': 'B109:OO111',
                'error': 'B111:OO112'}

TOR_no_SAP_match_sections = {'RO_data':'A2:A29',
            #'CFF_data':'A30:A40',
            'SAP_data': 'A30:A40',
            'workflow_data': 'A41:A49',
            'atomic_checks': 'A50:A70',
            'calculated_values' : 'A71:A97', 
            'results': 'A98:A102'}

TOR_no_SAP_match_conditionals = {'good': 'B98:OO101',
                'warning': 'B98:OO100',
                'error': 'B100:OO101'}
    
def save_xls(list_dfs, xls_path):
    with ExcelWriter(xls_path) as writer:
        for n, df in enumerate(list_dfs):
            df.to_excel(writer,'sheet%s' % n)
        writer.save()
        
def save_xls_dict(dict_df, xls_path):
    with ExcelWriter(xls_path) as writer:
        for key in dict_df:
            dict_df[key].to_excel(writer, key)
        writer.save()

def noaccent (s):
    s_no_accents = ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    return s_no_accents

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def days_between_dash(d1, d2):
    d1 = datetime.datetime.strptime(d1, "%d/%m/%Y")
    d2 = datetime.datetime.strptime(d2, "%d/%m/%Y")
    return abs((d2 - d1).days)

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return next_month - datetime.timedelta(days=next_month.day)

def findIdx_first(df, pattern, offset = True):
    """ Get the position of the first occurrence of the pattern in the df
        and return it as a tuple (row_index, col_index)
    """
    ret = df.apply(lambda x: x.str.contains(pattern)).values.nonzero()    
    if offset and len(ret[0]) > 0:
        ret = list(zip(*ret))[0]
        ret = ret[0]-2, ret[1]
        #this one gets the cell two cells under the heading specified in the pattern parameter
        #in the call for funds pdfs the relevant data is located two cells under the heading
        return ret
    else:
        return None if len(ret[0]) == 0 else list(zip(*ret))[0]

def getPageNumberofText (searchText, pdf_file):
    """Get the page number of the first occurrence of the searchText in the given pdf_file """
    fp = open(pdf_file, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    #print(type(retstr))
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for pageNumber, page in enumerate(PDFPage.get_pages(fp)):
        interpreter.process_page(page)
        data = retstr.getvalue()
        if searchText in data:
            return pageNumber
    return None

def parse_obj(lt_objs, searchText):
    """Parse the object list from a pdf file to find textboxes, and return the bounding box coordinates of the searchtext """
    # loop over the object list
    for obj in lt_objs:
        # if it's a textbox, print text and location
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            print ("%6d, %6d, %s" % (obj.bbox[0], obj.bbox[1], obj.get_text().replace('\n', '_')))
            if searchText in obj.get_text():
                return obj.bbox[1]
        # if it's a container, recurse
        elif isinstance(obj, pdfminer.layout.LTFigure):
            parse_obj(obj._objs, searchText)

def textbox_content_of_searchstring(lt_objs, searchText):
    """ Parse the object list from a pdf file to find textboxes, and return the full text box contents of the box containing the searchtext """
    # loop over the object list
    for obj in lt_objs:
        # if it's a textbox, print text and location
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            print ("%6d, %6d, %s" % (obj.bbox[0], obj.bbox[1], obj.get_text().replace('\n', '_')))
            if searchText in obj.get_text():
                return obj.get_text()
        # if it's a container, recurse
        elif isinstance(obj, pdfminer.layout.LTFigure):
            parse_obj(obj._objs, searchText)

def getCoordinatesofText (searchText, pdf_file):
    occurrence_list = []
    pageno = 0
    """Get the page numbers and coordinates of the searchText in the given pdf_file """
    fp = open(pdf_file, 'rb')
    rsrcmgr = PDFResourceManager()
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    rsrcmgr = PDFResourceManager()
    device = PDFDevice(rsrcmgr)
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    totalpages = resolve1(document.catalog['Pages'])['Count']

    for page in PDFPage.create_pages(document):
        pageno +=1

    # read the page into a layout object
        interpreter.process_page(page)
        layout = device.get_result()

    # extract text from this object
        coord = parse_obj(layout._objs, searchText)
        triplet_item = (pageno,totalpages, coord)
        if coord != None:
            occurrence_list.append(triplet_item)
        
    return occurrence_list

def getAllOccurencesofText (searchText, pdf_file):
    """Get all occurrences of the text in the pdf file, and return a list of X-coord, Y-coord, text and page number """
    occurrence_list = []
    fp = open(pdf_file, 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = PDFPage.get_pages(fp)

    for pageNumber, page in enumerate(pages):
        print('Processing next page...')
        print (pageNumber)
        interpreter.process_page(page)
        layout = device.get_result()
        for lobj in layout:
            if isinstance(lobj, LTTextBox):
                x, y, text = lobj.bbox[0], lobj.bbox[3], lobj.get_text()
                if searchText in text:
                    print('At %r is text: %s' % ((x, y), text))
                    quadruplet = (x, y, text, pageNumber)
                    occurrence_list.append(quadruplet)
    
    return occurrence_list



def query_ECB_forex_API(call_date, country='CH'):
    #currency check
    #queries ECB API for the last day of the month of the call date
    #it uses those days where there is no exchange rate qouted for EUR-CHF as a proxy for bank holidays
    #the default value for the country is CH, because the defaule forex rate is EUR-CHF
    #if the country is in the eurozone, it just returns 1
    #euro = True
    exchange_rate = 1
    
    if country not in eurozone_countries:
        #euro = False
        #if the call_date passed to the function is a datetime, just use that without conversion
        if str(type(call_date)) != "<class 'pandas._libs.tslibs.timestamps.Timestamp'>":
            try:
                date_forex = datetime.datetime.strptime(call_date, '%d/%m/%Y')
            except:
                date_forex = datetime.datetime.strptime(call_date, '%Y-%m-%d %H:%M:%S')
        else:
            date_forex = call_date
        last_day = last_day_of_month(date_forex)
        entrypoint = 'https://sdw-wsrest.ecb.europa.eu/service/' # Using protocol 'https'
        resource = 'data'           # The resource for data queries is always'data'
        flowRef ='EXR'              # Dataflow describing the data that needs to be returned, exchange rates in this case
        key = 'D.XXX.EUR.SP00.A'    # Defining the dimension values, explained below
        currentkey = key[0:2] + non_eurozone_currencies[country] + key[5:]
        print(currentkey)
        parameters = {
                'startPeriod':  datetime.datetime.strftime(date_forex, '%Y')+ '-' +  datetime.datetime.strftime(date_forex, '%m')+ '-01',  # Start date of the time series
                'endPeriod': last_day.strftime('%Y')+ '-' +  last_day.strftime('%m')+ '-' + last_day.strftime('%d')  # End date of the time series
                }
        request_url = entrypoint + resource + '/'+ flowRef + '/' + currentkey
        response = requests.get(request_url, params=parameters, headers={'Accept': 'text/csv'})
        ECB_df = pd.read_csv(io.StringIO(response.text))
        ECB_ts = ECB_df.filter(['TIME_PERIOD', 'OBS_VALUE'], axis=1)
        # 'TIME_PERIOD' was of type 'object' (as seen in df.info). Convert it to datetime first
        ECB_ts['TIME_PERIOD'] = pd.to_datetime(ECB_ts['TIME_PERIOD'])
        # Set 'TIME_PERIOD' to be the index
        ECB_ts = ECB_ts.set_index('TIME_PERIOD')
        # Print the last 5 rows to screen
        #ECB_ts.tail()
        print(ECB_ts.iloc[-2:-1]) #penultimate working day of the month (last but one)
        exchange_rate = float(ECB_ts.iloc[-2:-1].OBS_VALUE)

        #create a dictionary for returning the exchange rate info
    return exchange_rate


def subdelegation_check(df_subdelegation, person):
    """ Searches for a tokenized sentence in the subdelegation letters that contains the family name part of the user name """
    for index, subdelegation in df_subdelegation.iterrows():
        #print (index)
        #have to convert the strings into lists, because pandas cannot understand lists loaded from csv
        tokens = subdelegation['tokens'].lower().strip('[]').split(', ')
        tokens = [token.strip("\'") for token in tokens]
        sentences = subdelegation['sentences'].lower().strip('[]').split(', ')
        sentences = [sentence.strip("\'") for sentence in sentences]
        subdelegation_found = False
        try:
            subdelegation_text = ' '.join(tokens[[token[0:5] for token in tokens].index(person)-5:[token[0:5] for token in tokens].index(person)+5])
            #print(subdelegation_text)
            subdelegation_person = ' '.join(tokens[[token[0:5] for token in tokens].index(person)-1:[token[0:5] for token in tokens].index(person)+1])
            #print(subdelegation_person)
            subdelegation_found = True
            break
        except:
            pass
    if subdelegation_found:
        print('subdelegation_person: ', subdelegation_person)
        print('subdelegation_text: ', subdelegation_text)
    else:
        print('subdelegation not found')
    return(subdelegation_found, subdelegation_person, subdelegation_text)

def ECB_working_days_between_dates(start, end):
    '''
    Queries the ECB database for CHF/EUR qutoes between the two dates
    The proxy for working days is the length of the returned dataframe,
    e.g. how many days elapsed between the two days with quoted forex rates
    The inputs are two timestamps that are converted to string internally
    It returns an integer as length
    '''
    entrypoint = 'https://sdw-wsrest.ecb.europa.eu/service/' # Using protocol 'https'
    resource = 'data'           # The resource for data queries is always'data'
    flowRef ='EXR'              # Dataflow describing the data that needs to be returned, exchange rates in this case
    key = 'D.CHF.EUR.SP00.A'    # Defining the dimension values, explained below
    parameters = {
            #'startPeriod':  datetime.datetime.strftime(date_forex, '%Y')+ '-' +  datetime.datetime.strftime(date_forex, '%m')+ '-01',  # Start date of the time series
            #'endPeriod': last_day.strftime('%Y')+ '-' +  last_day.strftime('%m')+ '-' + last_day.strftime('%d')  # End date of the time series
            'startPeriod': str(start)[:-9],
            'endPeriod': str(end)[:-9]
            }
    request_url = entrypoint + resource + '/'+ flowRef + '/' + key
    response = requests.get(request_url, params=parameters, headers={'Accept': 'text/csv'})
    ECB_df = pd.read_csv(io.StringIO(response.text))
    return len(ECB_df)

def ECB_penultimate_working_day_of_month(date):
    #getting the penultimate working day of the month by proxy from ECB
    date_forex = datetime.datetime.strptime(date, '%d/%m/%Y')
    last_day = last_day_of_month(date_forex)
    entrypoint = 'https://sdw-wsrest.ecb.europa.eu/service/' # Using protocol 'https'
    resource = 'data'           # The resource for data queries is always'data'
    flowRef ='EXR'              # Dataflow describing the data that needs to be returned, exchange rates in this case
    key = 'D.CHF.EUR.SP00.A'    # Defining the dimension values, explained below
    parameters = {
            'startPeriod':  datetime.datetime.strftime(date_forex, '%Y')+ '-' +  datetime.datetime.strftime(date_forex, '%m')+ '-01',  # Start date of the time series
            'endPeriod': last_day.strftime('%Y')+ '-' +  last_day.strftime('%m')+ '-' + last_day.strftime('%d')  # End date of the time series
            #'endPeriod': forex_year + '-' + str(int(forex_month)+1) + '-01'
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
    return penultimate_working_day

        
def query_ECB_forex_API_exact_date(call_date, country='CH'):
    #currency check
    #queries ECB API for the exact date of the call date
    #euro = True
    exchange_rate = 1
    
    if country not in eurozone_countries:
        #euro = False
        #if the call_date passed to the function is a datetime, just use that without conversion
        if str(type(call_date)) != "<class 'pandas._libs.tslibs.timestamps.Timestamp'>":
            try:
                date_forex = datetime.datetime.strptime(call_date, '%d/%m/%Y')
            except:
                date_forex = datetime.datetime.strptime(call_date, '%Y-%m-%d %H:%M:%S')
        else:
            date_forex = call_date
        last_day = date_forex
        entrypoint = 'https://sdw-wsrest.ecb.europa.eu/service/' # Using protocol 'https'
        resource = 'data'           # The resource for data queries is always'data'
        flowRef ='EXR'              # Dataflow describing the data that needs to be returned, exchange rates in this case
        key = 'D.XXX.EUR.SP00.A'    # Defining the dimension values, explained below
        currentkey = key[0:2] + non_eurozone_currencies[country] + key[5:]
        print(currentkey)
        parameters = {
                'startPeriod':  datetime.datetime.strftime(date_forex, '%Y')+ '-' +  datetime.datetime.strftime(date_forex, '%m')+ '-01',  # Start date of the time series
                'endPeriod': last_day.strftime('%Y')+ '-' +  last_day.strftime('%m')+ '-' + last_day.strftime('%d')  # End date of the time series
                }
        request_url = entrypoint + resource + '/'+ flowRef + '/' + currentkey
        response = requests.get(request_url, params=parameters, headers={'Accept': 'text/csv'})
        ECB_df = pd.read_csv(io.StringIO(response.text))
        ECB_ts = ECB_df.filter(['TIME_PERIOD', 'OBS_VALUE'], axis=1)
        # 'TIME_PERIOD' was of type 'object' (as seen in df.info). Convert it to datetime first
        ECB_ts['TIME_PERIOD'] = pd.to_datetime(ECB_ts['TIME_PERIOD'])
        # Set 'TIME_PERIOD' to be the index
        ECB_ts = ECB_ts.set_index('TIME_PERIOD')
        # Print the last 5 rows to screen
        #ECB_ts.tail()
        print(ECB_ts.iloc[-1]) #penultimate working day of the month (last but one)
        exchange_rate = float(ECB_ts.iloc[-1].OBS_VALUE)

        #create a dictionary for returning the exchange rate info
    return exchange_rate

def get_Ares_date(pdf_file):
    """Extracts the Ares date from a pdf file, looking for a textbox containing Ares, splitting the text and interpreting the date """

#    call_for_funds_file = 'C://Users//admin//Dropbox//Ch5_GUI_demo_revenue//ch5_automation_sample_documents//Call for Funds 2019//06.pdf'
#    call_for_funds_file = '//home//vargaz//Dropbox//Ch5_GUI_demo_revenue//ch5_automation_sample_documents//Call for Funds 2019//12.pdf'
#    pdf_file = 'c://Users//admin//Dropbox//Ch5_GUI_demo_revenue//TOR//data//SI2.520865//SI2.520865-1.pdf'   

    #pdf_file = './pdf/9. September.pdf'
    fp = open(pdf_file, 'rb')
    rsrcmgr = PDFResourceManager()
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
        #need to check the types of pdf, an OCR function could come here
    device = PDFDevice(rsrcmgr)
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    #extract the stuff from the first page only, because the date is there
    pages = PDFPage.create_pages(document)
    #hack to get the first item from a generator -> make it a list and grab the first list item
    page = list(pages)[0]
    interpreter.process_page(page)
    #fake_file_handle = io.StringIO()
    #converter = TextConverter(rsrcmgr, fake_file_handle)
    #text = fake_file_handle.getvalue()
    layout = device.get_result()
    call_date = textbox_content_of_searchstring(layout._objs, 'Ares')
    fp.close()
    try:
        call_date = call_date.split('-')[1].strip()
        return datetime.datetime.strptime(call_date, '%d/%m/%Y')
    except:
        return pd.NaT

def get_esignature_date(pdf_file):
    """Extracts the e-signature date from a pdf file, looking for a textbox containing 'Electronically signed on ', splitting the text and interpreting the date """

#    call_for_funds_file = 'C://Users//admin//Dropbox//Ch5_GUI_demo_revenue//ch5_automation_sample_documents//Call for Funds 2019//06.pdf'
#    call_for_funds_file = '//home//vargaz//Dropbox//Ch5_GUI_demo_revenue//ch5_automation_sample_documents//Call for Funds 2019//12.pdf'
#    pdf_file = 'c://Users//admin//Dropbox//Ch5_GUI_demo_revenue//TOR//data//SI2.520865//SI2.520865-1.pdf'   

    #pdf_file = './pdf/9. September.pdf'
    fp = open(pdf_file, 'rb')
    rsrcmgr = PDFResourceManager()
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
        #need to check the types of pdf, an OCR function could come here
    device = PDFDevice(rsrcmgr)
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    #extract the stuff from the first page only, because the date is there
    pages = PDFPage.create_pages(document)
    #hack to get the first item from a generator -> make it a list and grab the first list item
    page = list(pages)[-1]
    interpreter.process_page(page)
    #fake_file_handle = io.StringIO()
    #converter = TextConverter(rsrcmgr, fake_file_handle)
    #text = fake_file_handle.getvalue()
    layout = device.get_result()
    #for CFF files after June 2020, the Commission has changed the way they are signed, and the get_Ares_date function doesn't work anymore
    call_date = textbox_content_of_searchstring(layout._objs, 'Electronically signed on')
    fp.close()
    try:
        call_date = call_date.split('Electronically signed on')[1].strip()
        return datetime.datetime.strptime(call_date[0:10], '%d/%m/%Y')
    except:
        return pd.NaT

def get_cff_pdf_date(pdf_file):
    """Extracts the cff month from a pdf file, looking for a textbox containing '1st WORKING DAY OF ' from page9, splitting the text and interpreting the date """

#    call_for_funds_file = 'C://Users//admin//Dropbox//Ch5_GUI_demo_revenue//ch5_automation_sample_documents//Call for Funds 2019//06.pdf'
#    call_for_funds_file = '//home//vargaz//Dropbox//Ch5_GUI_demo_revenue//ch5_automation_sample_documents//Call for Funds 2019//12.pdf'
#    pdf_file = 'c://Users//admin//Dropbox//Ch5_GUI_demo_revenue//TOR//data//SI2.520865//SI2.520865-1.pdf'   

    #pdf_file = './pdf/9. September.pdf'
    #pdf_file = './pdf/Rp20_EN_appel_02-2020-n.323801.pdf'
    
    page_number = getPageNumberofText('1st WORKING DAY OF ', pdf_file)
    
    fp = open(pdf_file, 'rb')
    rsrcmgr = PDFResourceManager()
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
        #need to check the types of pdf, an OCR function could come here
    device = PDFDevice(rsrcmgr)
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    #extract the stuff from the first page only, because the date is there
    pages = PDFPage.create_pages(document)
    #hack to get the first item from a generator -> make it a list and grab the first list item
    page = list(pages)[page_number]
    interpreter.process_page(page)
    #fake_file_handle = io.StringIO()
    #converter = TextConverter(rsrcmgr, fake_file_handle)
    #text = fake_file_handle.getvalue()
    layout = device.get_result()
    #for CFF files after June 2020, the Commission has changed the way they are signed, and the get_Ares_date function doesn't work anymore
    call_date = textbox_content_of_searchstring(layout._objs, '1st WORKING DAY OF ')
    fp.close()
    try:
        call_date = call_date.split('1st WORKING DAY OF ')[1].strip()
        return datetime.datetime.strptime(call_date[0:7], '%m/%Y')
    except:
        return pd.NaT


def ECB_first_working_day_after_19th_of_month(date):
    #getting the "first working day after the 19th of the second month following the month during which the entitlements were established"
    #date_forex = datetime.datetime.strptime(date, '%d/%m/%Y')
        
    date_forex = date
    #last_day = last_day_of_month(date_forex)
    entrypoint = 'https://sdw-wsrest.ecb.europa.eu/service/' # Using protocol 'https'
    resource = 'data'           # The resource for data queries is always'data'
    flowRef ='EXR'              # Dataflow describing the data that needs to be returned, exchange rates in this case
    key = 'D.CHF.EUR.SP00.A'    # Defining the dimension values, explained below
    parameters = {
            'startPeriod':  datetime.datetime.strftime(date_forex, '%Y')+ '-' +  datetime.datetime.strftime(date_forex, '%m')+ '-01',  # Start date of the time series
            'endPeriod': date_forex.strftime('%Y')+ '-' +  date_forex.strftime('%m')+ '-' + '28'  # End date of the time series
            #'endPeriod': forex_year + '-' + str(int(forex_month)+1) + '-01'
            }
    request_url = entrypoint + resource + '/'+ flowRef + '/' + key
    response = requests.get(request_url, params=parameters, headers={'Accept': 'text/csv'})
    ECB_df = pd.read_csv(io.StringIO(response.text))
    ECB_ts = ECB_df.filter(['TIME_PERIOD', 'OBS_VALUE'], axis=1)
    # 'TIME_PERIOD' was of type 'object' (as seen in df.info). Convert it to datetime first
    ECB_ts['TIME_PERIOD'] = pd.to_datetime(ECB_ts['TIME_PERIOD'])
    # Set 'TIME_PERIOD' to be the index
    #first_working_day_after_19th = ECB_ts.iloc[-1]['TIME_PERIOD'] #first working day after the 19th of the month (20th minus one)
    
    datelist = (list (ECB_ts['TIME_PERIOD'].apply(lambda x: x.day)))
    print(datelist)
    first_working_day_after_19th = [day for day in datelist if day-20 >=0][0]
    first_working_day_after_19th_datetime =  datetime.date(date_forex.year, date_forex.month, first_working_day_after_19th )
    print(first_working_day_after_19th_datetime)
    
    return first_working_day_after_19th_datetime


def round_up(n, decimals=0): 
    multiplier = 10 ** decimals 
    return math.ceil(n * multiplier) / multiplier

#searching for different possible valid combinations of the amounts in the TOR statement text
def searchAmount(df, what_col='justification_amounts', where_col='newtext'):

    rowlist = []
    hitlist = []
    found_value = []

    for index, row in df.iterrows():
    
        if str(row[what_col]) in row[where_col]:
            print("Full match: ", row.name)
            rowlist.append(row)
            hitlist.append('A')
            found_value.append(str(row[what_col]))
                
        elif str(row[what_col]).replace('.', ',') in row[where_col].replace('.',' '):
            print("Replace full match: ", row.name)
            rowlist.append(row)
            hitlist.append('E')
            found_value.append(str(row[what_col]).replace('.', ','))
    
        elif str(row[what_col]) in row[where_col].replace('.',''):
            print("Replace full match: ", row.name)
            rowlist.append(row)
            hitlist.append('IT')
            found_value.append(str(row[what_col]))
            
            #IT
        elif str(format(row[what_col], ',').replace(',', '.'))[0:4]+str(format(row[what_col], ',').replace('.', ','))[4:] in row[where_col]:
            print("Replace full match: ", row.name)
            rowlist.append(row)
            hitlist.append('IT')
            found_value.append(str(row[what_col])) 
    
        #IT HACK
        elif str(format(row[what_col], ',').replace(',', '.'))[0:4]+str(format(row[what_col], ',').replace('.', ', '))[4:] in row[where_col]:
            #print("Replace full match: ", row.name)
            rowlist.append(row)
            hitlist.append('IT')
            found_value.append(str(row[what_col]))
    
        #IT
        elif str(format(row[what_col], ',').replace(',', '.'))[0:4]+str(format(row[what_col], ',').replace(',', '.'))[4:8]+str(format(row[what_col], ',').replace('.', ','))[8:] in row[where_col]:
            print("Replace full match: ", row.name)
            rowlist.append(row)
            hitlist.append('IT')
            found_value.append(str(row[what_col])) 
    
        #IT HACK
        elif str(format(row[what_col], ',').replace(',', '.'))[0:4]+str(format(row[what_col], ',').replace(',', '.'))[4:8]+str(format(row[what_col], ',').replace('.', ', '))[8:] in row[where_col]:
            print("Replace full match: ", row.name)
            rowlist.append(row)
            hitlist.append('IT')
            found_value.append(str(row[what_col]))
    
        elif str(row[what_col]) in row[where_col].replace(' ',''):
            print("Replace full match: ", row.name)
            rowlist.append(row)
            hitlist.append('HU')
            found_value.append(str(row[what_col]))
    
        elif str(format(row[what_col], ',').replace(',', ' ').replace('.', ',')) in row[where_col].replace('.',' '):
            print("Replace full match: ", row.name)
            rowlist.append(row)
            hitlist.append('F')
            found_value.append(str(format(row[what_col], ',').replace(',', ' ').replace('.', ',')))
    
        elif str(round_up(row[what_col]*1.25,2)) in row[where_col].replace(',','.').replace(' ', ''):
            print("Full match (80%), local currency: ", row.name)
            rowlist.append(row)
            hitlist.append('K')
            found_value.append(str(round_up(row[what_col]*1.25,2)))
                    
        #i have to make it round .5 upwards, otherwise it doesn't find stuff
        elif str(round_up(row[what_col]/0.75,2)) in row[where_col]:
            print("Full match (75% of amount), local currency: ", row.name)
            rowlist.append(row)
            hitlist.append('N')
            found_value.append(str(round_up(row[what_col]/0.75,2)))
        
        elif str(round_up(row[what_col]/0.75,2)) in row[where_col].replace(',','.').replace(' ', ''):
            print("Full match (75% of amount), local currency: ", row.name)
            rowlist.append(row)
            hitlist.append('O')
            found_value.append(str(round_up(row[what_col]/0.75,2)))
    
        elif str(round_up(row[what_col]/0.75,2)) in row[where_col].replace('.', '').replace(',', '.'):
            print("Token match (75% of amount, round up), local currency: ", row.name)
            rowlist.append(row)
            hitlist.append('P')
            found_value.append(str(round_up(row[what_col]/0.75,2)))
            
        elif str(round(row[what_col]/0.75,2)) in row[where_col].replace('.', '').replace(',', '.'):
            print("Token match (75% of amount, round down), local currency: ", row.name)
            rowlist.append(row)
            hitlist.append('Q')
            found_value.append(str(round(row[what_col]/0.75,2)))
    
        elif str(format(round(row[what_col]/0.75,2), ',')).replace(',', ' ') in row[where_col]:
            print("Token match (75% of amount, round down), local currency: ", row.name)
            rowlist.append(row)
            hitlist.append('QQ')
            found_value.append(str(format(round(row[what_col]/0.75,2), ',')).replace(',', ' '))
            
        elif str(format(round(row[what_col]/0.8,2), ',')).replace(',', ' ') in row[where_col]:
            print("Token match (80% of amount, round down), local currency: ", row.name)
            rowlist.append(row)
            hitlist.append('QQQ')
            found_value.append(str(format(round(row[what_col]/0.8,2), ',')).replace(',', ' '))
    
        elif str(round(row[what_col]/0.75,2)-0.01) in row[where_col].replace('.', '').replace(',', '.'):
            print("Token match (75% of amount, round even more down), local currency: ", row.name)
            rowlist.append(row)
            hitlist.append('R')
            found_value.append(str(round(row[what_col]/0.75,2)-0.01))
            
        elif str(round(row[what_col]/0.8,2)) in row[where_col]:
            print("Full match (80% of amount, round down), local currency: ", row.name)
            rowlist.append(row)
            hitlist.append('T')
            found_value.append(str(round(row[what_col]/0.8,2)))
            
        elif str(round(row[what_col]/0.8,2)-0.01) in row[where_col]:
            print("Full match (80% of amount, round even more down), local currency: ", row.name)
            rowlist.append(row)
            hitlist.append('U')
            found_value.append(str(round(row[what_col]/0.8,2)-0.01))
    
        elif str(round(row[what_col]/0.8,2)-0.01) in row[where_col].replace('.', '').replace(',', '.'):
            print("Full match (80% of amount, round even more down), local currency: ", row.name)
            rowlist.append(row)
            hitlist.append('V')
            found_value.append(str(round(row[what_col]/0.8,2)-0.01))
        
        elif str(row[what_col]) in row[where_col].replace(',',''):
            print("Replace token match, local currency: ", row.name)
            rowlist.append(row)
            hitlist.append('AA')
            found_value.append(str(row[what_col]))        
            
        elif str(row[what_col]).replace('.','') in row[where_col].replace(',','.').replace('.',''):
            if str(row[what_col]).replace('.','') !=  '00':
                print("Replace token match3, local currency: ", row.name)
                rowlist.append(row)
                hitlist.append('EE')
                found_value.append(str(row[what_col]).replace('.',''))
            else:
                print("No match: ", row.name)
                rowlist.append(row)
                hitlist.append(np.nan)
                found_value.append(np.nan)           
        else:
            print("No match: ", row.name)
            rowlist.append(row)
            hitlist.append(np.nan)
            found_value.append(np.nan)

    return     rowlist, hitlist, found_value


def searchAmountInColumns(df, what_col, where_col_list):
    """
    Takes a dataframe, the search column that contains the value to be searched, and a list of columns
    that contain the columns where the value will be searched. The order of search is determined by
    the order of the list, the first hit from the column list is taken for each row
    Returns a dataframe containing the matches and match types
    """

    if len(where_col_list) < 1 or what_col == None:
        raise Exception("Please specify one column for the search value and a list for search columns") 
    
    df_search_results = pd.DataFrame()

    for where_col in where_col_list:
        _, hitlist, found_value = searchAmount(df, what_col=what_col, where_col=where_col)
        
        df_search_results[str('match_type_'+where_col)] = hitlist
        df_search_results[str('match_amount'+where_col)] = found_value
           
    df_search_results['matches'] = np.nan
    for colname in [x for x in df_search_results.columns if "amount" in x]:
        df_search_results['matches']  = df_search_results['matches'].fillna(df_search_results[colname])
    df_search_results['match_types'] = np.nan
    for colname in [x for x in df_search_results.columns if "type" in x and "types" not in x]:
        df_search_results['match_types']  = df_search_results['match_types'].fillna(df_search_results[colname])
        

    return df_search_results[['matches', 'match_types']]

def searchAmountInColumns2List(df, what_col_list, where_col_list):
    """
    Takes a dataframe, a list of search columns that contain the columns containing value to be searched, and a list of columns
    that contain the columns where the value will be searched. The order of search is determined by
    the order of the list, the first hit from the column list is taken for each row
    Returns a dataframe containing the matches and match types, and the what+where colnames
    
    """

    if len(where_col_list) < 1 or len(what_col_list) < 1 :
        raise Exception("Please specify a list for each search column") 
    
    df_search_results = pd.DataFrame()

    for what_col in what_col_list:

        for where_col in where_col_list:
            _, hitlist, found_value = searchAmount(df, what_col=what_col, where_col=where_col)
            
            df_search_results[str('match_type_'+what_col+'_'+where_col)] = hitlist
            df_search_results[str('match_amount_'+what_col+'_'+where_col)] = found_value
           
    df_search_results['matches'] = np.nan
    for colname in [x for x in df_search_results.columns if "amount" in x]:
        df_search_results['matches']  = df_search_results['matches'].fillna(df_search_results[colname])
    df_search_results['match_types'] = np.nan
    for colname in [x for x in df_search_results.columns if "type" in x and "types" not in x]:
        df_search_results['match_types']  = df_search_results['match_types'].fillna(df_search_results[colname])
        

    #return df_search_results[['matches', 'match_types']]
    return df_search_results


def getJustificationAmounts(df, column='RO Justification'):
    """
    
    Takes a dataframe column of text with amounts, and uses the price parser library
    to get the amounts out.
    If the currency is not none, the amount is a float and it's bigger than 3 it puts
    it into a list, if it doesn't meet the conditions, then a None is added.
    Returns the df with a new column with the list of justification amounts found
    in the given column
    

    """

    amounts_per_row = []
    for i, row in df.iterrows():
        sentences_curr = sent_tokenize(row[column])
        found_amounts = []
        for item in sentences_curr:
            found_amount = Price.fromstring(item)
            if found_amount.currency != None and found_amount.amount_float != None and found_amount.amount_float > 3:
                found_amounts.append(found_amount.amount_float)
                print(found_amount)
        amounts_per_row.append(found_amounts)
    
    df['justification_amounts'] = amounts_per_row
    
    return(df)

def rename_dupes_with_number(x, col):
    """ takes a dataframe and a column name, adds occurrence number to duplicate values in the column as a suffix and return a suffixed list"""
    counter = x.groupby(col).cumcount().add(1)
    suffix = [str('_dup_'+str(x)) if  x >1 else '' for x in counter]
    suffixed_list = list( map(concat, list(x[col]), suffix) )
    return suffixed_list


def GetDatesFromDF(df):
    """Takes a dataframe and tries to extract dates from the hardcoded columns.
    Each hardcoded columns have different rules, based on the patterns in the data observed.
    It is mostly heuristics.
    Returns a dataframe with various extracted and calculated dates related to the transactions in each row.
    """
    establishment_date_list = []
    transfer_date_list = []
    previous_month_list = []
    penultimate_day_of_previous_month_list = []
    rate_penultimate_day_list = []
    rate_posting_day_list = []
    rate_cashing_day_list = []
    
    penultimate_day_of_previous_month_SAP_list = []
    previous_month_SAP_list = []
    rate_penultimate_day_SAP_list = []   
    
    #datestring = ''
    for index, row in df.iterrows():
        #getting the dates and the exchange rates
        #date of establishment
        try:
            datestring = row['RO Contract or File nr'].replace(' ', '')[row['RO Contract or File nr'].replace(' ', '').index('MOISDE')+6:row['RO Contract or File nr'].replace(' ', '').index('MOISDE')+13]
            if datestring[3:5] != '20':
                datestring = datestring[0:3] + '20' + datestring[3:5]
            datestring = '01/' + datestring
            
            datestring = datestring.replace('20ET', '2020')
            
            if datestring[5] != '/':
                datestring = pd.NaT
            
            establishment_date_list.append(datestring)
        except:
            establishment_date_list.append(pd.NaT)
        #establishment_date_list = [x.replace('20ET', '2020') for x in establishment_date_list]
        #date of transfer
        try:
            datestring = row['RO Contract or File nr'].replace(' ', '')[row['RO Contract or File nr'].replace(' ', '').index('ESEN')+4:row['RO Contract or File nr'].replace(' ', '').index('ESEN')+11]
            if datestring[3:5] != '20':
                datestring = datestring[0:3] + '20' + datestring[3:5]
            datestring = '01/' + datestring
            
            datestring = datestring.replace('20-R', '2020')
            
            if datestring[5] != '/':
                datestring = pd.NaT
            transfer_date_list.append(datestring)
        except:
            transfer_date_list.append(pd.NaT)
        #first day of previous month, based on the date of transfer
        #either from the transfer date, or if can't find it, then from the RO header cashing date
    
    
        datestring = transfer_date_list[index]
        if not pd.isnull(datestring):
            if datestring[3:5] == '01':
                previous_month = '01/12/' + str(int(datestring[6:10])-1)
            else:
                if int(datestring[3:5])-1 < 10:
                    month = '0' + str(int(datestring[3:5])-1)
                else:
                    month = str(int(datestring[3:5])-1)
                previous_month = '01/' + month + datestring[5:10]
        else:
            if row['RO Cashing Cashed Date'].month-1 <0:
                previous_month = '01/12/' + str(row['RO Cashing Cashed Date'].year-1)
            else:
                previous_month = '01/'+str(row['RO Cashing Cashed Date'].month-1)+'/'+str(row['RO Cashing Cashed Date'].year)
        previous_month_list.append(previous_month)
    
        try:
            penultimate_day_of_previous_month = ECB_penultimate_working_day_of_month(previous_month)
            penultimate_day_of_previous_month_list.append(penultimate_day_of_previous_month)
        except:
            penultimate_day_of_previous_month_list.append(pd.NaT)
        try:
            rate_penultimate_day = query_ECB_forex_API(penultimate_day_of_previous_month, row['LE Country Code'])
            rate_penultimate_day_list.append(rate_penultimate_day)
        except:
            rate_penultimate_day_list.append(np.nan)
        
        cashing_day = str(row['RO Cashing Cashed Date'].day) + '/' + str(row['RO Cashing Cashed Date'].month) + '/' +str(row['RO Cashing Cashed Date'].year)
        try:
            rate_cashing_day  = query_ECB_forex_API_exact_date(cashing_day, row['LE Country Code'])
            rate_cashing_day_list.append(rate_cashing_day)
        except:
            rate_cashing_day_list.append(np.nan)
  
        posting_day = str(row['Posting Date'].day) + '/' + str(row['Posting Date'].month) + '/' +str(row['Posting Date'].year)
        try:
            rate_posting_day = query_ECB_forex_API_exact_date(posting_day, row['LE Country Code'])
            rate_posting_day_list.append(rate_posting_day)
        except:
            rate_posting_day_list.append(np.nan)   
        
        
        #penultimate rate for previous month based on SAP posting
        if row['Posting Date'].month-1 <0:
            previous_month_SAP = '01/12/' + str(row['Posting Date'].year-1)
        else:
            previous_month_SAP = '01/'+str(row['Posting Date'].month-1)+'/'+str(row['Posting Date'].year)
        previous_month_SAP_list.append(previous_month_SAP)
    
        try:
            penultimate_day_of_previous_month_SAP = ECB_penultimate_working_day_of_month(previous_month_SAP)
            penultimate_day_of_previous_month_SAP_list.append(penultimate_day_of_previous_month_SAP)
        except:
            penultimate_day_of_previous_month_SAP_list.append(pd.NaT)
        try:
            rate_penultimate_day_SAP = query_ECB_forex_API(penultimate_day_of_previous_month_SAP, row['LE Country Code'])
            rate_penultimate_day_SAP_list.append(rate_penultimate_day_SAP)
        except:
            rate_penultimate_day_SAP_list.append(np.nan)      
        
        
        
        df_dates = pd.DataFrame()
        df_dates['establishment date'] = establishment_date_list
        df_dates['transfer date'] = transfer_date_list
        df_dates['previous month'] = previous_month_list
        df_dates['penultimate day'] = penultimate_day_of_previous_month_list
        df_dates['penultimate rate'] = rate_penultimate_day_list
        df_dates['posting rate'] = rate_posting_day_list
        df_dates['cashing rate'] = rate_cashing_day_list
        
        df_dates['previous month_SAP'] = previous_month_SAP_list
        df_dates['penultimate day_SAP'] = penultimate_day_of_previous_month_SAP_list
        df_dates['penultimate rate_SAP'] = rate_penultimate_day_SAP_list       
        
    return df_dates


def make_hyperlink(value):
    "creates a clickable Excel hyperlink from the file path so that it could be displayed from Excel"
    #url = ""
    #return '=HYPERLINK("%s", "%s")' % (url.format(value), value)
    return '=HYPERLINK("%s", "%s")' % (value, value)

#1: Date of submission by MS:  ARES registration date?
#the audit team said it is not necessary, but then I don't know how we else we could get the submission data
def GetAresDates(df):
    """ Takes a dataframe and then extracts the Ares date from each file in the 'filename' column from the df.
    Return a dataframe with the extracted date and the regex extracted date from the OCRd text"""
    ares_df = pd.DataFrame()
    ares_list = []    
    
    for index, row in df.iterrows():
        print('index: ', index)
        try:
            filename = row['filename']
            #filename = '.'+filename.split('c:/Users/admin/Dropbox/Ch5_GUI_demo_revenue')[1]
            #filename = filename.replace('\\', '/')
            ares_date = get_Ares_date(filename)
        except:
            ares_date = pd.NaT
        print('ares date: ', ares_date)
        ares_list.append(ares_date)
    ares_df['ares_date'] = ares_list
    
    
    ares_regex_list = [pd.NaT] * len(df)
    for i, row in df.iterrows():
        print (i)
        if 'Ares' in row['text_extract'] or '4re5' in row['text_extract'] or '4r5' in row['text_extract']:
            #print(row['text_extract'])
            #regex search to compensate for typical OCR errors
            search_regex = re.compile("(Ares|4re5|4r5)\s?[(]\d\d\d\d[)]\s?\d\d\d\d\d\d\d\s?(-|of)\s?(\d\d[/]\d\d?[/]\d\d\d\d)", re.IGNORECASE)
            matchgroups = re.findall(search_regex, row['text_extract'])
            #third match group of the first match
            try:
                ares_date_regex = matchgroups[0][2]
                print(ares_date_regex)
                print(matchgroups)
            except:
                ares_date_regex =  pd.NaT
            ares_regex_list[i] = (ares_date_regex)
    
    ares_df['ares_regex_date'] = ares_regex_list     
    ares_df['ares_regex_date'] = ares_df['ares_regex_date'].apply(lambda x: x if str(x) == 'NaT' else datetime.datetime.strptime(x, '%d/%m/%Y'))

    return(ares_df)

def GetWorkFlowData(df, df_recovery_extract_workflow, df_subdelegation):
    """Extracts workflow data in a structured format from the workflow table of the recovery order extract file """
    authorisation_date_series = []
    authorising_officer_series = []
    processing_days_series = []
    subdelegation_found_series = []
    subdelegation_person_series = []
    subdelegation_text_series = []
    
    
    df_workflow = pd.DataFrame()
    for index, row in df.iterrows():

        try:
            authorising_officer_series.append(df_recovery_extract_workflow[(df_recovery_extract_workflow['RO Local Key']==row['RO Local Key_x']) & (df_recovery_extract_workflow['Workflow Step Description']=='AUTHORISING OFFICER')]['Workflow Person Id'].iloc[0])
            authorisation_date_series.append(df_recovery_extract_workflow[(df_recovery_extract_workflow['RO Local Key']==row['RO Local Key_x']) & (df_recovery_extract_workflow['Workflow Step Description']=='AUTHORISING OFFICER')]['Workflow Action Date'].iloc[0])
        except: #some TOR stuff doesn't seem to have it, that's why the exception
            try:
                #the column name is different for VAT/GNI
                authorising_officer_series.append(df_recovery_extract_workflow[(df_recovery_extract_workflow['RO Local Key']==row['RO Local Key']) & (df_recovery_extract_workflow['Workflow Step Description']=='AUTHORISING OFFICER')]['Workflow Person Id'].iloc[0])
                authorisation_date_series.append(df_recovery_extract_workflow[(df_recovery_extract_workflow['RO Local Key']==row['RO Local Key']) & (df_recovery_extract_workflow['Workflow Step Description']=='AUTHORISING OFFICER')]['Workflow Action Date'].iloc[0])
            except:      
                authorising_officer_series.append(None)
                authorisation_date_series.append(pd.NaT)

        
        try: #Some TOR transactions don't have authorisation it seems? or error? need to check
            #elapsed_days = df[(df['RO Local Key']==index) & (df['Workflow Step Description']=='AUTHORISING OFFICER')]['Workflow Action Date'].iloc[0] - df[(df['RO Local Key']==index) & (df['Workflow Step Description']=='INITIATING AGENT (first)')]['Workflow Action Date'].iloc[0] 
            elapsed_days = df_recovery_extract_workflow[(df_recovery_extract_workflow['RO Local Key']==row['RO Local Key_x']) & (df_recovery_extract_workflow['Workflow Step Description']=='AUTHORISING OFFICER')]['Workflow Action Date'].iloc[0] - df_recovery_extract_workflow[(df_recovery_extract_workflow['RO Local Key']==row['RO Local Key_x']) & (df_recovery_extract_workflow['Workflow Step Description']=='INITIATING AGENT (first)')]['Workflow Action Date'].iloc[0] 
            processing_days_series.append(elapsed_days)
        except:
            try:
                #the column name is different for VAT/GNI
                elapsed_days = df_recovery_extract_workflow[(df_recovery_extract_workflow['RO Local Key']==row['RO Local Key']) & (df_recovery_extract_workflow['Workflow Step Description']=='AUTHORISING OFFICER')]['Workflow Action Date'].iloc[0] - df_recovery_extract_workflow[(df_recovery_extract_workflow['RO Local Key']==row['RO Local Key']) & (df_recovery_extract_workflow['Workflow Step Description']=='INITIATING AGENT (first)')]['Workflow Action Date'].iloc[0] 
                processing_days_series.append(elapsed_days)               
            except:
                processing_days_series.append(pd.NaT)
            
        try:
            subdelegation_found, subdelegation_person, subdelegation_text = subdelegation_check(df_subdelegation, authorising_officer_series[-1][:-2].lower())
            subdelegation_found_series.append(subdelegation_found)
            subdelegation_person_series.append(subdelegation_person)
            subdelegation_text_series.append(subdelegation_text)
        except:
            subdelegation_found_series.append(None)
            subdelegation_person_series.append(None)
            subdelegation_text_series.append(None)
    
    df_workflow['authorisation_date'] = authorisation_date_series
    df_workflow['authorising_officer'] = authorising_officer_series
    df_workflow['processing_days'] =  processing_days_series
    df_workflow['subdelegation_found'] = subdelegation_found_series
    df_workflow['subdelegation_person'] = subdelegation_person_series
    df_workflow['subdelegation_person'] = df_workflow['subdelegation_person'].str.title()
    df_workflow['subdelegation_text'] = subdelegation_text_series
    
    return df_workflow

def CalculatePaymentDeadline(from_date):
    try: #adding two months to the date            
        establishment_date  = datetime.datetime.strptime(from_date, '%d/%m/%Y')    
        if establishment_date.month + 2 > 12:
            month = establishment_date.month - 10
            year = establishment_date.year + 1
            day = establishment_date.day
            query_date = datetime.date(year, month, day)
        else:
            month = establishment_date.month +2
            year = establishment_date.year
            day = establishment_date.day
            query_date = datetime.date(year, month, day)
        payment_deadline = ECB_first_working_day_after_19th_of_month(query_date)
    except:
        payment_deadline  = pd.NaT
    
    return payment_deadline

def get_Exploded_Columns(df, explosion_col='justification_matches', index_col='RO Local Key_x'):
    #df= df_check7[['RO Local Key_x', 'RO Position Local Key', 'filename']]
    
    d = defaultdict(count)
    
    i, r = pd.factorize(df[index_col])
    j = np.array([next(d[x]) for x in i])
    
    n, m = len(r), j.max() + 1
    
    b = np.empty((n, m), dtype=np.object)
    b[i, j] = df[explosion_col]
    
    d1 = pd.DataFrame(r.tolist(), columns=[index_col])
    #pack the number of exploded columns into column names with a suffix
    d2 = pd.DataFrame(b, columns=[str(explosion_col+'_SupportingDoc'+str(x+1)) for x in range(m)])    
    return d1.join(d2)

def add_Excel_formattting (writerobject, sections, conditionals, sheetname, transaction_type='GNI/VAT'):
    """
    

    Parameters
    ----------
    writerobject : the opened xlsxwriter object passed from the main script, containing the unformatted dataframe

    sections : a dictionary containing the sections of the A column to be formatted with different colours

    conditionals : a dictionary containing the Excel conditional formatting rules for all good, warning and error

    sheetname : the name of the worksheet where the formatted table is to be saved

    Returns
    -------
    writer : the modified xlsxwriter object containing the formatting.
    
    comment: it's a bit confusing, because even though I make a copy of the xlsxwriter object, it seems that modifying
    the copy has side-effects, the modifications are written immediately, so actually I am not sure that I have return
    anything here

    """
    writer = writerobject #I make a copy and work on the copy, just in case
    workbook  = writer.book
    worksheet = writer.sheets[sheetname]
    
    #freeze top row and left column
    worksheet.freeze_panes(1, 1)
    
    #set bold and border
    index_col_format = workbook.add_format({
        'bold': True,
        'border': 1})
    
    general_format = workbook.add_format({
        'bold': False,
        'text_wrap': True})
    
    green_background = workbook.add_format({
        'bg_color': '#90ee90'})
    
    light_blue_background = workbook.add_format({
        'bg_color': '#87cfeb'})
    
    light_brown_background = workbook.add_format({
        'bg_color': '#deb887'})
    
    light_pink_background = workbook.add_format({
        'bg_color': '#ffb6c1'})
    
    light_gray_background = workbook.add_format({
        'bg_color': '#c0c0c0'})
    
    lighter_blue_background = workbook.add_format({
        'bg_color': '#87cee8'})
    
    lighter_green_background = workbook.add_format({
        'bg_color': '#ccffcc'})
    
    risk_and_warning = workbook.add_format({
        'bg_color': '#fff2cc'})
    
    all_good = workbook.add_format({
        'bg_color': '#c6efce'})
    
    error = workbook.add_format({
        'bg_color': '#f8cbad'})
    
    #formatting index column and the other columns
    if transaction_type == 'VAT/GNI':
        worksheet.set_column('A:A', 56, index_col_format)
    else:
        worksheet.set_column('A:A', 71, index_col_format)
        
    worksheet.set_column('B:OO', 40, general_format)
    
    
    #we need to use conditional formatting, we can't change the format of existing cells
    worksheet.conditional_format(sections['RO_data'], {'type': 'cell',
                                               'criteria' : '<>', 
                                               'value' : '123',
                                               'format' : green_background})
    if transaction_type != 'TOR_no_SAP_match':
        worksheet.conditional_format(sections['CFF_data'], {'type': 'cell',
                                                   'criteria' : '<>', 
                                                   'value' : '123',
                                                   'format' : light_blue_background})
    

    worksheet.conditional_format(sections['SAP_data'], {'type': 'cell',
                                               'criteria' : '<>', 
                                               'value' : '123',
                                               'format' : light_brown_background})
    
    worksheet.conditional_format(sections['workflow_data'], {'type': 'cell',
                                               'criteria' : '<>', 
                                               'value' : '123',
                                               'format' : light_pink_background})
    
    
    worksheet.conditional_format(sections['atomic_checks'], {'type': 'cell',
                                               'criteria' : '<>', 
                                               'value' : '123',
                                               'format' : light_gray_background})
    
    worksheet.conditional_format(sections['calculated_values'], {'type': 'cell',
                                               'criteria' : '<>', 
                                               'value' : '123',
                                               'format' : lighter_blue_background})
    
    worksheet.conditional_format(sections['results'], {'type': 'cell',
                                               'criteria' : '<>', 
                                               'value' : '123',
                                               'format' : lighter_green_background})
    
    #we need to put the [] part into double quotes surrounded by single quotes, otherwise Excel freaks out
    #had to reverse engineer the xlsx format to find out the right way of entering it
    worksheet.conditional_format(conditionals['good'], {'type': 'cell',
                                               'criteria' : '==', 
                                               'value' : '"[]"',
                                               'format' : all_good})
    
    worksheet.conditional_format(conditionals['warning'], {'type': 'cell',
                                               'criteria' : '<>', 
                                               'value' : '"[]"',
                                               'format' : risk_and_warning})
    
    worksheet.conditional_format(conditionals['error'], {'type': 'cell',
                                               'criteria' : '<>', 
                                               'value' : '"[]"',
                                               'format' : error})
    
    worksheet.write(0,0,' ')
    
    return writer
