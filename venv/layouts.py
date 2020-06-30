import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import numpy as np
from components import Header, print_button, read_trace_file
from datetime import datetime as dt
from datetime import date, timedelta
import time

import pandas as pd
import os
import csv
import shutil
import pyodbc
from dateutil.relativedelta import relativedelta

# Read in Data
hamilton_computers = ["\\\HAMILTON08\C$\Program Files\Hamilton\LogFiles",
                      "\\\ZORRANDER\C$\Program Files\Hamilton\LogFiles",
                      "\\\MTGREENMTN\C$\Program Files\Hamilton\LogFiles",
                      "\\\MFG-00000833\C$\Program Files\Hamilton\LogFiles",
                      "\\\SANCHEZ\C$\Program Files\Hamilton\LogFiles"]

storage_location = 'C:\\Users\\dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\data'
# r=root, d=directories, f = files
x = []
for pc in hamilton_computers:
    path_split = pc.split("\\")
    pc_name = path_split[2]
    y = [os.path.join(r,file) for  r,d,f in os.walk(pc) for file in f]
    for z in y:
        file_split = z.split("\\")
        count = len(file_split)
        destination = storage_location + "\\" + pc_name +"\\" + file_split[count-1]
        if z.endswith(".trc") and not os.path.exists(destination):
            shutil.copy2(z,destination)
            x.append(destination)
for file in x:
    if file.endswith(".trc"):
        read_trace_file(file)

df = pd.read_csv('C:\\Users\\dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\data\\Hamilton.csv',
                 na_values=['Null','NA','nan'],
                 keep_default_na=False)
df.dropna(axis=0, inplace=True)


df['Time Start'] = pd.to_datetime(df['Time Start'])
df['Time End'] = pd.to_datetime(df['Time End'])
df['Time End'] = pd.to_datetime(df['Time End'])
df['Duration'] = df['Time End'].sub(df['Time Start']).dt.total_seconds().div(60)
df = df.drop(columns=['Tips Used 50uL','Tips Used 300uL'])
df = df.loc[(df!=0).any(axis=1)]
df = df[df['Serial Number'] != '0']
df = df[df['Serial Number'] != '0000']
df = df.rename(columns={'Tips Used 1000uL': 'Tips Used'})
unique_serial_numbers = df['Serial Number'].unique()

dt_columns = ['Method Name','Time Start', 'Time End', 'User Name', 'Tips Used',  'Duration', 'Aborted', 'File Name']

dt_columns_time = ['Method Name','Dispensing Time','Dispensing Count','Aspirating Time','Aspirating Count', 'Tip Pickup Time','Tip Pickup Count', 'Tip Eject Time','Tip Eject Count', 'User Time','User Count']

conditional_columns = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name']

dt_columns_total = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name' ]

df_columns_calculated = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name' ]

conditional_columns_calculated_calculated =['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name' ]

summary_columns = ['Method Name', 'Total', 'Average', 'TipsUsed', 'Success %']
summary_columns_time = ['Method Name', 'Average Dispense', 'Average Aspirate', 'Average Pickup', 'Average Eject', 'Average User']
summary_columns_time2 = ['Method Name', '% Dispense', '% Aspirate', '% Pickup', '% Eject', '% User', 'Average Total Time (min)']
ham_detail_columns= ['Time Since Start (sec)','Step Type', 'Message']

#Read in BarTender data
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=labels-internal\BARTENDER;"
                      "Database=BarTender_UNREG;"
                      "Trusted_Connection=yes;")

bt_df = pd.read_sql_query('SELECT btff.Name , p.Name as PrinterName, btp.TotalLabels, btp.CreatedDateTime FROM BtPrintJobs btp \
inner join BtFormatFileNames btff on btp.FormatFileNameID = btff.FileNameID \
inner join Printers p on btp.PrinterID = p.PrinterID', cnxn)
bt_df['CreatedDateTime']= bt_df['CreatedDateTime'] - 621355968000000000
bt_df['CreatedDateTime']= bt_df['CreatedDateTime']/10
bt_df['CreatedDateTime'] = pd.to_datetime(bt_df['CreatedDateTime'],unit='us')
bt_df['Server'] = 'Internal'


