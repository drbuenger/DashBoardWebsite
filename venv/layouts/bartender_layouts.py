
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


# Read in BarTender data
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=labels-internal\BARTENDER;"
                      "Database=BarTender_UNREG;"
                      "Trusted_Connection=yes;")

bt_df = pd.read_sql_query('SELECT btff.Name , p.Name as PrinterName, \
                            btp.TotalLabels, btp.CreatedDateTime FROM BtPrintJobs btp \
                            inner join BtFormatFileNames btff on btp.FormatFileNameID = btff.FileNameID \
                            inner join Printers p on btp.PrinterID = p.PrinterID', cnxn)
bt_df['CreatedDateTime'] = bt_df['CreatedDateTime'] - 621355968000000000
bt_df['CreatedDateTime'] = bt_df['CreatedDateTime'] / 10
bt_df['CreatedDateTime'] = pd.to_datetime(bt_df['CreatedDateTime'], unit='us')
bt_df['Server'] = 'Internal'

# Read in BarTender data
cnxn_controlled = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                                 "Server=lbl-controlled\BARTENDER_REG;"
                                 "Database=BarTender_REG;"
                                 "Trusted_Connection=yes;")
bt_df_commander = pd.read_sql_query('SELECT * FROM BtPrintJobCommandLines', cnxn_controlled)

bt_df_controlled = pd.read_sql_query('SELECT btff.Name, p.Name as PrinterName, btp.TotalLabels, btp.CreatedDateTime \
FROM [BarTender_REG].[dbo].[BtPrintJobs] btp \
inner join [BarTender_REG].[dbo].BtFormatFileNames btff on btp.FormatFileNameID = btff.FileNameID \
inner join [BarTender_REG].[dbo].[Printers] p on btp.PrinterID = p.PrinterID', cnxn_controlled)
bt_df_controlled['CreatedDateTime'] = bt_df_controlled['CreatedDateTime'] - 621355968000000000
bt_df_controlled['CreatedDateTime'] = bt_df_controlled['CreatedDateTime'] / 10
bt_df_controlled['CreatedDateTime'] = pd.to_datetime(bt_df_controlled['CreatedDateTime'], unit='us')
bt_df_controlled['Server'] = 'Controlled'

bartender_summary = ['PrinterName', 'Total', 'LastUsed']
bartender_summary2 = ['Name', 'Total', 'LastUsed']
bartender_table = ['PrinterName', 'Name', 'TotalLabels', 'Print Time', 'Server']

bt_df = bt_df.append(bt_df_controlled)

######################## START BarTender Category Layout ########################
layout_BarTender = html.Div([
    html.Div([
        # CC Header
        Header(),
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
                initial_visible_month=dt(bt_df['CreatedDateTime'].max().to_pydatetime().year,
                                         bt_df['CreatedDateTime'].max().to_pydatetime().month, 1),
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
                             'overflowX': 'auto', },
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
                             'overflowX': 'auto', },
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
                             'overflowX': 'auto', },
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