import dash_core_components as dcc
import dash_html_components as html
import dash_table
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
#df['Duration']=df['Duration'].map('{:,.1f}'.format)
df = df.drop(columns=['Tips Used 50uL','Tips Used 300uL'])
df = df.loc[(df!=0).any(axis=1)]
df = df[df['Serial Number'] != '0']
df = df[df['Serial Number'] != '0000']
df = df.rename(columns={'Tips Used 1000uL': 'Tips Used'})
#df.astype({'Tips Used 1000uL': 'int'}).dtypes
#df.astype({'Duration': 'float64'}).dtypes
unique_serial_numbers = df['Serial Number'].unique()

dt_columns = ['Method Name','Time Start', 'Time End', 'User Name', 'Tips Used',  'Duration', 'Aborted']

dt_columns_time = ['Method Name','Dispensing Time','Dispensing Count','Aspirating Time','Aspirating Count', 'Tip Pickup Time','Tip Pickup Count', 'Tip Eject Time','Tip Eject Count', 'User Time','User Count']

conditional_columns = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name']

dt_columns_total = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name' ]

df_columns_calculated = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name' ]

conditional_columns_calculated_calculated =['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name' ]

summary_columns = ['Method Name', 'Total', 'Average', 'TipsUsed', 'Success %']
summary_columns_time = ['Method Name', 'Average Dispense', 'Average Aspirate', 'Average Pickup', 'Average Eject', 'Average User']
summary_columns_time2 = ['Method Name', '% Dispense', '% Aspirate', '% Pickup', '% Eject', '% User', 'Average Total Time (sec)']

#Read in BarTender data
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=labels-internal\BARTENDER;"
                      "Database=BarTender_UNREG;"
                      "Trusted_Connection=yes;")

bt_df = pd.read_sql_query('SELECT btff.Name , p.Name as PrinterName, btp.TotalLabels, btp.CreatedDateTime FROM BtPrintJobs btp \
inner join BtFormatFileNames btff on btp.FormatFileNameID = btff.FileNameID \
inner join Printers p on btp.FormatID = p.PrinterID', cnxn)
bt_df['CreatedDateTime']= bt_df['CreatedDateTime'] - 621355968000000000
bt_df['CreatedDateTime']= bt_df['CreatedDateTime']/10
bt_df['CreatedDateTime'] = pd.to_datetime(bt_df['CreatedDateTime'],unit='us')

bartender_summary = ['PrinterName', 'Name', 'TotalLabels', 'CreatedDateTime']
bartender_summary2 =  ['PrinterName', 'Name', 'TotalLabels', 'CreatedDateTime']
bartender_table = ['PrinterName', 'Name', 'TotalLabels', 'CreatedDateTime']

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
    '''),
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
                style_header={
                    'whiteSpace': 'normal',
                    'height': 'auto'},
                style_cell_conditional=[
                    {'if': {'column_id': 'Method Name'},
                     'width': '20%'}],
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
    Table1
    '''),
        html.Div([
            dash_table.DataTable(
                id='datatable-bartender-summary',
                columns=[{"name": i, "id": i} for i in bartender_summary],
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto',},
                sort_action="native",
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in bt_df.to_dict('rows')
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
                    {'if': {'column_id': 'PrinterName'},
                     'width': '20%'}],
                css=[{'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                     {'selector': '.row', 'rule': 'margin: 0'}],
            ),
        ], className=" twelve columns", style={'marginTop': 0, 'marginBottom': 15}),

html.Div(children='''
    Table2
    '''),
        html.Div([
            dash_table.DataTable(
                id='datatable-bartender-summary-2',
                columns=[{"name": i, "id": i} for i in bartender_summary2],
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto',},
                sort_action="native",
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in bt_df.to_dict('rows')
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
                    {'if': {'column_id': 'PrinterName'},
                     'width': '20%'}],
                css=[{'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                     {'selector': '.row', 'rule': 'margin: 0'}],
            ),
        ], className=" twelve columns", style={'marginTop': 0, 'marginBottom': 15}),
html.Div(children='''
    Table3
    '''),
        # First Data Table
        html.Div([
            dash_table.DataTable(
                id='datatable-bartender-table',
                columns=[{"name": i, "id": i} for i in bartender_table],
                data=df.to_dict('records'),
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto',},
                sort_action="native",
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in bt_df.to_dict('rows')
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

######################## 404 Page ########################
noPage = html.Div([
    # CC Header
    Header('000000'),
    html.P(["404 Page not found"])
], className="no-page")