#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 18:43:14 2021

@author: zseebrz
"""
import base64
import datetime
import io
import os
import glob

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table

from urllib.parse import quote as urlquote

import pandas as pd

from app import app

import visdcc
from sqlitedict import SqliteDict

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

config_dict = SqliteDict('./config/config_db.sqlite', autocommit=True)

UPLOAD_DIRECTORY = config_dict['UPLOAD_DIRECTORY']

SUBDELEGATION_UPLOAD_DIRECTORY = config_dict['SUBDELEGATION_UPLOAD_DIRECTORY']
DW_UPLOAD_DIRECTORY = config_dict['DW_UPLOAD_DIRECTORY'] 
CFF_EXCEL_UPLOAD_DIRECTORY = config_dict['CFF_EXCEL_UPLOAD_DIRECTORY'] 
CFF_PDF_UPLOAD_DIRECTORY = config_dict['CFF_PDF_UPLOAD_DIRECTORY'] 
SAP_UPLOAD_DIRECTORY = config_dict['SAP_UPLOAD_DIRECTORY'] 

CFF_DATE_TABLE = config_dict['CFF_DATE_TABLE']

UPLOAD_FOLDERS = config_dict['UPLOAD_FOLDERS'] 

#config_dict['UPLOAD_FOLDERS'] = [config_dict['SUBDELEGATION_UPLOAD_DIRECTORY'], config_dict['DW_UPLOAD_DIRECTORY'], 
#                  config_dict['CFF_EXCEL_UPLOAD_DIRECTORY'], config_dict['CFF_PDF_UPLOAD_DIRECTORY'],
#                  config_dict['SAP_UPLOAD_DIRECTORY']]

for FOLDER in UPLOAD_FOLDERS:
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)


layout = html.Div(
    [
     
     
     dcc.ConfirmDialog(
        id='confirm',
        message='This will delete all uploaded files. Are you sure you want to continue?',
    ),
   

   #doesn't work properly, have to check why  
   #dcc.Location(id='url', refresh=True),
   dcc.Location(id='url-subdelegation', refresh=True), 
   dcc.Location(id='url-dw', refresh=True), 
   dcc.Location(id='url-cff-excel', refresh=True), 
   dcc.Location(id='url-cff-pdf', refresh=True), 
   dcc.Location(id='url-sap', refresh=True), 
   
   
   visdcc.Run_js('javascript-subdelegation'),
   visdcc.Run_js('javascript-dw'),
   visdcc.Run_js('javascript-cff-excel'),
   visdcc.Run_js('javascript-cff-pdf'),
   visdcc.Run_js('javascript-sap'),

   visdcc.Run_js('javascript-subdelegation2'),
   visdcc.Run_js('javascript-dw2'),
   visdcc.Run_js('javascript-cff-excel2'),
   visdcc.Run_js('javascript-cff-pdf2'),
   visdcc.Run_js('javascript-sap2'),
   
    #put the different filetype lists here
    
    #subdelegation letters
    
    dbc.Container([
        
        dbc.Row(
            dbc.Col(
                html.H1("File Browser and upload"), className="text-center")
                , className="mb-5 mt-5"),
        
        dbc.Row([
            dbc.Col(html.H5(children='Please upload all the necessary files for analysis:'
                                     )
                    , className="mb-4")
            ]),


        dbc.Row([
            dbc.Col(dbc.Card(children=[html.H3(children='Upload subdelegation letters from folder',
                                               className="text-center"),


                                       html.Div([
                                       
                                           dcc.Upload(id='upload-data-subdelegation',
                                                      children = html.Div([
                                                          dbc.Button("Upload subdelegation letters",
                                                          color="primary",
                                                          className="mt-3")
                                                          ]),
                                                        # Allow multiple files to be uploaded
                                                        multiple=True
                                                            ),
                                       
                                           dbc.Button('Delete subdelegation letters', 
                                                      id='delete_subdelegation',
                                                      color="warning",
                                                      className="mt-3",
                                                      n_clicks=0),
                                           
                                           ]),
                                       
                                           html.Hr(),
                                           html.H4("Subdelegation file List:"),
                                           html.Ul(id="file-list-subdelegation"),
                                                                             
                                       ],
                             body=True, color="dark", outline=True)
                    , width=8, className="mb-4"),
            
            dbc.Col(dbc.Card(children=[html.H3(children='Upload Data Warehouse extract from folder',
                                               className="text-center"),


                                       html.Div([
                                       
                                           dcc.Upload(id='upload-data-dw',
                                                      children = html.Div([
                                                          dbc.Button("Upload DW extract",
                                                          color="primary",
                                                          className="mt-3")
                                                          ]),
                                                        # Allow multiple files to be uploaded
                                                        multiple=False
                                                            ),
                                       
                                           dbc.Button('Delete DW extract', 
                                                      id='delete_dw',
                                                      color="warning",
                                                      className="mt-3",
                                                      n_clicks=0),
                                           
                                           ]),
                                       
                                           html.Hr(),
                                           html.H4("DW extract file:"),
                                           html.Ul(id="file-list-dw"),
                                                                             
                                       ],
                             body=True, color="dark", outline=True)
                    , width=8, className="mb-4"),            
            
               
            dbc.Col(dbc.Card(children=[html.H3(children='Upload Call For Funds XLSX files from folder',
                                               className="text-center"),


                                       html.Div([
                                       
                                           dcc.Upload(id='upload-data-cff-excel',
                                                      children = html.Div([
                                                          dbc.Button("Upload CFF Excel files",
                                                          color="primary",
                                                          className="mt-3")
                                                          ]),
                                                        # Allow multiple files to be uploaded
                                                        multiple=True
                                                            ),
                                       
                                           dbc.Button('Delete CFF Excel files', 
                                                      id='delete_cff-excel',
                                                      color="warning",
                                                      className="mt-3",
                                                      n_clicks=0),
                                           
                                           ]),
                                       
                                           html.Hr(),
                                           html.H4("CFF files in Excel:"),
                                           html.Ul(id="file-list-cff-excel"),
                                                                             
                                       ],
                             body=True, color="dark", outline=True)
                    , width=8, className="mb-4"),        
        
            dbc.Col(dbc.Card(children=[html.H3(children='Upload Call For Funds PDF files from folder',
                                               className="text-center"),


                                       html.Div([
                                       
                                           dcc.Upload(id='upload-data-cff-pdf',
                                                      children = html.Div([
                                                          dbc.Button("Upload CFF PDF files",
                                                          color="primary",
                                                          className="mt-3")
                                                          ]),
                                                        # Allow multiple files to be uploaded
                                                        multiple=True
                                                            ),
                                       
                                           dbc.Button('Delete CFF PDF files', 
                                                      id='delete_cff-pdf',
                                                      color="warning",
                                                      className="mt-3",
                                                      n_clicks=0),
                                           
                                           ]),
                                       
                                           html.Hr(),
                                           html.H4("CFF files in PDF:"),
                                           html.Ul(id="file-list-cff-pdf"),
                                                                             
                                       ],
                             body=True, color="dark", outline=True)
                    , width=8, className="mb-4"),       


            dbc.Col(dbc.Card(children=[html.H3(children='Upload SAP reports from folder',
                                               className="text-center"),


                                       html.Div([
                                       
                                           dcc.Upload(id='upload-data-sap',
                                                      children = html.Div([
                                                          dbc.Button("Upload SAP report files",
                                                          color="primary",
                                                          className="mt-3")
                                                          ]),
                                                        # Allow multiple files to be uploaded
                                                        multiple=True
                                                            ),
                                       
                                           dbc.Button('Delete SAP report files', 
                                                      id='delete_sap',
                                                      color="warning",
                                                      className="mt-3",
                                                      n_clicks=0),
                                           
                                           ]),
                                       
                                           html.Hr(),
                                           html.H4("SAP report files:"),
                                           html.Ul(id="file-list-sap"),
                                                                             
                                       ],
                             body=True, color="dark", outline=True)
                    , width=8, className="mb-4"),  

            
        ], className="mb-5"),
        
        ]),
        
    dbc.Button('Delete all uploaded files',
               id='delete_files',
               color="danger",
               className="mt-3",
               n_clicks=0),         
    #html.Button('Delete all uploaded files', id='delete_files', n_clicks=0),    
    html.Div(id='deleted'),

    
    #uncomment if you want to display the head of the datafiles
    #html.Div(id='output-data-upload'),

    html.Br(),
    html.Br(), 
    html.A("Please check carefully, if you have uploaded the correct files!"),
    
    html.Br(),
    html.Br(), 
    html.A("An automation pilot project by Chamber V and the ECALab.",
       href="https://www.eca.europa.eu")
    
    ],
    #style={"max-width": "800px"},
)

def save_file(name, content, save_folder):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    #we need to set the flags so that upload lock will be true and the date verify tab will show first
    config_dict['upload_lock'] = True
    config_dict['active_tab'] = 'date_verify'
    with open(os.path.join(save_folder, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


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


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename or 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            #data=df.to_dict('records'),
            data=df.head(5).to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

#subfunctions for closures
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

def update_filedialog(uploaded_filenames, uploaded_file_contents, save_folder): 
    print(uploaded_filenames, save_folder)
    #if the upload dialog did not have multiple selection enabled, it's not a list, just a string, we need try-except
    try:
        if uploaded_filenames is not None and uploaded_file_contents is not None:
            for name, data in zip(uploaded_filenames, uploaded_file_contents):
                save_file(name, data, save_folder)
    except:
        save_file(uploaded_filenames, uploaded_file_contents, save_folder)

    files = uploaded_files(save_folder)
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(save_folder+'/'+filename)) for filename in files]

def delete_file(n_clicks, delete_folder):
    """OK button was clicked"""
    print(n_clicks)
    if n_clicks:
        #print('delete_subdelegation was clicked')
        files = glob.glob(str(delete_folder)+'/*')
        for f in files:
            os.remove(f)
        config_dict['upload_lock'] = True
        config_dict['active_tab'] = 'date_verify'
        #return 'Files have been deleted'
        return "/file_upload/"
    #i have to return empty stuff at first run, otherwise it gives me an error
    else:
        return "/file_upload/"


#subdelegation letter upload and listing
@app.callback(Output('output-data-upload-subdelegation', 'children'),
              Input('upload-data-subdelegation', 'contents'),
              State('upload-data-subdelegation', 'filename'),
              State('upload-data-subdelegation', 'last_modified'))
def update_output_subdelegation(list_of_contents, list_of_names, list_of_dates):
    return update_output(list_of_contents, list_of_names, list_of_dates)

@app.callback(
    #[Output("file-list-subdelegation", "children"), Output("javascript-subdelegation2", "run")],
    #remove output from bracket when removing the second output arguments, otherwise it throws an error
    Output("file-list-subdelegation", "children"),
    [Input("upload-data-subdelegation", "filename"), Input("upload-data-subdelegation", "contents")],
    #prevent_initial_call = True)
    )   
def update_filedialog_subdelegation(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""
    save_folder = SUBDELEGATION_UPLOAD_DIRECTORY    
    return update_filedialog(uploaded_filenames, uploaded_file_contents, save_folder)#, "location.reload();"


#DW extract upload and listing

@app.callback(Output('output-data-upload-dw', 'children'),
              Input('upload-data-dw', 'contents'),
              State('upload-data-dw', 'filename'),
              State('upload-data-dw', 'last_modified'))
def update_output_dw(list_of_contents, list_of_names, list_of_dates):
    return update_output(list_of_contents, list_of_names, list_of_dates)


@app.callback(
    #[Output("file-list-dw", "children"), Output("dw2", "run")],
    [Output("file-list-dw", "children")],
    [Input("upload-data-dw", "filename"), Input("upload-data-dw", "contents")],
    #prevent_initial_call = True)
    )
def update_filedialog_dw(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""   
    save_folder = DW_UPLOAD_DIRECTORY
    print(uploaded_filenames, save_folder)
    return update_filedialog(uploaded_filenames, uploaded_file_contents, save_folder)#,  "location.reload();"

#CFF Excel upload and listing

@app.callback(Output('output-data-upload-cff-excel', 'children'),
              Input('upload-data-cff-excel', 'contents'),
              State('upload-data-cff-excel', 'filename'),
              State('upload-data-cff-excel', 'last_modified'))
def update_output_cff_excel(list_of_contents, list_of_names, list_of_dates):
    #os.remove(CFF_DATE_TABLE)
    return update_output(list_of_contents, list_of_names, list_of_dates)


@app.callback(
    Output("file-list-cff-excel", "children"),
    [Input("upload-data-cff-excel", "filename"), Input("upload-data-cff-excel", "contents")],
)
def update_filedialog_cff_excel(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""


    save_folder = CFF_EXCEL_UPLOAD_DIRECTORY
    print(uploaded_filenames, save_folder)
    return update_filedialog(uploaded_filenames, uploaded_file_contents, save_folder)


#CFF PDF upload and listing

@app.callback(Output('output-data-upload-cff-pdf', 'children'),
              Input('upload-data-cff-pdf', 'contents'),
              State('upload-data-cff-pdf', 'filename'),
              State('upload-data-cff-pdf', 'last_modified'))
def update_output_cff_pdf(list_of_contents, list_of_names, list_of_dates):
    #os.remove(CFF_DATE_TABLE)
    return update_output(list_of_contents, list_of_names, list_of_dates)


@app.callback(
    Output("file-list-cff-pdf", "children"),
    [Input("upload-data-cff-pdf", "filename"), Input("upload-data-cff-pdf", "contents")],
)
def update_filedialog_cff_pdf(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    save_folder = CFF_PDF_UPLOAD_DIRECTORY
    print(uploaded_filenames, save_folder)
    return update_filedialog(uploaded_filenames, uploaded_file_contents, save_folder)

#SAP report upload and listing

@app.callback(Output('output-data-upload-sap', 'children'),
              Input('upload-data-sap', 'contents'),
              State('upload-data-sap', 'filename'),
              State('upload-data-sap', 'last_modified'))
def update_output_sap(list_of_contents, list_of_names, list_of_dates):
    return update_output(list_of_contents, list_of_names, list_of_dates)


@app.callback(
    Output("file-list-sap", "children"),
    [Input("upload-data-sap", "filename"), Input("upload-data-sap", "contents")],
)
def update_filedialog_sap(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    
    save_folder = SAP_UPLOAD_DIRECTORY
    print(uploaded_filenames, save_folder)
    return update_filedialog(uploaded_filenames, uploaded_file_contents, save_folder)

#delete all files button, pop-up-window, deletion and page reload
@app.callback(
    Output("confirm", "displayed"),
    Input("delete_files", "n_clicks"),
    prevent_initial_call = True)   
def delete_files_dialog(n_clicks):
    """Delete files button clicked"""
    return True

@app.callback(
    [Output("deleted", "children"),Output("url", "pathname")],
    Input("confirm", "submit_n_clicks"),
    prevent_initial_call = True
    )   
def delete_files(submit_n_clicks):
    """OK button was clicked"""
    print(submit_n_clicks)
    if submit_n_clicks:
        print('ok was clicked')
        files_ = []
        for FOLDER in UPLOAD_FOLDERS:
            files_ += glob.glob(str(FOLDER)+'/*')
            print(glob.glob(str(FOLDER)+'/*'))
        files = glob.glob(str(UPLOAD_DIRECTORY)+'/*')
        for f in files_:
            os.remove(f)
        os.remove(CFF_DATE_TABLE)
        config_dict['upload_lock'] = True
        config_dict['active_tab'] = 'date_verify'
        #return 'Files have been deleted'
        return files, "/file_upload"
    #i have to return empty stuff at first run, otherwise it gives me an error
    else:
        return [],""

#subdelegation delete button callbacks
@app.callback(
    #[Output("deleted-subdelegation", "children"),Output("url-subdelegation", "pathname")],
    Output("javascript-subdelegation", "run"),
    Input("delete_subdelegation", "n_clicks"),
    prevent_initial_call = True
    )   
def delete_subdelegation_files(n_clicks):
    """OK button was clicked"""
    if n_clicks:
        delete_folder = SUBDELEGATION_UPLOAD_DIRECTORY
        print(n_clicks)
        delete_file(n_clicks, delete_folder)
        return "location.reload();"
    return ""
    
#abac dw delete button callbacks
@app.callback(
    Output("javascript-dw","run"),
    Input("delete_dw", "n_clicks"),
    prevent_initial_call = True
    )   
def delete_dw_file(n_clicks):
    """OK button was clicked"""
    if n_clicks:
        delete_folder = DW_UPLOAD_DIRECTORY
        print(n_clicks)
        delete_file(n_clicks, delete_folder)
        return "location.reload();"
    return ""

#cff excel delete button callbacks
@app.callback(
    Output("javascript-cff-excel", "run"),
    Input("delete_cff-excel", "n_clicks"),
    prevent_initial_call = True
    )   
def delete_cff_excel_file(n_clicks):
    if n_clicks:
        delete_folder = CFF_EXCEL_UPLOAD_DIRECTORY
        print(n_clicks)
        delete_file(n_clicks, delete_folder)
        return "location.reload();"
    return ""

#cff pdf delete button callbacks
@app.callback(
    Output("javascript-cff-pdf", "run"),
    Input("delete_cff-pdf", "n_clicks"),
    prevent_initial_call = True
    )   
def delete_cff_pdf_file(n_clicks):
    if n_clicks:
        delete_folder = CFF_PDF_UPLOAD_DIRECTORY
        print(n_clicks)
        delete_file(n_clicks, delete_folder)
        return "location.reload();"
    return ""
    
#cff SAP button callbacks
@app.callback(
    Output("javascript-sap", "run"),
    Input("delete_sap", "n_clicks"),
    prevent_initial_call = True
    )   
def delete_sap_file(n_clicks):
    if n_clicks:
        delete_folder = SAP_UPLOAD_DIRECTORY
        print(n_clicks)
        delete_file(n_clicks, delete_folder)
        return "location.reload();"
    return ""

#if __name__ == '__main__':
#    app.run_server(debug=True)