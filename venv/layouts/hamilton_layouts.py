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



# Read in Data
hamilton_computers = [
    "\\\MTGREENMTN\\C$\Program Files\\Hamilton\\LogFiles",
    "\\\ZORRANDER\\C$\\Program Files\\Hamilton\\Logfiles Archive 2276",
    "\\\ZORRANDER\\C$\\Program Files\\Hamilton\\Logfiles",
    "\\\SANCHEZ\\C$\\Program Files\\Hamilton\\LogFiles",
    "\\\HAMILTON08\\C$\\Program Files\\Hamilton\\LogFiles",
    "\\\MFG-00000833\\C$\\Program Files\\Hamilton\\LogFiles",
    "\\\MFG-STARLET1\\C$\\Program Files (x86)\\Hamilton\\LogFiles",
    #"\\\MFG-STARLET2\\C$\\Program Files (x86)\\Hamilton\\LogFiles",
    #"\\\MFG-STARLET3\\C$\\Program Files (x86)\\Hamilton\\LogFiles",
]

hamilton_asset_ids = {
    "1731": "HAM-01",
    "2276": "HAM-02",
    "A928": "HAM-03",
    "C034": "HAM-05",
    "D363": "HAM-09",
    "E487": "HAM-10",
    "SN1": "HAM-11",
    "SN2": "HAM-12",
}

storage_location = 'C:\\Users\\dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\data'
# r=root, d=directories, f = files
x = []
for pc in hamilton_computers:

    path_split = pc.split("\\")
    pc_name = path_split[2]
    try:
        if os.path.exists(pc):
            y = [os.path.join(r, file) for r, d, f in os.walk(pc) for file in f]
            for z in y:
                file_split = z.split("\\")
                count = len(file_split)
                destination = storage_location + "\\" + pc_name + "\\" + file_split[count - 1]
                if z.endswith(".trc") and not os.path.exists(destination):
                    shutil.copy2(z, destination)
                    x.append(destination)
    except:
        print("PC Not found: " + pc_name)
for file in x:
    if file.endswith(".trc"):
        read_trace_file(file)

df = pd.read_csv('C:\\Users\\dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\data\\Hamilton.csv',
                 na_values=['Null', 'NA', 'nan'],
                 keep_default_na=False)
df.dropna(axis=0, inplace=True)

df['Time Start'] = pd.to_datetime(df['Time Start'])
df['Time End'] = pd.to_datetime(df['Time End'])
df['Time End'] = pd.to_datetime(df['Time End'])
df['Duration'] = df['Time End'].sub(df['Time Start']).dt.total_seconds().div(60)
df = df.drop(columns=['Tips Used 50uL', 'Tips Used 300uL'])
df = df.loc[(df != 0).any(axis=1)]
df = df[df['Serial Number'] != '0']
df = df[df['Serial Number'] != '0000']
df = df.rename(columns={'Tips Used 1000uL': 'Tips Used'})
unique_serial_numbers = df['Serial Number'].unique()
unique_serial_numbers.sort()
dt_columns = ['Method Name', 'Time Start', 'Time End', 'User Name', 'Tips Used', 'Duration', 'Aborted', 'File Name']
dt_columns_time = ['Method Name',
                   'Dispensing Time',
                   'Dispensing Count',
                   'Aspirating Time',
                   'Aspirating Count',
                   'Tip Pickup Time',
                   'Tip Pickup Count',
                   'Tip Eject Time',
                   'Tip Eject Count',
                   'User Time',
                   'User Count']

summary_columns = ['Method Name', 'Total', 'Average', 'TipsUsed', 'Success %']
summary_columns_time = ['Method Name',
                        'Average Dispense',
                        'Average Aspirate',
                        'Average Pickup',
                        'Average Eject',
                        'Average User']
summary_columns_time2 = ['Method Name',
                         '% Dispense',
                         '% Aspirate',
                         '% Pickup',
                         '% Eject',
                         '% User',
                         'Average Total Time (min)']
ham_detail_columns = ['Time Since Start (sec)', 'Step Type', 'Message']


summary_columns_tips = ['Serial Number',
                        'TipsUsed',
                        ]

layout_hamilton = html.Div([

    html.Div([
        # CC Header
        Header(),
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
                initial_visible_month=dt(df['Time End'].max().to_pydatetime().year,
                                         df['Time End'].max().to_pydatetime().month, 1),
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
                options=[{'label': hamilton_asset_ids[i] + " / " + i, 'value': i} for i in unique_serial_numbers],
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
                             'overflowX': 'auto', },
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
                                     'overflowX': 'auto', },
                        sort_action="native",
                        selected_rows=[],
                        style_cell={
                            "fontFamily": "Arial",
                            "size": 11, 'textAlign': 'left',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0,
                            'whiteSpace': 'normal',
                            'height': 'auto',
                        },
                        style_header={
                            'whiteSpace': 'normal',
                            'height': 'auto'},
                        style_cell_conditional=[
                            {
                                'if': {
                                    'column_id': 'Time Since Start (sec)'
                                },
                                'width': '8%',
                                'textAlign': 'center'
                            },
                            {
                                'if': {
                                    'column_id': 'Step Type'
                                },
                                'width': '8%'
                            },

                        ],
                        css=[{'selector': '.dash-cell div.dash-cell-value',
                              'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},
                             {'selector': '.row', 'rule': 'margin: 0'}],
                    ),
                ], className=" twelve columns", style={'marginTop': 0, 'marginBottom': 15}), ),
                dbc.ModalFooter(dbc.Button("Close Detail Page", id="close-detail-button"), )
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
                             'overflowX': 'auto', },
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
                , style_data_conditional=[{
                    'if': {
                        'filter_query': '{Aborted} contains "Yes"',
                        'column_id': 'Aborted'},
                    'backgroundColor': '#FF4136',
                    'fontWeight': 'bold'
                    , }]
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
        Header(),
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
                initial_visible_month=dt(df['Time End'].max().to_pydatetime().year,
                                         df['Time End'].max().to_pydatetime().month, 1),
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
                options=[{'label': hamilton_asset_ids[i] + " / " + i, 'value': i} for i in unique_serial_numbers],
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
                             'overflowX': 'auto', },
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
                             'overflowX': 'auto', },
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
                             'overflowX': 'auto', },
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

layout_hamilton_tips = html.Div([
    html.Div([
        # CC Header
        Header(),
        # Date Picker
        html.Div(children='''
    Pick a Start/End Date
    '''),
        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range-hamilton-tips',
                with_portal=True,
                min_date_allowed=dt(2018, 1, 1),
                max_date_allowed=df['Time End'].max().to_pydatetime(),
                initial_visible_month=dt(df['Time End'].max().to_pydatetime().year,
                                         df['Time End'].max().to_pydatetime().month, 1),
                end_date=df['Time End'].max().to_pydatetime(),
                start_date=(df['Time Start'].max() - timedelta(30)).to_pydatetime(),

            )
        ], className="row ", style={'marginTop': 0, 'marginBottom': 15, 'marginLeft': 0}),

        html.Div(children='''
    Tip Usage
    '''),
        html.Div([
            dash_table.DataTable(
                id='datatable-hamilton-summary-tips',
                columns=[{"name": i, "id": i} for i in summary_columns_tips],
                style_table={'maxWidth': '1500px',
                             'overflowX': 'auto', },
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
    ], className="subpage")
], className="page")