#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 09:39:08 2021

@author: zseebrz
"""
# -*- coding: utf-8 -*-
#import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table

import dash

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from cff_processor_website import get_cff_dates_from_pdf_for_batch#, prepare_call_for_funds_for_batch_xlsx
#from cff_processor_website import process_call_for_funds_xlsx, getdate_CFF_xlsx, get_cff_dates_from_xlsx_for_batch
from cff_processor_website import prepare_subdelegation_for_batch, prepare_SAP_for_batch
from cff_processor_website import prepare_call_for_funds_for_batch_xlsx_website

from GNI_VAT_new_implementation_July2021_web import run_checks


from app import app

import pandas as pd
import os
#import glob
import time

from urllib.parse import quote as urlquote

import visdcc

from pathlib import Path
from zipfile import ZipFile

import shutil

#direct copy from GNI/VAT processor, to be checked
#from audit_revenues_2021_july_website import query_ECB_forex_API, query_ECB_forex_API_exact_date#, subdelegation_check
#from audit_revenues_2021_july_website import SAP_accounts, budget_lines, months, eurozone_countries, all_currencies, non_eurozone_currencies
#from audit_revenues_2020_basic import ECB_penultimate_working_day_of_month, query_ECB_forex_API_exact_date, get_Ares_date
#from audit_revenues_2020_basic import ECB_first_working_day_after_19th_of_month
#from audit_revenues_2021_july_website import ECB_working_days_between_dates
#from audit_revenues_2021_july_website import add_Excel_formattting, VAT_GNI_sections, VAT_GNI_conditionals
#from price_parser import Price
#from audit_revenues_2020_basic import sent_tokenize

#from operator import concat
#from audit_revenues_2021_july_website import rename_dupes_with_number, make_hyperlink, GetWorkFlowData

from pm4py.objects.conversion.log import converter as log_converter

#from pm4py.algo.discovery.dfg import algorithm as dfg_discovery## Import the dfg visualization object

from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
#from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
#from pm4py.visualization.petri_net import visualizer as pn_visualizer

## Import the dfg_discovery algorithm
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery## Import the dfg visualization object
#from pm4py.visualization.dfg import visualizer as dfg_visualization#Create graph from log

from pm4py.algo.organizational_mining.sna import algorithm as sna
#from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
#from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
#from pm4py.visualization.petri_net import visualizer as pn_visualizer
#import pm4py
import numpy as np
    
from pm4py.utils import get_properties
import dash_cytoscape as cyto

#this is a fork of the pm4py heuristic net visualiser that returns a graphviz object instead of a bitmap
import heu_graph as hn_visualizer

#import heu_graph
import dash_interactive_graphviz
import os

import networkx as nx
import math

from pm4py.visualization.dfg import visualizer as dfg_visualization#Create graph from log
#from dfg_viz import visualizer as dfg_visualization#Create graph from log using forked, non-hash names

from pm4py import discover_dfg as dfg_discovery2


from sqlitedict import SqliteDict
config_dict = SqliteDict('./config/config_db.sqlite', autocommit=True)

SUBDELEGATION_FILE = config_dict['SUBDELEGATION_FILE']
SAP_FILE = config_dict['SAP_FILE']
#TOR_extract = 'df_TOR_statement_extract_2020_new_w_textract.xlsx'
RO_extract = config_dict['RO_extract']
CFF_FILE = config_dict['CFF_FILE'] 
RESULT_FILE = config_dict['RESULT_FILE']

#CHECKS_LOCK_FILE = './lockfiles/check_lock.txt'
#PREPROCESS_LOCK_FILE = './lockfiles/preprocess_lock.txt'
#CFF_DATES_LOCK_FILE = './lockfiles/cff_dates_lock.txt'
#UPLOADS_LOCK_FILE = './lockfiles/uploads_lock.txt'

#LOCKFILES = [PREPROCESS_LOCK_FILE, CFF_DATES_LOCK_FILE, UPLOADS_LOCK_FILE]
#LOCKFILE_DIRECTORY = './lockfiles/'

#additional imports for the progress bar
#import time
#import dash_html_components as html
#import dash_core_components as dcc
#from dash.exceptions import PreventUpdate
#from dash_extensions.enrich import Output, Dash, Trigger, FileSystemCache
#steps, sleep_time = 100, 0.1
#import time

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

CFF_DATE_TABLE = config_dict['CFF_DATE_TABLE'] 
CFF_PDF_FOLDER = config_dict['CFF_PDF_FOLDER'] 
CFF_XLSX_FOLDER = config_dict['CFF_XLSX_FOLDER'] 

UPLOAD_DIRECTORY = config_dict['UPLOAD_DIRECTORY']

SUBDELEGATION_UPLOAD_DIRECTORY = config_dict['SUBDELEGATION_UPLOAD_DIRECTORY'] 
DW_UPLOAD_DIRECTORY = config_dict['DW_UPLOAD_DIRECTORY'] 
CFF_EXCEL_UPLOAD_DIRECTORY = config_dict['CFF_EXCEL_UPLOAD_DIRECTORY'] 
CFF_PDF_UPLOAD_DIRECTORY = config_dict['CFF_PDF_UPLOAD_DIRECTORY'] 
SAP_UPLOAD_DIRECTORY = config_dict['SAP_UPLOAD_DIRECTORY'] 

CFF_DATE_TABLE = config_dict['CFF_DATE_TABLE'] 

PROCESSED_DIRECTORY = config_dict['PROCESSED_DIRECTORY']
RESULT_DIRECTORY = config_dict['RESULT_DIRECTORY'] 

PREPROCESS_FOLDERS = config_dict['PREPROCESS_FOLDERS']

#config_dict['PREPROCESS_FOLDERS'] = [config_dict['PROCESSED_DIRECTORY'], config_dict['RESULT_DIRECTORY']]

for FOLDER in PREPROCESS_FOLDERS:
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

if not os.path.exists(CFF_XLSX_FOLDER):
    os.makedirs(CFF_XLSX_FOLDER)
  
if not os.path.exists('./cff_dates/'):
    os.makedirs('./cff_dates/')

#helper function to get networkx data structure from a dfg matrix container
def nx_viz(metric_values):
    """
    Perform SNA visualization starting from the Matrix Container object
    and the Resource-Resource matrix
    Parameters
    -------------
    metric_values
        Value of the metrics
    parameters
        Possible parameters of the algorithm, including:
            - Parameters.WEIGHT_THRESHOLD -> the weight threshold to use in displaying the graph
            - Parameters.FORMAT -> format of the output image (png, svg ...)
    Returns
    -------------
    graph
        networkX graph
    """
    import networkx as nx

    weight_threshold = 0
    
    directed = metric_values[2]

    rows, cols = np.where(metric_values[0] > weight_threshold)
    edges = zip(rows.tolist(), cols.tolist())

    if directed:
        graph = nx.DiGraph()
    else:
        graph = nx.Graph()

    labels = {}
    nodes = []
    for index, item in enumerate(metric_values[1]):
        labels[index] = item
        nodes.append(index)

    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)


    return graph, labels

#global variable for spinner on check button
#checks_running = False

#making sure the appropriate tab is displayed after a page refresh
active_tab = config_dict['preprocessing_tab'] 
layout = html.Div(
        [

        visdcc.Run_js('javascript-refresh'),
        visdcc.Run_js('javascript-refresh2'),
        visdcc.Run_js('javascript-refresh3'),     

        #dcc.Interval(id="interval", interval=500),
        
        dcc.ConfirmDialog(
        id='confirm_checks',
        message="The audit checks may take a few minutes to run. Please don't close your browser. Do you want to continue?",
                        ),

        dbc.Container([
        
        dcc.Location(id='url-preproc', refresh=True),
        
        dbc.Row(
            dbc.Col(
                html.H1("Verify and preprocess verify files, run the checks"), className="text-center")
                , className="mb-5 mt-5"),
        
        dbc.Row([
            dbc.Col(html.H5(children='Please follow the instructions on the three tabs below'
                                     )
                    , className="mb-4")
            ]),

            
    dcc.Tabs(id='tabs-prep', value=active_tab, children=[
        dcc.Tab(label='1. Verify CFF dates', value='date_verify'),
        #dcc.Tab(label='2. Preprocess files', value='preprocess'),
        dcc.Tab(label='2. Preprocess data and run the audit checks', value='check'),       
    
    ]),
    html.Div(id='tabs-content')
    
            ], className="mb-5"),
])


def init_cff_data_table(CFF_DATE_TABLE):
        try:
            #check if we already have a table verified by the users
        
            pdf_data = pd.read_excel(CFF_DATE_TABLE)
            print('CFF date Excel file exists, loading saved data')
        except:
            print('CFF date Excel file does NOT exist, running PDF processing')
        
            dates_pdf, files_pdf, cff_month_pdf = get_cff_dates_from_pdf_for_batch(CFF_PDF_FOLDER)
            
            
            #now we are going to join the pdf file links to the matched df
            pdf_data = pd.DataFrame()
            pdf_data['date_xlsx'] = cff_month_pdf
            pdf_data['pdf_files'] = files_pdf
            pdf_data['date_pdf'] = dates_pdf
            pdf_data = pdf_data.sort_values(by=['date_xlsx'])
            pdf_data['date_xlsx'] = pdf_data['date_xlsx'].apply(lambda x : x.strftime("%m/%Y"))
            #pdf_data= pdf_data[['date_pdf', 'pdf_files']]
            
            excel_cff_list = []
            for i in range(1, len(pdf_data)+1):
                #print (i)
                if i < 10:
                     excel_cff_list.append(str("0"+str(i)+"/2020"))
                else:
                    excel_cff_list.append(str(str(i)+"/2020"))
            
            pdf_data['date_xlsx'] = excel_cff_list
            
            
            #the only way to put links in the table is by markdown
            def f(row):
                #return "[{0}](<http://localhost:8050/download/uploads/cff_pdf/{0}>)".format(row["pdf_files"])
                #need to verify if it works or not with just uploads    
                return "[{0}](</download/uploads/cff_pdf/{0}>)".format(row["pdf_files"])

            
            pdf_data['pdf_files'] = pdf_data.apply(f, axis=1) 
            
            pdf_data['date_pdf']= pdf_data['date_pdf'].apply(lambda x : x.strftime("%Y-%m-%d"))
            
            pdf_data.columns = ['date_xlsx', 'pdf_files', 'date_match']
            
            pdf_data.to_excel(CFF_DATE_TABLE, index=False)
        
        return pdf_data

@app.callback(Output('tabs-content', 'children'),
              Input('tabs-prep', 'value'))
              #State('datatable-cff', 'contents'))
def render_content(tab):
    #set the right message before starting to render the tab
    if (config_dict['preprocessing_lock'] == True) and (config_dict['cff_date_lock'] == False):
        preprocess_message = "Some pre-processing is needed before we can run the checks. You have already pre-processed the files, please run the audit checks or check out the Analytics dashboard"
    else:
        preprocess_message = "Some pre-processing is needed before we can run the checks. Please click on the 'Start pre-processing' button"

    if (config_dict['checks_lock'] == True) and (config_dict['cff_date_lock'] == False):
        checks_message = "Now that everything is ready, you can download the results by clicking on the link at the bottom of the page, or you can check out the Analytics dashboard. Please refresh the page!"
    elif (config_dict['cff_date_lock'] == True):
        checks_message = "There is one step left: please click on the 'Run the pre-processing and the audit checks' button"
    else:
        checks_message = "Now that everything is ready, please click on the 'Run the audit checks'  button"


    
    if tab == 'date_verify':
                
        return html.Div([
            
                dbc.Container([
                             
                        dbc.Row(
                            dbc.Col(
                                html.H5("Please verify if the system extracted the CFF date properly by comparing the value in the table with the date on the CFF pdf file:"), className="text-center")
                                , className="mb-5 mt-5"),            

                        dbc.Row(
                            dbc.Col(
                                html.H6("We need to verify the dates on the CFF pdf files, because the Commission does not include the Call for Funds data on the Excel files. Please check if the submission dates are correct. If not, you can modify the values in the 'CFF DATE IN PDF' columns, and save the changes by pressing the 'SAVE CHANGES' button"), className="text-center")
                                , className="mb-6 mt-6"),   

                        #dbc.Row(
                        #    dbc.Col(
                        #        html.H6("If you see a spinning circle, please wait until the system finishes reading the files ."), className="text-center")
                        #        , className="mb-7 mt-7"),  


                        dcc.Input(id="loading-input-1", value='', type='hidden'),
                        
                        dcc.Loading(
                                        id="loading-1",
                                        type="circle",
                                        children=[html.Div(id="loading-output-1"),
                        
                                    ]),

                        html.Div([
                        
                            dbc.Row(
                                [
                                    dbc.Col(html.Div([
                        
                        dbc.Button('Save changes', 
                                                      id='save-cff-dates',
                                                      color="warning",
                                                      className="mt-3",
                                                      n_clicks=0),

                                                    ] )),#end of col

                                    dbc.Col(html.Div([

                        
                        dbc.Button('Go to audit checks', 
                                                      id='change-tab-button',
                                                      color="success",
                                                      className="mt-3",
                                                      n_clicks=0),
                                        
                                                    ] ))#end of col

                                ])#end of row                                                   
                        

                        ]), #end of div


                        html.Div(id='save_message')
                        
                        
                             ])#close container
                        ]) #close div

    elif tab == 'check':
        return html.Div([
            
            
               dbc.Container([
                             
                        dbc.Row(
                            dbc.Col(
                                html.H5(checks_message), className="text-center")
                                , className="mb-5 mt-5"),            

                        html.Div([
                        
                            dbc.Row(
                                [
                                    dbc.Col(html.Div([
                        
                        dbc.Button('Preprocess and run the checks', 
                                                      id='checks-start',
                                                      color="warning",
                                                      className="mt-3",
                                                      n_clicks=0),

                                                    ] )),#end of col

                                    dbc.Col(html.Div([

                        
                        dcc.Link(

                        dbc.Button('View the Analytics dasboard', 
                                                      id='change-page-button',
                                                      color="success",
                                                      className="mt-3",
                                                      n_clicks=0),
                            href='/GNI_dash'),
                                        
                                                    ] )),#end of col
                                    
                                dbc.Col(html.Div([
                        

                        
                        dbc.Button('Download the complete audit package', 
                                                      id='download-audit-package-button',
                                                      color="primary",
                                                      className="mt-3",
                                                      n_clicks=0),
                        
                        dcc.Download(id="download-audit-package"),

                                                    ] )),#end of col
                                    

                                ])#end of row                                                   
                        

                        ]), #end of div

                        dcc.Interval(id="progress-interval", n_intervals=0, interval=500), 

                        html.Br(),

                        #collapse for preprocessing progress bar
                        dbc.Row(
                            dbc.Col(
                                html.H5("Preprocessing: "), className="text-left")
                                , className="mb-5 mt-5"), 

                        dcc.Input(id="loading-input-3", value='', type='hidden'),
                        
                        dcc.Loading(
                                        id="loading-3",
                                        type="circle",
                                        children=[html.Div(id="loading-output-3"),                        
                                    ]),  

                        dbc.Collapse(     
                        
                        dbc.Progress(id="progress",     striped=True, color="info", style={"height": "40px"})
                        
                        , id='collapse',
                        is_open=False), #end collapse

                        html.P(id='progress-message'),

                        dbc.Row(
                            dbc.Col(
                                html.H5("Running the audit checks: "), className="text-left")
                                , className="mb-5 mt-5"), 

                        #collapse for the checks progress bar
                        dbc.Collapse(     
                
                        #dbc.Progress(id="progress", children=["25%"], value=25, striped=True, color="success", style={"height": "20px"})
                        
                       
                        dbc.Progress(id="progress-check",     striped=True, color="info", style={"height": "40px"})
                        
                        , id='collapse-check',
                        is_open=False), #end collapse


                        html.P(id='progress-message-check'),
 
                        html.Hr(),
                        html.H4("Download the check results in an Excel file:"),
                        html.Ul(id="file-list-check"),


                        
                             ]),#close container
               
               dbc.Container([
                            
#                        dbc.Row(
#                            dbc.Col(
#                                html.H5(preprocess_message), className="text-center")
#                                , className="mb-5 mt-5"),            

#                        html.Div([

#                        dbc.Button('Start pre-processing', 
#                                                      id='preprocess-start',
#                                                      color="warning",
#                                                      className="mr-1",
#                                                      n_clicks=0),

                        
#                        ]),               

                        #interval for progress bar
                        #dcc.Interval(id="progress-interval", n_intervals=0, interval=500), 

                        html.Br(),

                        #collapse for preprocessing progress bar
#                        dbc.Collapse(     
                
                        
#                        dbc.Progress(id="progress",     striped=True, color="info", style={"height": "40px"})
                        
#                        , id='collapse',
#                        is_open=False), #end collapse

#                        html.P(id='progress-message'),

                        dcc.Input(id="loading-input-2", value='', type='hidden'),
                        
                        dcc.Loading(
                                        id="loading-2",
                                        type="circle",
                                        children=[html.Div(id="loading-output-2"),                        
                                    ]),   

                        html.Hr(),
                        html.H4("Preprocessed file list:"),
                        html.Ul(id="file-list-preprocessed"),

                        
                             ])#close container

                        ]) #close div

@app.callback(
[Output("save_message", "data"),Output("url-preproc", "pathname"), Output("javascript-refresh", "run"),],
#[Input("save-cff-dates", "n_clicks"), Input("datatable-cff", "data")],
Input("save-cff-dates", "n_clicks"),
State("datatable-cff", "data"),
prevent_initial_call = True)
def download_excel(n_clicks, table_data):
    df = pd.DataFrame.from_dict(table_data)
    if not n_clicks:
      raise PreventUpdate
    #if we save the file with index, it will add an index column on each save, messing up the structure
    df.to_excel(CFF_DATE_TABLE, index=False)
    config_dict['cff_date_lock'] = True
    return "File saved", "/preprocess_checks", "location.reload();"


@app.callback(
Output("loading-output-1", "children"), 
Input("loading-input-1", "value"))
def cff_dates_table(value):
    
    table = dash_table.DataTable(data=init_cff_data_table(CFF_DATE_TABLE).to_dict('records'),
        #dash_table.DataTable(data=pd.read_excel(CFF_DATE_TABLE).to_dict('records'),
        #dash_table.DataTable(data=dates_df.to_dict('records'),                     
                             columns= [{"name": "CFF month in Excel", "id": "date_xlsx"},
                                       {"name": "CFF date in PDF", "id": "date_match", "presentation": "input", "editable": True},
                                       {"name": "Link to CFF pdf file", "id": "pdf_files", "presentation": "markdown"}],
                             
                             #columns= [{"name": i, "id": i, "presentation": "markdown"} for i in pd.read_excel(CFF_DATE_TABLE).columns],
                             
                             #columns= [{"name": i, "id": i} for i in dates_df.columns],
                             
                             style_cell_conditional=[
                                {'if': {'column_id': 'pdf_files'},
                                 'textAlign': 'right'}],  
                             
                             id='datatable-cff',
                             #editable=True
                             )
    
    return table


#we need a method to make the buttons work and change tabs. now only one button can change tabs
#because if we do like in the commented out procedure, one button doesn't see the other yet
#and there will be an unknown output error message
"""
@app.callback(
    Output('tabs-prep','value'),
    [Input('preprocess-tab-button','n_clicks'),Input('checks-tab-button','n_clicks')],
    prevent_initial_call = True
)
def display_tabs(n_clicks):
    ctx = dash.callback_context
    source = ctx.triggered[0]['prop id'].split('.')[0]
    if source == 'preprocess-tab-button':
        return 'preprocess'
    if source == 'checks-tab-button':
        return 'preprocess'
