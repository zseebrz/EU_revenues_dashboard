#######
# Here we'll use the mpg.csv dataset to demonstrate
# how multiple inputs can affect the same graph.
######
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_table as dt

import plotly.graph_objects as go
import pandas as pd

from app import app

from pm4py.objects.conversion.log import converter as log_converter

from pm4py.algo.discovery.dfg import algorithm as dfg_discovery## Import the dfg visualization object
from pm4py.visualization.dfg import visualizer as dfg_visualization#Create graph from log

from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
#from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
#from pm4py.visualization.petri_net import visualizer as pn_visualizer

## Import the dfg_discovery algorithm
#from pm4py.algo.discovery.dfg import algorithm as dfg_discovery## Import the dfg visualization object
#from pm4py.visualization.dfg import visualizer as dfg_visualization#Create graph from log

from pm4py.algo.organizational_mining.sna import algorithm as sna
#from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
#from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
#from pm4py.visualization.petri_net import visualizer as pn_visualizer
import pm4py
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
config_dict = SqliteDict('./config/config_db.sqlite', autocommit=True)

RESULTS_FOLDER = config_dict['RESULTS_FOLDER'] 
UPLOADS_DW_FOLDER = config_dict['UPLOADS_DW_FOLDER']

if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)

try:
    df = pd.read_excel(config_dict['RESULT_FILE'])
except:
    df = pd.DataFrame()

try:
    
    #rudimentary way of getting the RO extract filename from the upploads DW folder
    for filename in os.listdir(UPLOADS_DW_FOLDER):
        path = os.path.join(UPLOADS_DW_FOLDER, filename)
        if os.path.isfile(path):
            RO_extract = path
    
    #RO_extract = './uploads/dw/RO_2020_w_txt_fields.xlsx'
    
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
    
    #heu_net = heuristics_miner.apply_heu(log)
    #gviz_heu = hn_visualizer.apply(heu_net)
    #hn_visualizer.view(gviz_heu)
        
    #a peculiar way to insantiate the parameters object, took a while to understand
    dfg_parameters = dfg_discovery.Variants.PERFORMANCE.value.Parameters
    parameters = get_properties(log)
    #parameters[dfg_parameters.FORMAT] = format
    aggregationMeasure = "max"
    aggregation_measure = "max"
    parameters[dfg_parameters.AGGREGATION_MEASURE] = aggregationMeasure
    
    dfg = dfg_discovery.apply(log)# Visualise
    dfg_perf = dfg_discovery.apply(log, parameters=parameters, variant=dfg_discovery.Variants.PERFORMANCE)
    
    
    
    dfg_1, start_activities, end_activities = pm4py.discover_dfg(log)
    
    
    #a peculiar way to insantiate the parameters object, took a while to understand
    dfg_parameters = dfg_visualization.Variants.FREQUENCY.value.Parameters
    parameters = get_properties(log)
    #parameters[dfg_parameters.FORMAT] = format
    parameters[dfg_parameters.START_ACTIVITIES] = start_activities
    parameters[dfg_parameters.END_ACTIVITIES] = end_activities
    
    gviz_start_end = dfg_visualization.apply(dfg, log=log, parameters=parameters,
                                             variant=dfg_visualization.Variants.FREQUENCY)
    
    gviz_start_end = gviz_start_end.source
    #pm4py.view_dfg(dfg_1, start_activities, end_activities)
    
    dfg_parameters = dfg_visualization.Variants.PERFORMANCE.value.Parameters
    parameters = get_properties(log)
    #parameters[dfg_parameters.FORMAT] = format
    parameters[dfg_parameters.START_ACTIVITIES] = start_activities
    parameters[dfg_parameters.END_ACTIVITIES] = end_activities
    #sojourn time also doesn't work, there is no start and end time stamp
    #parameters[dfg_parameters.START_TIMESTAMP_KEY] = 'time:start_timestamp'
    #doesn't work, maybe we have an older version, need to check
    #parameters[dfg_parameters.AGGREGATION_MEASURE] = aggregation_measure
    
    gviz_start_end_perf = dfg_visualization.apply(dfg, log=log, parameters=parameters,
                                             variant=dfg_visualization.Variants.PERFORMANCE)
    
    gviz = dfg_visualization.apply(dfg, log=log, variant=dfg_visualization.Variants.FREQUENCY)
    gviz_perf = dfg_visualization.apply(dfg, log=log, variant=dfg_visualization.Variants.PERFORMANCE)
    
    heu_net = heuristics_miner.apply_heu(log, parameters={heuristics_miner.Variants.CLASSIC.value.Parameters.DEPENDENCY_THRESH: 0.99})
    gviz_heu = hn_visualizer.apply(heu_net)
    
    gviz_heu.write("heu_graph.txt")
    
    #convoluted way to get the dotfile as a struing
    with open("heu_graph.txt","r") as f:
        gviz_heu = f.read()
        

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


    
except:
    gviz = None
    gviz_start_end = None 
    elements = None
    gviz_heu = None

"""
df = df[['authorising_officer', 'RO Cashed Payment Amount (Eur)_pos']]

df.columns = ['officer', 'cashed']
"""