#Read in BarTender data
cnxn2 = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=lbl-controlled\BARTENDER_REG;"
                      "Database=BarTender_REG;"
                      "Trusted_Connection=yes;")

bt_df2 = pd.read_sql_query('SELECT btff.Name, p.Name as PrinterName, btp.TotalLabels, btp.CreatedDateTime \
FROM [BarTender_REG].[dbo].[BtPrintJobs] btp \
inner join [BarTender_REG].[dbo].BtFormatFileNames btff on btp.FormatFileNameID = btff.FileNameID \
inner join [BarTender_REG].[dbo].[Printers] p on btp.PrinterID = p.PrinterID', cnxn2)
bt_df2['CreatedDateTime']= bt_df2['CreatedDateTime'] - 621355968000000000
bt_df2['CreatedDateTime']= bt_df2['CreatedDateTime']/10
bt_df2['CreatedDateTime'] = pd.to_datetime(bt_df2['CreatedDateTime'],unit='us')
bt_df2['Server'] = 'Controlled'

bartender_summary = ['PrinterName', 'Total', 'LastUsed']
bartender_summary2 =  ['Name', 'Total', 'LastUsed']
bartender_table = ['PrinterName', 'Name', 'TotalLabels', 'Print Time', 'Server']

bt_df = bt_df.append(bt_df2)



# Read in Data
stretcher_files = ["\\\janetjackson-pc\C$\\NanoFluidics\LogData\Blue",
                      "\\\janetjackson-pc\C$\\NanoFluidics\LogData\Green",
                      "\\\janetjackson-pc\C$\\NanoFluidics\LogData\Red",
                      "\\\janetjackson-pc\C$\\NanoFluidics\LogData\Yellow"]

# r=root, d=directories, f = files
for folder in stretcher_files:
    path_split = folder.split("\\")
    es_color = path_split[6]
    y = [os.path.join(r,file) for  r,d,f in os.walk(folder) for file in f]
    for z in y:
        file_split = z.split("\\")
        count = len(file_split)
        destination = storage_location + "\\ES\\" + es_color +"\\" + file_split[count-1]
        if z.endswith(".CSV") and not os.path.exists(destination):
            shutil.copy2(z,destination)

stretcher_summary = ['Stretcher', 'Lane 1 (uA)', 'Lane 1 (V)', 'Lane 2 (uA)', 'Lane 2 (V)', 'Lane 3 (uA)', 'Lane 3 (V)', 'Lane 4 (uA)', 'Lane 4 (V)', 'Lane 5 (uA)', 'Lane 5 (V)', 'Lane 6 (uA)', 'Lane 6 (V)', 'Total']
stretcher_table = ['Stretcher', 'Lane 1 (uA)', 'Lane 1 (V)', 'Lane 2 (uA)', 'Lane 2 (V)', 'Lane 3 (uA)', 'Lane 3 (V)', 'Lane 4 (uA)', 'Lane 4 (V)', 'Lane 5 (uA)', 'Lane 5 (V)', 'Lane 6 (uA)', 'Lane 6 (V)', 'Date and Time']

