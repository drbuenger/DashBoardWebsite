
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


# Read from NAV
server = 'NANO-ERP'
database = 'NanoString'
username = 'NAV-RO'
password = 'r3@d0nly!'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

inv_df = pd.read_sql_query('SELECT TOP (1000) [timestamp] ,[Status] ,[No_] ,[Description] ,[Description 2] ,[Creation Date] \
    [Last Date Modified]       ,[Starting Time]      ,[Starting Date]      ,[Ending Time]      ,[Ending Date]      ,[Due Date]      ,[Finished Date] \
    ,[Location Code]       ,[Bin Code]       ,[Quantity]       ,[Unit Cost]       ,[Cost Amount]       ,[Assigned User ID] \
    FROM [NanoString].[dbo].[NanoString$Production Order]', cnxn)

inventory_columns = ['No_','Status','Assigned User ID','Quantity', 'Location Code', 'Due Date', 'Description',  'Description 2']

layout_Inventory = html.Div([
    html.Div([
        Header(),
        html.Div(children='''
        Inventory Data
        '''),
        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range-inventory',
                with_portal=True,
                min_date_allowed=dt(2018, 1, 1),
                max_date_allowed=inv_df['Due Date'].max().to_pydatetime(),
                initial_visible_month=dt(inv_df['Due Date'].max().to_pydatetime().year,
                                         inv_df['Due Date'].max().to_pydatetime().month, 1),
                end_date=inv_df['Due Date'].max().to_pydatetime(),
                start_date=(inv_df['Due Date'].max() - timedelta(6)).to_pydatetime(),
            )
        ], className="row ", style={'marginTop': 0, 'marginBottom': 15, 'marginLeft': 0}),
        html.Div([
            dash_table.DataTable(
                id='datatable-inventory',
              #  data=inv_df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in inventory_columns],
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
    ], className="subpage")
], className="page")
