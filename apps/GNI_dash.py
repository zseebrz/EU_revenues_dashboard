#######
# Here we'll use the mpg.csv dataset to demonstrate
# how multiple inputs can affect the same graph.
######
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
#from dash.dependencies import Input, Output
from dash_extensions.enrich import Dash, ServersideOutput, Output, Input, Trigger
import dash_table as dt

import plotly.graph_objects as go
import pandas as pd

from app import app

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
#app = dash.Dash()

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

from sqlitedict import SqliteDict
#desperate try
global config_dict
config_dict = SqliteDict('./config/config_db.sqlite', autocommit=True)

RESULTS_FOLDER = config_dict['RESULTS_FOLDER'] 
UPLOADS_DW_FOLDER = config_dict['UPLOADS_DW_FOLDER']

if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)

layout =     dbc.Container([
        
    dbc.Row([
            dbc.Col(html.H1("GNI and VAT revenue checks dashboard", className="text-center")
                    , className="mb-5 mt-5")
        ]),#end of row

        #triggers the data update
        html.Div(id="onload"),
        #hide the output
        html.Div(id="onload_output"), 

        html.Div([
                
        dcc.Tabs(id='tabs-dash', value='error_analysis', children=[
            dcc.Tab(label='Error Analysis', value='error_analysis'),
            dcc.Tab(label='Visual Analytics', value='visual_analytics'),
            dcc.Tab(label='Actual Process', value='actual_process'),
            dcc.Tab(label='Process Model', value='process_model'),
            dcc.Tab(label='Social Network Analysis', value='social_network'),       
           
            ]),#tabs
        
            html.Div(id='tabs-content-dash')
        
        ],
    style={'padding':10}),#end of div
     
    ])#end of container

@app.callback(Output('tabs-content-dash', 'children'),
              Input('tabs-dash', 'value'))
              #State('datatable-cff', 'contents'))