features = df.columns

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
    2
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

except:

    df_errors = pd.DataFrame()
    df_warnings = pd.DataFrame()
    df_risks = pd.DataFrame()
    df2 = pd.DataFrame()
    
#errors = df_errors.to_dict('records')
#warnings = df_warnings.to_dict('records')

layout =     dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("GNI and VAT revenue checks dashboard", className="text-center")
                    , className="mb-5 mt-5")
        ]),


        html.Div([
    
        dcc.Tabs([
            

        dcc.Tab(label='Error analysis', children=[
 
        html.Hr(),
        
        dbc.Row([
            dbc.Col(html.H4(children='An overview of audit errors and warnings (red flags) found for GNI/VAT:'
                                     )
                    , className="mb-4")
            ]),
 
        dbc.Row([
            dbc.Col(html.H5(children='Errors'
                                     )
                    , className="mb-5")
            ]),
                  
            dbc.Container([
                    
                        html.Div(dt.DataTable(columns=[{"name": i, "id": i} for i in df_errors.columns], 
                                              data=df_errors.to_dict('records'), 
                                              id='table_errors',
                                              style_table={'overflowX': 'auto'},))
                                    
            ]),#end of container

            html.Br(),

            dbc.Row([
            dbc.Col(html.H5(children='Warnings'
                                     )
                    , className="mb-5")
            ]),
    
            dbc.Container([
                    
                        html.Div(dt.DataTable(columns=[{"name": i, "id": i} for i in df_warnings.columns], 
                                              data=df_warnings.to_dict('records'), 
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
                    
                        html.Div(dt.DataTable(columns=[{"name": i, "id": i} for i in df_risks.columns], 
                                              data=df_risks.to_dict('records'), 
                                              id='table_risks',
                                              style_table={'overflowX': 'auto'},))
                                    
            ]),#end of container
            
        ]),     #end of tab               

            

        
        dcc.Tab(label='Visual Analytics', children=[

        html.Hr(), 

        dbc.Row([
            dbc.Col(html.H4(children='Please choose the fields to be analysed from the drop-down list'
                                     )
                    , className="mb-4"),
            ]),#end of row

            html.Div([
            dcc.Dropdown(
                id='xaxis',
                options=[{'label': i.title(), 'value': i} for i in features],
                value='MS'
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='yaxis',
                options=[{'label': i.title(), 'value': i} for i in features],
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
            ), #end of tab
        
        dcc.Tab(label='Actual Process', children=[
 
        html.Hr(),
        
        dbc.Row([
            dbc.Col(html.H5(children='This is how the process looks like in real life:'
                                     )
                    , className="mb-4")
            ]),
                   
            dbc.Container([
                    
                    dash_interactive_graphviz.DashInteractiveGraphviz(
                        id="graph", 
                        style=dict(height="80%", width="80%", display="flex"),
                        #style=dict(display="flex", flexDirection="column", fit="True", scale="1"),
                        #style={'fit': True, 'scale':'1'},
                        dot_source=gviz_start_end)
                                    
            ]),#end of container
 
            
        ]),     #end of tab   
      
        dcc.Tab(label='Process Model', children=[
                    
        html.Hr(),
        
        dbc.Row([
            dbc.Col(html.H5(children='This is the process model derived from the workflow data:'
                                     )
                    , className="mb-4")
            ]),
                                   
                    dash_interactive_graphviz.DashInteractiveGraphviz(
                        id="graph_heu", 
                        style=dict(height="80%", width="80%", display="flex"),
                        #style={'fit':'True'},
                        dot_source=gviz_heu)
            
        ]),     #end of tab   
        


        dcc.Tab(label='Social Network Analysis', children=[
                    
        html.Hr(),
        
        dbc.Row([
            dbc.Col(html.H5(children='This is the "working together" social network of users:'
                                     )
                    , className="mb-4")
            ]),
                 
                                html.Div([
                                    cyto.Cytoscape(
                                        id='cytoscape',
                                        layout={'name': 'preset', 'directed':'True'},
                                        style={'width': '100%', 'height': '900px'},
                                        elements=elements,
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
                                ])   


                                    #dcc.Loading(
                                    #    id="loading-4",
                                    #    type="circle",
                                    #    children=[
                                    #        dash_interactive_graphviz.DashInteractiveGraphviz(
                                    #        id="graph_heu",
                                    #        dot_source=gviz_heu.source),                                           
                                    #]),
            
        ]),     #end of tab   
        
        
            ])#tabs
        
        ],
    style={'padding':10})
     
    ])#end of container
        

@app.callback(
    Output('VAT_scatterplot', 'figure'),
    [Input('xaxis', 'value'),
     Input('yaxis', 'value')])
def update_VAT_scatterplot(xaxis_name, yaxis_name):
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
@app.callback(
    Output('VAT_vs_GNI', 'figure'),
    [Input('xaxis', 'value'),
     Input('yaxis', 'value')])
def update_VAT_graph(xaxis_name, yaxis_name):
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

#if __name__ == '__main__':
#    app.run_server()