"""

@app.callback(
#[Output("loading-output-2", "children"), Output("javascript-refresh2", "run")],
Output("loading-output-2", "children"),
Input("checks-start", "n_clicks"),
prevent_initial_call = True)
def run_preprocessing_and_checks(n_clicks):
    if n_clicks: 
        #saves the text content of the subdelegation letters in an Excel file
        config_dict['checks_progress_state'] = 0
        
        config_dict['preprocessing_progress_state'] = 5
        config_dict['preprocessing_status_message'] = 'Processing subdelegation letters'
        
        df_subdelegation = prepare_subdelegation_for_batch(pathname=SUBDELEGATION_UPLOAD_DIRECTORY)
        df_subdelegation.to_excel('./processed/df_subdelegation.xlsx')
        
        config_dict['preprocessing_progress_state'] = 20
        config_dict['preprocessing_status_message'] = 'Processing SAP reports'
        
        #consolidates the SAP reports into one dataframe and excel file, while removing all empty lines
        df_SAP = prepare_SAP_for_batch(pathname=SAP_UPLOAD_DIRECTORY)
        df_SAP.to_excel('./processed/df_SAP.xlsx', index=False)
        
        config_dict['preprocessing_progress_state'] = 60
        config_dict['preprocessing_status_message'] = 'Preparing Call for Funds data for analysis'
        
        cff_data = prepare_call_for_funds_for_batch_xlsx_website('.//uploads//cff_excel/', CFF_DATE_TABLE)
        cff_data.to_excel('./processed/cff_data.xlsx')
        
        config_dict['preprocessing_progress_state'] = 100
        config_dict['preprocessing_status_message'] = 'Preprocessing done!'
        
        config_dict['preprocessing_lock'] = True
        config_dict['cff_date_lock'] = False
      
        #config_dict['preprocessing_tab'] = 'preprocess'
        config_dict['first_check_run'] = True
        
        #time.sleep(2)
        
        config_dict['preprocessing_status_message'] = ''

        #start of audit checks        
        #returns the dataframe, which is not used yet, but may be used later, so I keep it as it is for the moment
        result_df = run_checks()
               
        config_dict['checks_lock'] = True
        config_dict['checks_first_display'] = True
        
        config_dict['upload_lock'] = False
        config_dict['preprocessing_lock'] = False
        config_dict['cff_date_lock'] = False
        
        if config_dict['first_check_run'] == True:
            config_dict['preprocessing_tab'] = 'check'
        else:
            config_dict['preprocessing_tab'] = 'date_verify'


        #time.sleep(2)
        config_dict['status_message'] = 'delete start'
        try:
            shutil.rmtree("./temp_zip")
        except:
            config_dict['status_message'] = 'folder delete failed'
            pass

        try:
            os.remove(config_dict['last_zipfile_name'])
        except:
            config_dict['status_message'] = 'zip file delete failed'
            pass
        
        """
        try:
           os.mkdir("./temp_zip")
        except:
            pass
        """
        #config_dict['status_message'] = 'copy start'
        shutil.copytree("./", "./temp_zip")
        config_dict['status_message'] = 'snapshot copied'
        
        zipfile = './temp_zip/audit_package_' + config_dict['last_checks_datetime'] + '.zip'
        config_dict['last_zipfile_name'] = zipfile
        config_dict['status_message'] = zipfile
        
        src_path = Path("./temp_zip").expanduser().resolve(strict=True)
        config_dict['status_message'] = str(src_path)
        config_dict['status_message'] = 'zip start'
        
        #for file in src_path.rglob('*'):
        #    config_dict['status_message'] = str(file)
        
        #with ZipFile(zipfile, 'w', ZIP_DEFLATED) as zf:
        
        with ZipFile(zipfile, 'w') as zf:
            for file in src_path.rglob('*'):
                #print(file)
                config_dict['status_message'] = str(file)
                #need to remove the "./" from the zipfile name and take the string value of the PosixPath object
                #and exclude the zip archive from the recursive operation, otherwise it freaks out
                #if zip_name[2:] not in str(file) and "__pycache__" not in str(file) and "heu_graph.text" not in str(file):
                if zipfile[2:] not in str(file):
                    zf.write(file, file.relative_to(src_path.parent))
                    config_dict['status_message'] = str(file)+ 'has been zipped'
                else:
                    config_dict['status_message'] = str(file)+ 'skipped'
                    pass
        
        
        
        
        #zip_dir(zipfile, "./temp_zip")
        #config_dict['last_zipfile_name'] = zipfile

    
        #preparing the dashboard visual data
        config_dict['status_message'] = 'Preparing visualisation data'
        try:
            config_dict['dash_df'] = pd.read_excel(config_dict['RESULT_FILE'])
            
            config_dict['status_message'] = 'Initial data load successful'
        except:
            config_dict['dash_df'] = pd.DataFrame()
        
        try:
            
            #rudimentary way of getting the RO extract filename from the upploads DW folder
            #for filename in os.listdir(UPLOADS_DW_FOLDER):
            #    path = os.path.join(UPLOADS_DW_FOLDER, filename)
            #    if os.path.isfile(path):
            #        RO_extract = path
            
            #RO_extract = './uploads/dw/RO_2020_w_txt_fields.xlsx'
            RO_extract = config_dict['RO_extract'] 
            
            df_recovery_extract_positions = pd.read_excel(RO_extract, sheet_name='RO Positions')
            
            df_recovery_extract_VAT_GNI_positions = df_recovery_extract_positions[ (df_recovery_extract_positions['RO SubNature of Recovery Desc']=='REVENUES VAT') |  (df_recovery_extract_positions['RO SubNature of Recovery Desc']=='REVENUES GNI')]
            
            df_recovery_extract_workflow = pd.read_excel(RO_extract, sheet_name='RO Workflows')
            
            VAT_GNI_keys = df_recovery_extract_workflow['RO Local Key'].isin(df_recovery_extract_VAT_GNI_positions['RO Local Key'])
            
            eventlog = df_recovery_extract_workflow[VAT_GNI_keys]
            
            eventlog['action'] = eventlog['Workflow Action Code'] + ' - ' + eventlog['Workflow Step Description']  
            
            eventlog.rename(columns={'Workflow Action DateTime': 'time:timestamp', 
            'RO Local Key': 'case:concept:name', 'action': 'concept:name', 'Workflow Person Id': 'org:resource'}, inplace=True)
            
            eventlog['time:start_timestamp'] = eventlog['time:timestamp']
            
            log = log_converter.apply(eventlog)
            config_dict['dash_log'] = log
            config_dict['dash_eventlog'] = eventlog
            
            config_dict['status_message'] = 'Event log creation successful'
    
            dfg, start_activities, end_activities = dfg_discovery2(log)
            
            #a peculiar way to insantiate the parameters object, took a while to understand
            dfg_parameters = dfg_visualization.Variants.FREQUENCY.value.Parameters
            parameters = get_properties(log)
            #parameters[dfg_parameters.FORMAT] = format
            parameters[dfg_parameters.START_ACTIVITIES] = start_activities
            parameters[dfg_parameters.END_ACTIVITIES] = end_activities
            
            #gviz_start_end = dfg_visualization.apply(dfg, log=log, parameters=parameters,
            #                                         variant=dfg_visualization.Variants.FREQUENCY)
        
            import dfg_frequency
            gviz_start_end = dfg_frequency.apply(dfg, log=log, parameters=parameters)
        
            
            gviz_start_end = gviz_start_end.source
            config_dict['dash_gviz_start_end']   =    gviz_start_end
                    
            heu_net = heuristics_miner.apply_heu(log, parameters={heuristics_miner.Variants.CLASSIC.value.Parameters.DEPENDENCY_THRESH: 0.99})
            gviz_heu = hn_visualizer.apply(heu_net)
            
            config_dict['status_message'] = 'Process map creation successful'
            
            activity_list = list(heu_net.nodes.keys())
            #need to get the reverse list, so first activity would be on the top, need to start from 1
            activity_y_coordinates = list(range(1,len(activity_list)+1))[::-1]
            
           # activity_coordinates = list(zip(len(activity_list)*[0], activity_y_coordinates))
            activity_coord = {}
            for i, activity in enumerate(activity_list):
                activity_coord[activity] = activity_y_coordinates[i]
            
            #breaking up the dot file into lines
            gviz_start_end_lines = gviz_start_end.split('\n')
            for i,line in enumerate(gviz_start_end_lines):
                for activity in activity_list:
                    if activity in line and "->" not in line:
                        #print(line)
                        #line = line.replace('style=filled]', 'style=filled, pos="1,1"]')
                        activity_name = line.split('"')[1]
                        #activity_coord[activity_name]
                        #we need to add +1 so that the start and end activity would be max + 1 and 0
                        line = line.replace('style=filled]', str('style=filled, pos="0,' + str(activity_coord[activity_name]) + '!\"]'))
                        gviz_start_end_lines[i] = line
                        #print(line)
                    #the startnode has the highest position
                    elif '"@@startnode" [label=' in line:
                        line = line.replace('style=filled]', str('style=filled, pos="0,' + str(len(activity_list)+1) + '!\"]'))
                        gviz_start_end_lines[i] = line
                        line = line.replace('@@S','Start') 
                        line = line.replace('fontcolor="#32CD32"','')
                    #the endnode has the lowets position
                    elif '"@@endnode" [label=' in line:
                        line = line.replace('style=filled]', str('style=filled, pos="0,0!\"]'))
                        line = line.replace('@@E','End') 
                        line = line.replace('fontcolor="#FFA500"','')
                        gviz_start_end_lines[i] = line            
                        
            
            #add splines to make it look better
            gviz_start_end_lines.insert(len(gviz_start_end_lines)-1,'\tsplines=True\n')
            #putting the dot file back together
            comparestring = '\n'.join(gviz_start_end_lines)
            comparestring = comparestring.replace('fontsize=12','fontsize=10')
            #comparestring == gviz_start_end
            
            gviz_start_end = comparestring
            
            config_dict['dash_gviz_start_end'] = gviz_start_end     
            
            config_dict['status_message'] = 'Process map layout creation successful'
                
            #gviz_heu.write("heu_graph.txt")
            
            #convoluted way to get the dotfile as a string
            #with open("heu_graph.txt","r") as f:
            #    gviz_heu = f.read()
                
        
            #finally found a method to pass it as as string
            gviz_heu = gviz_heu.to_string()
            config_dict['dash_gviz_heu'] = gviz_heu
    
            config_dict['status_message'] = 'Process model layout creation successful'
        
            hw_values = sna.apply(log, variant=sna.Variants.HANDOVER_LOG)
                
            G, labels = nx_viz(hw_values)
            
            
            weight_matrix = hw_values[0]
            names = hw_values[1]
            
            #create the cytoscape graph
            pos = nx.layout.circular_layout(G, scale = 4)
            nodes = [
                {
                    'data': {'id': str(node), 'label': labels[node]},
                    'position': {'x': int(200*pos[node][0]), 'y': int(200*pos[node][1])},
                    #'locked': 'false'
                }
                for node in G.nodes
            ]
            
            
            edges = []
            for edge in G.edges:
                #if {'data': {'source': str(edge[0]), 'target': str(edge[1])}} not in edges and str(edge[0]) != str(edge[1]):
                #    edges.append({'data': {'source': str(edge[0]), 'target': str(edge[1])}})
                if str(edge[0]) != str(edge[1]):
                    edges.append({'data': {'source': str(edge[0]), 'target': str(edge[1])}})
            
            edges_int = []
            for edge in G.edges:
                #if {'data': {'source': edge[0], 'target': edge[1]}} not in edges and edge[0] != edge[1]:
                #    edges_int.append({'data': {'source': edge[0], 'target': edge[1]}})
                if str(edge[0]) != str(edge[1]):
                    edges_int.append({'data': {'source': edge[0], 'target': edge[1]}})
            
            #adding the weights from the edges_int list. a bit convoluted, but cytoscape requires strings for IDs
            for i,edge in enumerate(edges_int):
                #print(i, edge)
                edges[i]['data']['weight'] = math.log(weight_matrix[edge['data']['source'],edge['data']['target']] * 20000,4)
                #edges[i]['data']['weight'] = weight_matrix[edge['data']['source'],edge['data']['target']] * 200
            
            elements = nodes + edges
        
            config_dict['dash_elements'] = elements 
            
            config_dict['status_message'] = 'Social network graph creation successful'
            
        except:
            #gviz = None
            gviz_start_end = None 
            elements = None
            gviz_heu = None
    
            config_dict['dash_gviz_start_end'] = None
            config_dict['dash_elements'] = None 
            config_dict['dash_gviz_heu'] = None 
            
            config_dict['status_message'] = 'Error during process mining calculations'
        
        """
        df = df[['authorising_officer', 'RO Cashed Payment Amount (Eur)_pos']]
        
        df.columns = ['officer', 'cashed']
        """
        
        #features = df.columns
        features = config_dict['dash_df'].columns
        
        config_dict['dash_features'] = features
        
        
        #helper function for scatterplot labels
        def label_audit_results (row):
            if row['Errors'] != '[]' :
                return 'Error'
            elif row['Warnings'] != '[]' :
                return 'Warning'
            else:
                 return 'No error'
        
        
        #calculating VAT and GNI data
        try:
            df_GNI = pd.read_excel(config_dict['RESULT_FILE'], sheet_name='GNI')
            df_VAT = pd.read_excel(config_dict['RESULT_FILE'], sheet_name='VAT')
            
            df_GNI['Audit results'] = df_GNI.apply (lambda row: label_audit_results(row), axis=1)
            df_VAT['Audit results'] = df_VAT.apply (lambda row: label_audit_results(row), axis=1)
            
            colorsIdx = {'No error': '#1f77b4', 'Warning': '#ff7f0e', 'Error': '#d62728'}
            
            df_GNI['Audit classification'] = df_GNI['Audit results'].map(colorsIdx)
            df_VAT['Audit classification'] = df_VAT['Audit results'].map(colorsIdx)
            
            df = df_GNI.append(df_VAT)
            
            result = df[['MS', 'transaction_type', 'RO Cashed Amount (Eur)_pos',
                   'Rejection in workflow',
                   'Workflow steps exceed average',
                   'Workflow duration longer than average', 'One-day-approval',
                   'workflow_days_under_30', 'budget_line_correct', 'SAP_accounting_class',
                   'recovery_order_position_amount_in_local_curr_matches_call',
                   'Missing SAP data', 'amount_diff_within_tolerance',
                   'amount_requested_in_time',
                   'cashing deadline_observed', 'CFF_rate_diff_within_tolerance']].groupby(['MS',
                                                                                     'transaction_type']).sum()
            
            
            
            result = result.reset_index()
                                                                                            
            x = result[result['transaction_type']=='VAT']['RO Cashed Amount (Eur)_pos']
            y = result[result['transaction_type']=='GNI']['RO Cashed Amount (Eur)_pos']
            ms = result[result['transaction_type']=='VAT']['MS']
            
            df2 = pd.DataFrame()
            df2['GNI'] = list(y)
            df2['VAT'] = list(x)
            df2['MS'] = list(ms)
            
            df_GNI_errors = df_GNI[df_GNI['Errors'] != '[]']
            df_VAT_errors = df_VAT[df_VAT['Errors'] != '[]']
            
            df_GNI_warnings = df_GNI[df_GNI['Warnings'] != '[]']
            df_VAT_warnings = df_VAT[df_VAT['Warnings'] != '[]']
            
            df_GNI_risks = df_GNI[(df_GNI['Risk flags'] != '[]') & (df_GNI['Risk flags'] != "['One-day-approval']")  & (df_GNI['Risk flags'] != "['Workflow duration longer than average']")]
            df_VAT_risks = df_VAT[(df_VAT['Risk flags'] != '[]') & (df_VAT['Risk flags'] != "['One-day-approval']")  & (df_VAT['Risk flags'] != "['Workflow duration longer than average']")]
            
            df_errors = df_GNI_errors.append(df_VAT_errors)
            
            df_warnings = df_GNI_warnings.append(df_VAT_warnings)
            
            df_risks = df_GNI_risks.append(df_VAT_risks)
            
            df_errors = df_errors[['RO Position Local Key', 
                   'GL Account Short Desc', 'RO Due Date','RO Cashing Cashed Date',
                   'RO SubNature of Recovery Desc', 'RO Cashed Amount (Eur)_pos',
                   'month', 'MS', 'authorising_officer',
                   'Risk flags', 'Warnings', 'Errors']]
            
            df_warnings = df_warnings[['RO Position Local Key', 
                   'GL Account Short Desc', 'RO Due Date','RO Cashing Cashed Date',
                   'RO SubNature of Recovery Desc', 'RO Cashed Amount (Eur)_pos',
                   'month', 'MS', 'authorising_officer',
                   'Risk flags', 'Warnings', 'Errors']]
            
            df_risks = df_risks[['RO Position Local Key', 
                   'GL Account Short Desc', 'RO Due Date','RO Cashing Cashed Date',
                   'RO SubNature of Recovery Desc', 'RO Cashed Amount (Eur)_pos',
                   'month', 'MS', 'authorising_officer',
                   'Risk flags', 'Warnings', 'Errors']]
            
            config_dict['status_message'] = 'Error analysis calculations completed'
        
        except:
        
            df_errors = pd.DataFrame()
            df_warnings = pd.DataFrame()
            df_risks = pd.DataFrame()
            df2 = pd.DataFrame()
            
            config_dict['status_message'] = 'Error during analysis calculations'
            
        config_dict['dash_df_errors'] = df_errors
        config_dict['dash_df_warnings'] = df_warnings
        config_dict['dash_df_risks'] = df_risks
        config_dict['dash_df2'] = df2       
        config_dict['dash_df_VAT'] = df_VAT
        config_dict['dash_df_GNI'] = df_GNI
            
        #errors = df_errors.to_dict('records')
        #warnings = df_warnings.to_dict('records')
        
        try:
            error_stats = 'Number of errors: ' + str(len(df_errors)) + ' / ' + str(len(df)) + ', Amount affected by error: ' + str(int(df_errors['RO Cashed Amount (Eur)_pos'].sum())) + ' EUR'
            warning_stats = 'Number of warnings: ' + str(len(df_warnings)) + ' / ' + str(len(df)) + ', Amount affected by warnings: ' + str(int(df_warnings['RO Cashed Amount (Eur)_pos'].sum())) + ' EUR'
            countries_with_error = 'Member States affected by errors: ' + str(list(set(df_errors['MS'])))
            countries_with_warning = 'Member States affected by warnings: ' +  str(list(set(df_warnings['MS'])))
            
            error_stats = [error_stats, html.Br(), countries_with_error]
            warning_stats = [warning_stats, html.Br(), countries_with_warning]
            
        except:
            error_stats = ''
            warning_stats = ''
            countries_with_error = ''
            countries_with_warning = ''
            
        config_dict['dash_error_stats'] = error_stats
        config_dict['dash_warning_stats'] = warning_stats
        config_dict['dash_countries_with_error'] = countries_with_error
        config_dict['dash_countries_with_warning'] = countries_with_warning


        
        config_dict['status_message'] = ''
        
        return dbc.Container([
                        dbc.Row(
                            dbc.Col(
                                html.H5("The audit checks have been completed, after refreshing the page, please download the results file or look at the analytics dasboard!"), className="text-center")
                                #, className="mb-5 mt-5"),])  , "location.reload();"
                                , className="mb-5 mt-5"),])
    else:
        return 'End of callback run'#,''
    

#file folder display functions, will need to consolidate
def uploaded_files(save_folder):
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(save_folder):
        path = os.path.join(save_folder, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files

def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)

def update_filedialog(save_folder): 

    files = uploaded_files(save_folder)
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(save_folder+'/'+filename)) for filename in files]

@app.callback(
    Output("file-list-preprocessed", "children"),
    [Input("loading-input-2", "value")],
)
def update_filedialog_preprocessed(value):
    """Save uploaded files and regenerate the file list."""
    folder = PROCESSED_DIRECTORY
    return update_filedialog(folder)

@app.callback(
    Output("file-list-check", "children"),
    [Input("loading-input-3", "value")],
)
def update_filedialog_checks(value):
    """Save uploaded files and regenerate the file list."""
    folder = RESULT_DIRECTORY
    return update_filedialog(folder)


@app.callback(
    [Output("something", "children")],#,Output("url", "pathname")],
    Input("confirm_check", "submit_n_clicks"),
    prevent_initial_call = True
    )   
def start_preprocessing(submit_n_clicks):
    """OK button was clicked"""
    print(submit_n_clicks)
    if submit_n_clicks:
        print('ok was clicked')
        return "something"
    #i have to return empty stuff at first run, otherwise it gives me an error
    else:
        return [],""

#open collapse
@app.callback(
    Output("collapse", "is_open"),
    Input("checks-start", "n_clicks"),
    #[Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

#callback for progress bar
@app.callback(
    [Output("progress", "value"), Output("progress", "children"), Output("progress-message", "children")],
    [Input("progress-interval", "n_intervals")],
)
def update_progress(n):
    # check progress of some background process, in this example we'll just
    # use n_intervals constrained to be in 0-100
    #progress = min(n % 110, 100)
    progress = config_dict['preprocessing_progress_state']
    message = config_dict['preprocessing_status_message']
    # only add text after 5% progress to ensure text isn't squashed too much
    return progress, f"{progress} %" if progress >= 5 else "", message

#open collapse for audit checks
@app.callback(
    Output("collapse-check", "is_open"),
    Input("checks-start", "n_clicks"),
    #[Input("collapse-button", "n_clicks")],
    [State("collapse-check", "is_open")],
)
def toggle_collapse_check(n, is_open):
    if n:
        return not is_open
    return is_open

#callback for progress bar for audit checks
@app.callback(
    [Output("progress-check", "value"), Output("progress-check", "children"), Output("progress-message-check", "children")],
    [Input("progress-interval", "n_intervals")],
)
def update_progress_check(n):
    # check progress of some background process, in this example we'll just
    # use n_intervals constrained to be in 0-100
    #progress = min(n % 110, 100)
    progress = config_dict['checks_progress_state']
    message = config_dict['status_message']
    # only add text after 5% progress to ensure text isn't squashed too much
    return progress, f"{progress} %" if progress >= 5 else "", message

@app.callback(
    # Button: switch to run checks tab
    Output("tabs-prep", "value"),
    [Input("change-tab-button", "n_clicks")],
    prevent_initial_call = True)
def change_tabs(click):
    if click:
        return "check"

@app.callback(
    [Output("loading-output-3", "children"), Output("download-audit-package", "data")],
    #Output("download-audit-package", "data"),
    Input("download-audit-package-button", "n_clicks"),
    prevent_initial_call=True,
)
def download_audit_package(n_clicks):
    #remove the previous zipfile, otherwise they will pile up in the folder
    if n_clicks:

        """        
        try:
            shutil.rmtree("./temp_zip")
        except:
            pass

        try:
            os.remove(config_dict['last_zipfile_name'])
        except:
            pass
        
        try:
           os.mkdir("./temp_zip")
        except:
            pass
        
        copy_tree("./", "./temp_zip")
        
        zipfile = './temp_zip/audit_package_' + config_dict['last_checks_datetime'] + '.zip'
        zip_dir(zipfile, "./temp_zip")
        config_dict['last_zipfile_name'] = zipfile
        time.sleep(15)
        
        """
        zipfile = config_dict['last_zipfile_name']
        return '', dcc.send_file(zipfile,filename=zipfile[2:])
    else:
        pass

"""
@app.callback(Output('datatable-upload-container', 'data'),
              Output('datatable-upload-container', 'columns'),
              Input('datatable-cff', 'contents'))
def update_output(contents):
    if contents is None:
        return [{}], []
    df = pd.read_excel('/processed/cff_pdf_dates_xlsx')  
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
"""

"""
if __name__ == '__main__':
    app.run_server(debug=True)
"""
