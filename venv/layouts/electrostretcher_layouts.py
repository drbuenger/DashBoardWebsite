import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from components import Header, read_trace_file
from datetime import datetime as dt
from datetime import date, timedelta
import pandas as pd
import os
import shutil
import pyodbc
import plotly.express as px

storage_location = 'C:\\Users\\dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\data'


# Read in Data
stretcher_files = ["\\\janetjackson-pc\C$\\NanoFluidics\LogData\Blue",
                   "\\\janetjackson-pc\C$\\NanoFluidics\LogData\Green",
                   "\\\janetjackson-pc\C$\\NanoFluidics\LogData\Red",
                   "\\\janetjackson-pc\C$\\NanoFluidics\LogData\Yellow",
                   "\\\\NANO-WIN7MFG1\C$\\NanoFluidics\LogData\Pink",
                   "\\\\NANO-WIN7MFG1\C$\\NanoFluidics\LogData\Green",
                   "\\\\NANO-WIN7MFG1\C$\\NanoFluidics\LogData\Purple",
                   "\\\\MFG-PC-010\C$\\NanoFluidics\LogData\Gray",
                   "\\\\MFG-PC-010\C$\\NanoFluidics\LogData\White"
                   ]

# r=root, d=directories, f = files
for folder in stretcher_files:
    try:
        es_color_dict = {'label': 'Blue', 'value': 'Blue'}
        es_color_list = ['Blue']
        path_split = folder.split("\\")
        length_split = len(path_split)
        es_color = path_split[length_split - 1]
        if es_color not in es_color_list:
            es_color_dict.update({'label': es_color, 'value': es_color})
            es_color_list.append(es_color)
        y = [os.path.join(r, file) for r, d, f in os.walk(folder) for file in f]
    except:
        print("Folder not Found: " + folder)
    for z in y:
        file_split = z.split("\\")
        count = len(file_split)
        destination = storage_location + "\\ES\\" + es_color + "\\" + file_split[count - 1]
        if z.endswith(".CSV") and not os.path.exists(destination):
            shutil.copy2(z, destination)

stretcher_summary = ['Stretcher',
                     'Lane 1 (uA)',
                     'Lane 1 (V)',
                     'Lane 2 (uA)',
                     'Lane 2 (V)',
                     'Lane 3 (uA)',
                     'Lane 3 (V)',
                     'Lane 4 (uA)',
                     'Lane 4 (V)',
                     'Lane 5 (uA)',
                     'Lane 5 (V)',
                     'Lane 6 (uA)',
                     'Lane 6 (V)',
                     'Total']

stretcher_table = ['Stretcher',
                   'Lane 1 (uA)',
                   'Lane 1 (V)',
                   'Lane 2 (uA)',
                   'Lane 2 (V)',
                   'Lane 3 (uA)',
                   'Lane 3 (V)',
                   'Lane 4 (uA)',
                   'Lane 4 (V)',
                   'Lane 5 (uA)',
                   'Lane 5 (V)',
                   'Lane 6 (uA)',
                   'Lane 6 (V)',
                   'Date and Time']