def render_content(tab):

    if tab == 'error_analysis':       
        return html.Div([
            
            dbc.Container([
            
 
        html.Hr(),
        
        dbc.Row([
            dbc.Col(html.H4(children='An overview of audit errors and warnings (red flags) found for GNI/VAT:'
                                     )
                    , className="mb-4")
            ]),

        dbc.Row([
            dbc.Col([html.H5(children=config_dict['dash_error_stats'])]
                    , className="mb-5")
            ]),

                  
            dbc.Container([
                    
                        html.Div(dt.DataTable(columns=[{"name": i, "id": i} for i in config_dict['dash_df_errors'].columns], 
                                              data=config_dict['dash_df_errors'].to_dict('records'), 
                                              id='table_errors',
                                              style_table={'overflowX': 'auto'},))
                                    
            ]),#end of container

            html.Br(),
            html.Br(),

            dbc.Row([
            #dbc.Col(html.H5(#children='Warnings'
            dbc.Col(html.H5(children=config_dict['dash_warning_stats']
                                     )
                    , className="mb-5")
            ]),

            #dbc.Row([
            #dbc.Col([html.H5(children=countries_with_warning)]
            #        , className="mb-5")
            #                   ]),
    
            dbc.Container([
                    
                        html.Div(dt.DataTable(columns=[{"name": i, "id": i} for i in config_dict['dash_df_warnings'].columns], 
                                              data=config_dict['dash_df_warnings'].to_dict('records'), 
                                              id='table_errors',
                                              style_table={'overflowX': 'auto'},))
                                    
            ]),#end of container
            
            html.Br(),

            dbc.Row([
            dbc.Col(html.H5(children='Risk flags'
                                     )
                    , className="mb-5")
            ]),
    
            dbc.Container([
                    
                        html.Div(dt.DataTable(columns=[{"name": i, "id": i} for i in config_dict['dash_df_risks'].columns], 
                                              data=config_dict['dash_df_risks'].to_dict('records'), 
                                              id='table_risks',
                                              style_table={'overflowX': 'auto'},))
                                    
            ]),#end of container
            
        ]),     #end of to level container

        ]) #end of top level div               

            

  
    elif tab == 'visual_analytics':     
        return html.Div([
            
            dbc.Container([                

        html.Hr(), 

        dbc.Row([
            dbc.Col(html.H4(children='Please choose the fields to be analysed from the drop-down list'
                                     )
                    , className="mb-4"),
            ]),#end of row

            html.Div([
            dcc.Dropdown(
                id='xaxis',
                options=[{'label': i.title(), 'value': i} for i in config_dict['dash_features']],
                value='MS'
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='yaxis',
                options=[{'label': i.title(), 'value': i} for i in config_dict['dash_features']],
                value='RO Cashed Payment Amount (Eur)_pos'
            )
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

        html.Br(),

        dbc.Row([
            dbc.Col(html.H5("VAT data for 2020", className="text-center")
                    , className="mb-5 mt-5")
        ]),

        html.Div([dcc.Graph(id='VAT_scatterplot'),]),
               
        dbc.Row([
            dbc.Col(html.H5("GNI data for 2020", className="text-center")
                    , className="mb-5 mt-5")
        ]),
        
        dcc.Graph(id='GNI_scatterplot'),
        
        html.Br(),

        dbc.Row([
            dbc.Col(html.H5("VAT vs GNI based payments per Member State in 2020", className="text-center")
                    , className="mb-5 mt-5")
        ]),
        
        dcc.Graph(id='VAT_vs_GNI')
                
        
        
                                            ], #end of children        
            ), #end of to level container
        ]) #end of top level div


    elif tab == 'actual_process':     
        return html.Div([
            
            dbc.Container([
 
        html.Hr(),
        
        dbc.Row([
            dbc.Col(html.H4(children='This is how the process looks like in real life:'
                                     )
                    , className="mb-4")
            ]),
                   
            html.Div([
                
                    html.Div(
                    
                    dash_interactive_graphviz.DashInteractiveGraphviz(
                        id="graph", 
                        style=dict(height="80%", width="80%", display="flex"),
                        #engine='neato',
                        #style=dict(display="flex", flexDirection="column", fit="True", scale="1"),
                        #style={'fit': True, 'scale':'1'},
                        dot_source=config_dict['dash_gviz_start_end'])
                    
                    ),
                    
                    html.Div([
                        
               
                html.H5("Layout engine"),
                dcc.Dropdown(
                    id="engine",
                    value="fdp",
                    options=[
                        dict(label=engine, value=engine)
                        for engine in [
                            "dot",
                            "fdp",
                            "neato",
                            #"circo",
                            #"osage",
                            #"patchwork",
                            #"twopi",
                        ]
                    ],
                ), #end dropdown      
                
                html.P(''),
                html.H5("Selected element"),
                html.Div(id="selection"), 
                        
                        ], style=dict(display="flex", flexDirection="column"),)#end of div
                                    
            ],style=dict(position="absolute", height="100%", width="100%", display="flex"),
                ),#end of upper level div/container
 
            
        ]),     #end of top level container
            
        ]) #end of top level div
      

    elif tab == 'process_model':
        return html.Div([
            
            dbc.Container([
                   
        html.Hr(),
        
        dbc.Row([
            dbc.Col(html.H5(children='This is the process model derived from the workflow data:'
                                     )
                    , className="mb-4")
            ]),

            dbc.Container([
                    
                    html.Div(
                    
                    dash_interactive_graphviz.DashInteractiveGraphviz(
                        id="graph_heu", 
                        style=dict(height="80%", width="80%", display="flex"),
                        #engine='neato',
                        #style=dict(display="flex", flexDirection="column", fit="True", scale="1"),
                        #style={'fit': True, 'scale':'1'},
                        dot_source=config_dict['dash_gviz_heu'])
                    
                    ),
                    
                    html.Div([
                        
                #html.H3("Selected element"),
                html.Div(id="selection_heu"),                    
                        
                        ])
                                    
            ]),#end of container
            
        ]),     #end of top level container
            
        ]) #end of top level div
        

    elif tab == 'social_network':   
        return html.Div([
            
            dbc.Container([
                  
        html.Hr(),
        
        dbc.Row([
            dbc.Col(html.H5(children='This is the "working together" social network of users:'
                                     )
                    , className="mb-4")
            ]),                 
                                html.Div([
                                    
                                                    html.Div([
                        
                #html.H3("Selected element"),
                html.Div(id="selection_cyto"),

                html.Div(id="cyto_info"),                      
                        
                        ]),
                                    
                                    cyto.Cytoscape(
                                        id='cytoscape',
                                        layout={'name': 'preset', 'directed':'True'},
                                        style={'width': '100%', 'height': '900px'},
                                        elements=config_dict['dash_elements'] ,
                                        responsive=True,
                                        stylesheet=[
                                        {
                                            'selector': 'node',
                                            'style': {
                                                'label': 'data(label)',
                                                'width' : '100',
                                                'height' : '100',
                                                'background-color': '#65c5f6',
                                            }
                                        },
                                        
                                         {
                                            'selector': 'labels',
                                            'style': {
                                                'font-size': '18',
                                            }
                                        },       
                                        
                                        {
                                            'selector': 'edge',
                                            'style': {
                                                'curve-style': 'bezier',
                                                'mid-target-arrow-color': '#8f5a86',
                                                'mid-target-arrow-shape': 'vee',
                                                'arrow-scale': '2',
                                                'line-color': '#e8adac',
                                                'width': 'data(weight)'
                                            }
                                            }] #stylesheet end
                                    )
                                ]),
                                



                                    #dcc.Loading(
                                    #    id="loading-4",
                                    #    type="circle",
                                    #    children=[
                                    #        dash_interactive_graphviz.DashInteractiveGraphviz(
                                    #        id="graph_heu",
                                    #        dot_source=gviz_heu.source),                                           
                                    #]),
            
        ]),     #end of top level container   
        
     
    ])#end of top level div
        
        

@app.callback(
    Output('VAT_scatterplot', 'figure'),
    [Input('xaxis', 'value'),
     Input('yaxis', 'value')])
def update_VAT_scatterplot(xaxis_name, yaxis_name):
    df_VAT = config_dict['dash_df_VAT']
    return {
        'data': [go.Scatter(
            x=df_VAT[df_VAT['Audit results']=='No error'][xaxis_name],
            y=df_VAT[df_VAT['Audit results']=='No error'][yaxis_name],
            #text=df['RO Position Local Key'],
            text = df_VAT['RO Position Local Key'].map(str) + " / " + df_VAT['RO Cashing Cashed Date'].dt.strftime('%Y-%m-%d'),

            name = 'No errors',
            showlegend = True,

            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'color' : list(df_VAT[df_VAT['Audit results']=='No error']['Audit classification']),
                'line': {'width': 0.5, 'color': 'white'}
            }
        ),
            
            #in normal plotly, you have to add each trace separately if you want to have a legend. quite painful
            go.Scatter(
            x=df_VAT[df_VAT['Audit results']=='Warning'][xaxis_name],
            y=df_VAT[df_VAT['Audit results']=='Warning'][yaxis_name],
            #text=df['RO Position Local Key'],
            text = df_VAT['RO Position Local Key'].map(str) + " / " + df_VAT['RO Cashing Cashed Date'].dt.strftime('%Y-%m-%d'),

            name = 'Warning',
            showlegend = True,

            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'color' : list(df_VAT[df_VAT['Audit results']=='Warning']['Audit classification']),
                'line': {'width': 0.5, 'color': 'white'}
            }
        ),
            
            go.Scatter(
            x=df_VAT[df_VAT['Audit results']=='Error'][xaxis_name],
            y=df_VAT[df_VAT['Audit results']=='Error'][yaxis_name],
            #text=df['RO Position Local Key'],
            text = df_VAT['RO Position Local Key'].map(str) + " / " + df_VAT['RO Cashing Cashed Date'].dt.strftime('%Y-%m-%d'),

            name = 'Error',
            showlegend = True,

            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'color' : list(df_VAT[df_VAT['Audit results']=='Error']['Audit classification']),
                'line': {'width': 0.5, 'color': 'white'}
            }
        ),
            
            
            ],
        'layout': go.Layout(
            xaxis={'title': xaxis_name.title()},
            yaxis={'title': yaxis_name.title()},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
            #text='Legend title',

        ),
        
    }

