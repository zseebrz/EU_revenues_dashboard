#open the persistent config storage
from sqlitedict import SqliteDict
from first_run import InitializeConfig
try:
    config_dict = SqliteDict('./config/config_db.sqlite', autocommit=True)
except:
    InitializeConfig()
    config_dict = SqliteDict('./config/config_db.sqlite', autocommit=True)


import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# must add this line in order for the app to be deployed successfully on Heroku
from app import server
from app import app
# import all pages in the app
from apps import home, GNI_dash, file_upload, preprocess_checks

from flask import Flask, send_from_directory
#import socket

import os

#config_dict.close()

# building the navigation bar
# https://github.com/facultyai/dash-bootstrap-components/blob/master/examples/advanced-component-usage/Navbars.py
dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Home", href="/home"),
        dbc.DropdownMenuItem("Upload Files", href="/file_upload"),
        dbc.DropdownMenuItem("Run checks", href="/preprocess_checks"),
        dbc.DropdownMenuItem("Analytics dashboard", href="/GNI_dash"),
    ],
    nav = True,
    in_navbar = True,
    label = "Navigation",
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="/assets/ECA_icon.png", height="60px")),
                        dbc.Col(dbc.NavbarBrand("GNI and VAT Revenue Checks", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="/home",
            ),
            dbc.NavbarToggler(id="navbar-toggler2"),
            dbc.Collapse(
                dbc.Nav(
                    # right align dropdown menu with ml-auto className
                    [dropdown], className="ml-auto", navbar=True
                ),
                id="navbar-collapse2",
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-4",
)

def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

for i in [2]:
    app.callback(
        Output(f"navbar-collapse{i}", "is_open"),
        [Input(f"navbar-toggler{i}", "n_clicks")],
        [State(f"navbar-collapse{i}", "is_open")],
    )(toggle_navbar_collapse)

# embedding the navigation bar
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    html.Div(id='upload_alert'),
    html.Div(id='cff_date_alert'),
    html.Div(id='preprocessing_alert'),
    html.Div(id='checks_alert'),

    navbar,
    
    html.Div(id='page-content')
])

@app.callback(Output('upload_alert', 'children'),
              [Input('url', 'pathname')])
def display_upload_warning(pathname):
    if config_dict['upload_lock']:
        return dbc.Alert("The uploaded source files have changed, please re-run CFF data verification, preprocessing and the audit checks", color="warning")

@app.callback(Output('cff_date_alert', 'children'),
              [Input('url', 'pathname')])
def display_cff_data_warning(pathname):
    if config_dict['cff_date_lock']:
        return dbc.Alert("The CFF date verification file was changed, please re-run preprocessing and the audit checks", color="warning")
    
# removed the separate preprocessing tab and integrated preprocessing and checks in one tab and one callback
#@app.callback(Output('preprocessing_alert', 'children'),
#              [Input('url', 'pathname')])
#def display_preprocessing_warning(pathname):
#    if config_dict['preprocessing_lock']:
#        return dbc.Alert("The preprocessed data files have changed, please re-run preprocessing and the audit checks", color="warning")
    
@app.callback(Output('checks_alert', 'children'),
              [Input('url', 'pathname')])
def display_checks_warning(pathname):
    if config_dict['checks_lock']:
        if config_dict['checks_first_display'] and not config_dict['cff_date_lock']:
            return dbc.Alert("All files are up-to-date, you can download the results file or check the audit dashboard!", 
                             id="alert-fade", dismissable=True, is_open=True, color="success")


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/file_upload':
        return file_upload.layout
    elif pathname == '/preprocess_checks':
        return preprocess_checks.layout
    elif pathname == '/GNI_dash':
        return GNI_dash.layout
    else:
        return home.layout


#this decorator belongs to the file upload page, but must be located in the main loop to establish the server route
#to the underlying Flask server
#UPLOAD_DIRECTORY = "./uploads"
@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    #print (UPLOAD_DIRECTORY + path)
    #we don't need the upload directory, because we have the folder name in the full path
    return send_from_directory('', path, as_attachment=True)

#host = socket.gethostbyname(socket.gethostname())
#it gives 127.0.0.1, so useless in this case
if __name__ == '__main__':
    #app.run_server(debug=True, host='0.0.0.0', port = 8050)
    #need to disable hot reload for the downloading the whole audit zip package
    #app.run_server(debug=True,  dev_tools_hot_reload = False, host='0.0.0.0', port = 8050)
    app.run_server(debug=False,  dev_tools_hot_reload = False, host='0.0.0.0', port = 8050)
