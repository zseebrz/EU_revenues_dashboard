#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 17:02:03 2021

@author: zseebrz
"""
import pandas as pd
import time
import os
import textract
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize

#subdelegation check
#store all subdelegation letters as text fields (list of tokens and list of sentences) in the dataframe
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
        

#saves the text content of the TOR statements in an Excel file
df_extract = prepare_TOR_statement_for_batch_from_directory(pathname='./TOR_data_2020')
df_extract.to_excel('df_TOR_statement_extract_2020_new_w_textract.xlsx')


#saves the text content of the subdelegation letters in an Excel file
df_subdelegation = prepare_subdelegation_for_batch(pathname='./Sub-delegations for signing')
df_subdelegation.to_excel('df_subdelegation.xlsx')

#consolidates the SAP reports into one dataframe and excel file, while removing all empty lines
df_SAP = prepare_SAP_for_batch(pathname='./2020_full/sap')
df_SAP.to_excel('df_SAP.xlsx')

