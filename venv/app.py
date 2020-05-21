import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
import random
from collections import deque
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pandas_datareader.data as web
import pandas as pd
import plotly.subplots as splots
import csv
from itertools import zip_longest as zip
import pyodbc
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=localhost;"
                      "Database=HamiltonVectorDB_e2f1e32cb3594605886d645ab4c4e8e5;"
                      "Trusted_Connection=yes;")



with open("C:\\Program Files (x86)\\HAMILTON\LogFiles\\Normal_Starlet_a8bbe6d7256c4704845244ab98e1a631_Trace.trc", 'r') as in_file:
    stripped = (line.strip() for line in in_file)
    lines = (line for line in stripped if line)
    grouped = zip(*[lines] * 3)
    with open('extracted.csv', 'w') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(('title', 'intro', 'tagline'))
        writer.writerows(grouped)

app = dash.Dash()
app.layout = html.Div(children=[
    html.Div(children='''
Pick a Hamilton
    '''),
    dcc.Dropdown(
        id='input',
        options=[
            {'label': 'C034', 'value': 'C034'},
            {'label': 'D363', 'value': 'D363'},
            {'label': 'HAM1', 'value': 'HAM1'}
        ],
        value='HAM1'
    ),
    html.Div(id='output-graph')

])

@app.callback(
    Output(component_id='output-graph',component_property='children'),
    [Input(component_id='input',component_property='value')]
    )

def update_graph(input_data):
    df_v = pd.read_sql_query('select * from HxActionMoveVolume where TargetLabwareVolume > 0', cnxn)
    df_t = pd.read_sql_query('select * from HxAction', cnxn)
    fig = splots.make_subplots(rows=1, cols=1, shared_xaxes=True,vertical_spacing=0.009,horizontal_spacing=0.009)
    fig['layout']['margin'] = {'l': 30, 'r': 10, 'b': 50, 't': 25}

    fig.append_trace({'x':df_t.ActionTime,'y':df_v.Volume,'type':'scatter','name':'Actual'},1,1)
    fig.append_trace({'x':df_t.ActionTime,'y':df_v.TargetLabwareVolume,'type':'scatter','name':'Target'},1,1)
    fig['layout'].update(title='Delivery Amounts')

    return dcc.Graph(
        id='example-graph',
        figure=fig
    )

if __name__ == "__main__":
    app.run_server(debug=True)
