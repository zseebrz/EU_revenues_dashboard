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
        checks_message = "Now that everything is ready, you can download the results by clicking on the link at the bottom of the page, or you can check out the Analytics dashboard"
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
            pass

        try:
            os.remove(config_dict['last_zipfile_name'])
        except:
            pass
        
        """
        try:
           os.mkdir("./temp_zip")
        except:
            pass
        """
        #config_dict['status_message'] = 'copy start'
        shutil.copytree("./", "./temp_zip")
        
        zipfile = './temp_zip/audit_package_' + config_dict['last_checks_datetime'] + '.zip'
        config_dict['last_zipfile_name'] = zipfile
        #config_dict['status_message'] = zipfile
        
        src_path = Path("./temp_zip").expanduser().resolve(strict=True)
        #config_dict['status_message'] = str(src_path)
        #config_dict['status_message'] = 'zip start'
        
        #for file in src_path.rglob('*'):
        #    config_dict['status_message'] = str(file)
        
        #with ZipFile(zipfile, 'w', ZIP_DEFLATED) as zf:
        
        with ZipFile(zipfile, 'w') as zf:
            for file in src_path.rglob('*'):
                #print(file)
                #config_dict['status_message'] = str(file)
                #need to remove the "./" from the zipfile name and take the string value of the PosixPath object
                #and exclude the zip archive from the recursive operation, otherwise it freaks out
                #if zip_name[2:] not in str(file) and "__pycache__" not in str(file) and "heu_graph.text" not in str(file):
                if zipfile[2:] not in str(file):
                    zf.write(file, file.relative_to(src_path.parent))
                    #config_dict['status_message'] = str(file)+ 'has been zipped'
                else:
                    pass
        
        
        
        
        #zip_dir(zipfile, "./temp_zip")
        #config_dict['last_zipfile_name'] = zipfile
        
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