######################## START ElectroStretcher Category Layout ########################
layout_stretcher = html.Div([
    html.Div([
        # CC Header
        Header(),
        # Date Picker
        html.Div(children='''
    Pick a Start/End Date
    '''),
        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range-stretcher',
                with_portal=True,
                min_date_allowed=dt(2016, 1, 1),
                max_date_allowed=date.today(),
                initial_visible_month=dt(date.today().year, date.today().month, 1),
                end_date=date.today(),
                start_date=(date.today() - timedelta(3)),
            )
        ], className="row ", style={'marginTop': 0, 'marginBottom': 15, 'marginLeft': 0}),
        html.Div(children='''
    Stretching By Color
    '''),
        html.Div([
            dash_table.DataTable(
                id='datatable-stretcher-summary',
                columns=[{"name": i, "id": i} for i in stretcher_summary],
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto'},
                sort_action="native",
                tooltip_duration=None,
                style_cell={"fontFamily": "Arial",
                            "size": 11, 'textAlign': 'left',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0,
                            },
                style_header={
                    'whiteSpace': 'normal',
                    'height': 'auto'},
                style_cell_conditional=[
                    {'if': {'column_id': 'Stretcher'},
                     'width': '5%'}],
                css=[{'selector': '.dash-cell div.dash-cell-value',
                      'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                     {'selector': '.row', 'rule': 'margin: 0'}],
            ),
        ], className=" twelve columns", style={'marginTop': 0, 'marginBottom': 15}),

        html.Div(children='''
    Electrostretcher History
    '''),
        html.Div(children='''
Select Stretchers
'''),
        html.Div([dcc.Checklist(
            id='stretcher-color-select',
            options=[
                {'label': 'Blue  ', 'value': 'Blue'},
                {'label': 'Red', 'value': 'Red'},
                {'label': 'Green', 'value': 'Green'},
                {'label': 'Yellow', 'value': 'Yellow'},
                {'label': 'Purple', 'value': 'Purple'},
                {'label': 'Pink', 'value': 'Pink'},
                {'label': 'Gray', 'value': 'Gray'},
                {'label': 'White', 'value': 'White'},
            ],
            value=['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Pink', 'Gray', 'White'],
            labelStyle={'display': 'block'}
        )]),

        # First Data Table
        html.Div([
            dash_table.DataTable(
                id='datatable-stretcher-table',
                columns=[{"name": i, "id": i} for i in stretcher_table],
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto', },
                row_selectable='single',
                selected_rows=[0],
                sort_action="native",
                tooltip_duration=None,
                style_cell={"fontFamily": "Arial",
                            "size": 11, 'textAlign': 'left',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0,
                            },
                style_header={
                    'whiteSpace': 'normal',
                    'height': 'auto'},
                style_cell_conditional=[
                    {'if': {'column_id': 'Stretcher'},
                     'width': '5%'}
                ],
                css=[{'selector': '.dash-cell div.dash-cell-value',
                      'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                     {'selector': '.row', 'rule': 'margin: 0'}],
                style_data_conditional=[{
                    'if': {
                        'filter_query': '{Lane 1 (uA)} < 400',
                        'column_id': 'Lane 1 (uA)'},
                    'backgroundColor': '#FF4136',
                    'fontWeight': 'bold'},
                    {'if': {
                        'filter_query': '{Lane 2 (uA)} < 400',
                        'column_id': 'Lane 2 (uA)'},
                        'backgroundColor': '#FF4136',
                        'fontWeight': 'bold'},
                    {'if': {
                        'filter_query': '{Lane 3 (uA)} < 400',
                        'column_id': 'Lane 3 (uA)'},
                        'backgroundColor': '#FF4136',
                        'fontWeight': 'bold'},
                    {'if': {
                        'filter_query': '{Lane 4 (uA)} < 400',
                        'column_id': 'Lane 4 (uA)'},
                        'backgroundColor': '#FF4136',
                        'fontWeight': 'bold'},
                    {'if': {
                        'filter_query': '{Lane 5 (uA)} < 400',
                        'column_id': 'Lane 5 (uA)'},
                        'backgroundColor': '#FF4136',
                        'fontWeight': 'bold'},
                    {'if': {
                        'filter_query': '{Lane 6 (uA)} < 400',
                        'column_id': 'Lane 6 (uA)'},
                        'backgroundColor': '#FF4136',
                        'fontWeight': 'bold', },
                    {'if': {
                        'filter_query': '{Lane 1 (V)} < 140',
                        'column_id': 'Lane 1 (V)'},
                        'backgroundColor': '#FF4136',
                        'fontWeight': 'bold'},
                    {'if': {
                        'filter_query': '{Lane 2 (V)} < 140',
                        'column_id': 'Lane 2 (V)'},
                        'backgroundColor': '#FF4136',
                        'fontWeight': 'bold'},
                    {'if': {
                        'filter_query': '{Lane 3 (V)} < 140',
                        'column_id': 'Lane 3 (V)'},
                        'backgroundColor': '#FF4136',
                        'fontWeight': 'bold'},
                    {'if': {
                        'filter_query': '{Lane 4 (V)} < 140',
                        'column_id': 'Lane 4 (V)'},
                        'backgroundColor': '#FF4136',
                        'fontWeight': 'bold'},
                    {'if': {
                        'filter_query': '{Lane 5 (V)} < 140',
                        'column_id': 'Lane 5 (V)'},
                        'backgroundColor': '#FF4136',
                        'fontWeight': 'bold'},
                    {'if': {
                        'filter_query': '{Lane 6 (V)} < 140',
                        'column_id': 'Lane 6 (V)'},
                        'backgroundColor': '#FF4136',
                        'fontWeight': 'bold'}
                ]

            ),
        ], className="datatable-hamilton", style={'marginTop': 0, 'marginBottom': 15}),
        html.Div([

            dcc.Graph(id='es-graph',
                      figure=px.line()),
        ], className=" twelve columns"

        ),
    ], className="subpage")
], className="page")

######################## END ElectroStretcher Category Layout ########################