######################## START Hamilton Category Layout ########################
layout_hamilton = html.Div([

    #    print_button(),

    html.Div([
        # CC Header
        Header('100000'),
        # Date Picker
html.Div(children='''
    Pick a Start/End Date
    '''),
        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range-hamilton-category',
                with_portal=True,
                min_date_allowed=dt(2018, 1, 1),
                max_date_allowed=df['Time End'].max().to_pydatetime(),
                initial_visible_month=dt(df['Time End'].max().to_pydatetime().year, df['Time End'].max().to_pydatetime().month, 1),
                end_date=df['Time End'].max().to_pydatetime(),
                start_date=(df['Time Start'].max() - timedelta(6)).to_pydatetime(),
            )
        ], className="row ", style={'marginTop': 0, 'marginBottom': 15, 'marginLeft': 0}),
    html.Div(children='''
    Pick a Hamilton
    '''),
        html.Div([
            dcc.Dropdown(
                id='dropdown-input-hamilton',
                style={'maxWidth': '300px'},
                options=[{'label': i, 'value': i} for i in unique_serial_numbers],
                value=unique_serial_numbers[0],
            )
        ], style={'marginTop': 0, 'marginBottom': 15}),

html.Div(children='''
    Summary Data
    '''),
        html.Div([
            dash_table.DataTable(
                id='datatable-hamilton-summary',
                columns=[{"name": i, "id": i} for i in summary_columns],
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto',},
                sort_action="native",
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in df.to_dict('rows')
                ],
                tooltip_duration=None,
                style_cell={
                            "fontFamily": "Arial",
                            "size": 11, 'textAlign': 'left',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0,
                            },
                style_header={
                    'whiteSpace': 'normal',
                    'height': 'auto'},
                style_cell_conditional=[
                    {'if': {'column_id': 'Method Name'},
                     'width': '20%'}],
                css=[{'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                     {'selector': '.row', 'rule': 'margin: 0'}],
            ),
        ], className=" twelve columns", style={'marginTop': 0, 'marginBottom': 15}),
html.Div(children='''
    Hamilton Data by Serial Number
    ''',
         ),

        dbc.Button("Run Detail Page", id="run-detail-button"),

        dbc.Modal(
            [
                dbc.ModalHeader("Hamilton Method Detail Page"),
                dbc.ModalBody(html.Div([
                    dash_table.DataTable(
                        id='run-detail-data',
                        columns=[{"name": i, "id": i} for i in ham_detail_columns],
                        style_table={'maxWidth': '1400px',
                             'overflowX': 'auto',},
                        sort_action="native",
                        selected_rows=[],
                        style_cell={
                            "fontFamily": "Arial",
                            "size": 11, 'textAlign': 'left',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0,
                            },
                        style_header={
                            'whiteSpace': 'normal',
                            'height': 'auto'},
                        style_cell_conditional=[
                            {
                                'if': {
                                    'column_id': 'Method Name'
                                },
                             'width': '15%'
                            },

                        ],
                        css=[{'selector': '.dash-cell div.dash-cell-value',
                             'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                             {'selector': '.row', 'rule': 'margin: 0'}],
            ),
        ], className=" twelve columns", style={'marginTop': 0, 'marginBottom': 15}),),
                dbc.ModalFooter(dbc.Button("Close Detail Page", id="close-detail-button"),)
            ],
            size='xl',
            id="run-detail-page",
            is_open=False,
            centered=True

        ),

        # First Data Table
        html.Div([
            dash_table.DataTable(
                id='datatable-hamilton-category',
                columns=[{"name": i, "id": i} for i in dt_columns],
                data=df.to_dict('records'),
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto',},
                sort_action="native",
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in df.to_dict('rows')
                ],
                tooltip_duration=None,
                style_cell={"fontFamily": "Arial",
                            "size": 11, 'textAlign': 'left',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0,

                            },
                row_selectable='single',
                style_header={
                    'whiteSpace': 'normal',
                    'height': 'auto'},
                style_cell_conditional=[
                    {'if': {'column_id': 'Method Name'},
                     'width': '20%'},
                    {
                        'if': {
                            'column_id': 'File Name',
                        },
                        'display': 'none'
                    },
                ],
                css=[{'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                     {'selector': '.row', 'rule': 'margin: 0'}]
                ,style_data_conditional=[{
            'if': {
                'filter_query': '{Aborted} contains "Yes"',
                'column_id': 'Aborted'},
                    'backgroundColor': '#FF4136',
                    'fontWeight': 'bold'
            ,}]
            ),
        ], className="datatable-hamilton", style={'marginTop': 0, 'marginBottom': 15}),
        # Download Button
        # html.Div([
        #     html.A(html.Button('Download Data', id='download-button'), id='download-link-hamilton-category')
        # ]),
        # GRAPHS
        # html.Div([
        #     html.Div(
        #         id='update_graph_1'
        #     ),
        #     html.Div([
        #         dcc.Graph(id='hamilton-category'),
        #     ], className=" twelve columns"
        #     ), ], className="row "
        # ),
    ], className="subpage")
], className="page")

######################## END Hamilton Category Layout ########################

######################## START Hamilton Time Category Layout ########################
layout_hamilton_time = html.Div([
    html.Div([
        # CC Header
        Header('010000'),
        # Date Picker
html.Div(children='''
    Pick a Start/End Date
    '''),
        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range-hamilton-category-time',
                with_portal=True,
                min_date_allowed=dt(2018, 1, 1),
                max_date_allowed=df['Time End'].max().to_pydatetime(),
                initial_visible_month=dt(df['Time End'].max().to_pydatetime().year, df['Time End'].max().to_pydatetime().month, 1),
                end_date=df['Time End'].max().to_pydatetime(),
                start_date=(df['Time Start'].max() - timedelta(6)).to_pydatetime(),

            )
        ], className="row ", style={'marginTop': 0, 'marginBottom': 15, 'marginLeft': 0}),
    html.Div(children='''
    Pick a Hamilton
    '''),
        html.Div([
            dcc.Dropdown(
                id='dropdown-input-hamilton-time',
                style={'maxWidth': '300px'},
                options=[{'label': i, 'value': i} for i in unique_serial_numbers],
                value=unique_serial_numbers[0],
            )
        ], style={'marginTop': 0, 'marginBottom': 15}),

html.Div(children='''
    Averages Data for Time Study
    '''),
        html.Div([
            dash_table.DataTable(
                id='datatable-hamilton-summary-time',
                columns=[{"name": i, "id": i} for i in summary_columns_time],
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto',},
                sort_action="native",
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in df.to_dict('rows')
                ],
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
                    {'if': {'column_id': 'Method Name'},
                     'width': '20%'}],
                css=[{'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                     {'selector': '.row', 'rule': 'margin: 0'}],
            ),
        ], className=" twelve columns", style={'marginTop': 0, 'marginBottom': 15}),

html.Div(children='''
    Summary Data for Time Study
    '''),
        html.Div([
            dash_table.DataTable(
                id='datatable-hamilton-summary-time2',
                columns=[{"name": i, "id": i} for i in summary_columns_time2],
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto',},
                sort_action="native",
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in df.to_dict('rows')
                ],
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
                    {'if': {'column_id': 'Method Name'},
                     'width': '20%'}],
                css=[{'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                     {'selector': '.row', 'rule': 'margin: 0'}],
            ),
        ], className=" twelve columns", style={'marginTop': 0, 'marginBottom': 15}),
html.Div(children='''
    Hamilton Data by Serial Number
    '''),
        # First Data Table
        html.Div([
            dash_table.DataTable(
                id='datatable-hamilton-category-time',
                columns=[{"name": i, "id": i} for i in dt_columns_time],
                data=df.to_dict('records'),
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto',},
                sort_action="native",
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in df.to_dict('rows')
                ],
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
                    {'if': {'column_id': 'Method Name'},
                     'width': '20%'}
                ],
                css=[{'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                     {'selector': '.row', 'rule': 'margin: 0'}]

            ),
        ], className="datatable-hamilton", style={'marginTop': 0, 'marginBottom': 15}),
        # Download Button
        # html.Div([
        #     html.A(html.Button('Download Data', id='download-button'), id='download-link-hamilton-category')
        # ]),
        # GRAPHS
        # html.Div([
        #     html.Div(
        #         id='update_graph_1'
        #     ),
        #     html.Div([
        #         dcc.Graph(id='hamilton-category'),
        #     ], className=" twelve columns"
        #     ), ], className="row "
        # ),
    ], className="subpage")
], className="page")