@app.callback(
    Output('GNI_scatterplot', 'figure'),
    [Input('xaxis', 'value'),
     Input('yaxis', 'value')])
def update_GNI_scatterplot(xaxis_name, yaxis_name):
    df_GNI = config_dict['dash_df_GNI']
    colorsIdx = {'No error': '#1f77b4', 'Warning': '#ff7f0e', 'Error': '#d62728'}
    return {
        'data': [go.Scatter(
            x=df_GNI[xaxis_name],
            y=df_GNI[yaxis_name],
            #text=df['RO Position Local Key'],
            text = df_GNI['RO Position Local Key'].map(str) + " / " + df_GNI['RO Cashing Cashed Date'].dt.strftime('%Y-%m-%d'),

            name = 'No errors',
            showlegend = True,

            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'color' : list(df_GNI['Audit results'].map(colorsIdx)),
                'line': {'width': 0.5, 'color': 'white'}
            }
        ),
            
            #in normal plotly, you have to add each trace separately if you want to have a legend. quite painful
            go.Scatter(
            x=df_GNI[df_GNI['Audit results']=='Warning'][xaxis_name],
            y=df_GNI[df_GNI['Audit results']=='Warning'][yaxis_name],
            #text=df['RO Position Local Key'],
            text = df_GNI['RO Position Local Key'].map(str) + " / " + df_GNI['RO Cashing Cashed Date'].dt.strftime('%Y-%m-%d'),

            name = 'Warning',
            showlegend = True,

            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'color' : list(df_GNI[df_GNI['Audit results']=='Warning']['Audit classification']),
                'line': {'width': 0.5, 'color': 'white'}
            }
        ),
            
            go.Scatter(
            x=df_GNI[df_GNI['Audit results']=='Error'][xaxis_name],
            y=df_GNI[df_GNI['Audit results']=='Error'][yaxis_name],
            #text=df['RO Position Local Key'],
            text = df_GNI['RO Position Local Key'].map(str) + " / " + df_GNI['RO Cashing Cashed Date'].dt.strftime('%Y-%m-%d'),

            name = 'Error',
            showlegend = True,

            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'color' : list(df_GNI[df_GNI['Audit results']=='Error']['Audit classification']),
                'line': {'width': 0.5, 'color': 'white'}
            }
        ),
            
            ],
        'layout': go.Layout(
            #title={'text': 'GNI data for 2020'},
            xaxis={'title': xaxis_name.title()},
            yaxis={'title': yaxis_name.title()},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }



