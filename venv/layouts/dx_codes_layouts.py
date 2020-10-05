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

# Duplicate Test Codes
diag_test_codes_location_source = 'W:\\Production\\Bartender Trigger Directory'
y = [os.path.join(r, file) for r, d, f in os.walk(diag_test_codes_location_source) for file in f]
for z in y:
    file_split = z.split("\\")
    count = len(file_split)
    destination = storage_location + "\\DX\\" + file_split[count - 1]
    if z.endswith(".old") and not os.path.exists(destination):
        shutil.copy2(z, destination)

generator_columns = ['Num of Tests', 'Product', 'Unique ID', 'Test Code', 'Date and Time']
generator_columns_duplicates = ['Duplicate Print Jobs']
generator_columns_duplicates2 = ['Date and Time', 'Unique ID', 'Test Code', 'Product', 'File Name']

######################## START duplicate test codes Category Layout ########################
layout_duplicate_test_codes = html.Div([
    html.Div([
        # CC Header
        Header(),
        # Date Picker
        html.Div(children='''
    Pick a Start/End Date
    '''),
        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range-generator',
                with_portal=True,
                min_date_allowed=dt(2016, 1, 1),
                max_date_allowed=date.today() + timedelta(1),
                initial_visible_month=dt(date.today().year, date.today().month, 1),
                end_date=date.today(),
                start_date=(date.today() - timedelta(65)),
            )
        ], className="row ", style={'marginTop': 0, 'marginBottom': 15, 'marginLeft': 0}),
        html.Div(children='''
    Duplicate Print Jobs Found
    '''),
        html.Div([
            dash_table.DataTable(
                id='datatable-generator-duplicates',
                columns=[{"name": i, "id": i} for i in generator_columns_duplicates],
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
    Duplicate Codes Found
    '''),
        html.Div([
            dash_table.DataTable(
                id='datatable-generator-duplicates2',
                columns=[{"name": i, "id": i} for i in generator_columns_duplicates2],
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
    All Test Codes Found
    '''),
        html.Div([
            dash_table.DataTable(
                id='datatable-generator',
                columns=[{"name": i, "id": i} for i in generator_columns],
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

    ], className="subpage")
], className="page")

######################## END Duplicate Test Codes Category Layout ########################