######################## END Hamilton Time Category Layout ########################

######################## START BarTender Category Layout ########################
layout_BarTender = html.Div([
    html.Div([
        # CC Header
        Header('001000'),
        # Date Picker
html.Div(children='''
    Pick a Start/End Date
    '''),
        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range-bartender',
                with_portal=True,
                min_date_allowed=dt(2018, 1, 1),
                max_date_allowed=bt_df['CreatedDateTime'].max().to_pydatetime(),
                initial_visible_month=dt(bt_df['CreatedDateTime'].max().to_pydatetime().year, bt_df['CreatedDateTime'].max().to_pydatetime().month, 1),
                end_date=bt_df['CreatedDateTime'].max().to_pydatetime(),
                start_date=(bt_df['CreatedDateTime'].max() - timedelta(6)).to_pydatetime(),
            )
        ], className="row ", style={'marginTop': 0, 'marginBottom': 15, 'marginLeft': 0}),
html.Div(children='''
Select Internal/Controlled
'''),
        html.Div([dcc.Checklist(
            id='bartender-server-select',

            options=[
        {'label': 'Controlled  ', 'value': 'Controlled'},
        {'label': 'Internal', 'value': 'Internal'}
    ],
            value=['Controlled', 'Internal'],
            labelStyle={'display': 'inline-block'}
        )]),

html.Div(children='''
    Labels By Printer
    '''),
        html.Div([
            dash_table.DataTable(
                id='datatable-bartender-summary',
                data=bt_df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in bartender_summary],
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto',},
                sort_action="native",
                # tooltip_data=[
                #     {
                #         column: {'value': str(value), 'type': 'markdown'}
                #         for column, value in row.items()
                #     } for row in bt_df.to_dict('rows')
                # ],
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
                    {'if': {'column_id': 'PrinterName'},
                     'width': '20%'}],
                css=[{'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                     {'selector': '.row', 'rule': 'margin: 0'}],
            ),
        ], className=" twelve columns", style={'marginTop': 0, 'marginBottom': 15}),

html.Div(children='''
    Labels by Label
    '''),
        html.Div([
            dash_table.DataTable(
                id='datatable-bartender-summary-2',
                data=bt_df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in bartender_summary2],
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto',},
                sort_action="native",
                # tooltip_data=[
                #     {
                #         column: {'value': str(value), 'type': 'markdown'}
                #         for column, value in row.items()
                #     } for row in bt_df.to_dict('rows')
                # ],
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
                    {'if': {'column_id': 'PrinterName'},
                     'width': '20%'}],
                css=[{'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                     {'selector': '.row', 'rule': 'margin: 0'}],
            ),
        ], className=" twelve columns", style={'marginTop': 0, 'marginBottom': 15}),
html.Div(children='''
    Print History
    '''),
        # First Data Table
        html.Div([
            dash_table.DataTable(
                id='datatable-bartender-table',
                columns=[{"name": i, "id": i} for i in bartender_table],
                data=bt_df.to_dict('records'),
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto',},
                sort_action="native",
                # tooltip_data=[
                #     {
                #         column: {'value': str(value), 'type': 'markdown'}
                #         for column, value in row.items()
                #     } for row in bt_df.to_dict('rows')
                # ],
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
                    {'if': {'column_id': 'PrinterName'},
                     'width': '20%'}
                ],
                css=[{'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                     {'selector': '.row', 'rule': 'margin: 0'}]

            ),
        ], className="datatable-hamilton", style={'marginTop': 0, 'marginBottom': 15}),
        # Download Button
        # html.Div([
        #     html.A(html.Button('Download Data', id='download-button'), id='download-link-hamilton-category')
        # ]),
        # GRAPHS
        # html.Div([
        #     html.Div(
        #         id='update_graph_1'
        #     ),
        #     html.Div([
        #         dcc.Graph(id='hamilton-category'),
        #     ], className=" twelve columns"
        #     ), ], className="row "
        # ),
    ], className="subpage")
], className="page")

######################## END BarTender Category Layout ########################

######################## START ElectroStretcher Category Layout ########################
layout_stretcher = html.Div([
    html.Div([
        # CC Header
        Header('000100'),
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
                end_date= date.today(),
                start_date=(date.today() - timedelta(6)),
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
                             'overflowX': 'auto',},
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
        # First Data Table
        html.Div([
            dash_table.DataTable(
                id='datatable-stretcher-table',
                columns=[{"name": i, "id": i} for i in stretcher_table],
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto',},
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
                     {'selector': '.row', 'rule': 'margin: 0'}]

            ),
        ], className="datatable-hamilton", style={'marginTop': 0, 'marginBottom': 15}),
    ], className="subpage")
], className="page")

######################## END ElectroStretcher Category Layout ########################

######################## 404 Page ########################
noPage = html.Div([
    # CC Header
    Header('000000'),
    html.P(["404 Page not found"])
], className="no-page")