@app.callback(
    Output('VAT_vs_GNI', 'figure'),
    [Input('xaxis', 'value'),
     Input('yaxis', 'value')])
def update_VAT_graph(xaxis_name, yaxis_name):
    df2 = config_dict['dash_df2']
    
    #calculating the regression line manually for 
    from sklearn.model_selection import train_test_split
    from sklearn import linear_model

    try:
        X = np.array(df2.VAT).reshape(-1,1)
        #Y = np.array(df2.GNI).reshape(-1,1)
        X_train, X_test, y_train, y_test = train_test_split(X, df2.GNI, random_state=42)
        
        model = linear_model.LinearRegression()
        model.fit(X_train, y_train)
        
        x_range = np.linspace(X.min(), X.max(), 100)
        y_range = model.predict(x_range.reshape(-1, 1))
    except:
        x_range = 1
        y_range = 1
    
    return {
        'data': [go.Scatter(
            x=df2['VAT'],
            y=df2['GNI'],
            #text=df['RO Position Local Key'],
            text = df2['MS'],
            #trendline = 'ols',
            textposition='top right',
            mode='markers+text',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        ),
            go.Scatter(x=x_range, y=y_range)
           ],
        'layout': go.Layout(
            xaxis={'title': 'VAT'},
            yaxis={'title': 'GNI'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
            showlegend = False
        )
    }

@app.callback(Output("selection", "children"), [Input("graph", "selected_node"), Input("graph", "selected_edge")])
def show_selected(node, edge):
    eventlog = config_dict['dash_eventlog']
    node_count = eventlog[eventlog['concept:name']==node]
    #edge info is not used yet
    #edge_count = eventlog[eventlog['concept:name']==edge]
    node_msg = '\n' + str(len(node_count)) + ' out of ' + str(len(eventlog['case:concept:name'].unique())) + ' cases'
    #return [node, edge, node_msg]
    if node:
        return [html.P(node), html.P(node_msg)]

@app.callback(Output("selection_heu", "children"), [Input("graph_heu", "selected_node"), Input("graph_heu", "selected_edge")])
def show_selected_heu(node, edge):
    return [node, edge]

@app.callback(
    [Output("selection_cyto", "children"),Output("cyto_info", "children"),], 
    #[Input("cytoscape", "selectedNodeData"), Input("cytoscape", "selectedEdgeData")])
    [Input("cytoscape", "tapNodeData"), Input("cytoscape", "tapEdgeData")])
def show_selected_cyto(node, edge):
    #we don't use the edges at this point, maybe later
    eventlog = config_dict['dash_eventlog']
    basic_info = str(node)# + ' / ' + str(edge)
    try:
        extended_info = 'Involved in ' + str(len(eventlog[eventlog['org:resource']==node['label']]['case:concept:name'].unique())) + ' / ' +str(len(eventlog['case:concept:name'].unique())) + ' cases'
    except:
        extended_info = ''
    return basic_info, extended_info

@app.callback(
    Output("graph", "engine"),
    Input("engine", "value"),
)
def display_output(value):
    return value

@app.callback(
    Output("onload_output", "children"),
    Trigger("onload", "children"))
def load_df(onload):    
    
    #reload the key-value store, otherwise it won't update the cached version, it seems
    config_dict = SqliteDict('./config/config_db.sqlite', autocommit=True)
    
    a = '\n '
    for key in config_dict:
        a = a + key + ' ->  ' + str(config_dict[key]) + '\n \n'
    return ''#a

#if __name__ == '__main__':
#    app.run_server()
