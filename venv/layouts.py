import dash_core_components as dcc
import dash_html_components as html
import dash_table
from components import Header, print_button, read_trace_file
from datetime import datetime as dt
from datetime import date, timedelta
import pandas as pd
import os
import csv
import shutil
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

df = pd.read_csv('C:\\Users\\dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\data\\Hamilton.csv')

df.dropna(axis=0, inplace=True)

df['Time Start'] = pd.to_datetime(df['Time Start'])
df['Time End'] = pd.to_datetime(df['Time End'])
df['Duration'] = df['Time End'] - df['Time Start']
#df['Duration'] = pd.Timedelta(df['Time End'] - df['Time Start']).seconds / 60
#df['Time Start'] = df['Time Start'].dt.strftime("%Y/%m/%d %H:%M:%S")
#df['Time End'] = df['Time End'].dt.strftime("%Y/%m/%d %H:%M:%S")
#df['Duration'] = pd.Timedelta(['Duration'].dt.str("%Y/%m/%d %H:%M:%S")


df = df.loc[(df!=0).any(axis=1)]
unique_serial_numbers = df['Serial Number'].unique()


dt_columns = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name']

conditional_columns = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name']

dt_columns_total = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name' ]

df_columns_calculated = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name' ]

conditional_columns_calculated_calculated =['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name' ]

summary_columns = ['Method Name', 'Total']

######################## START Hamilton Category Layout ########################
layout_hamilton = html.Div([

    #    print_button(),

    html.Div([
        # CC Header
        Header(),
        # Date Picker
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
        ], className="row ", style={'marginTop': 30, 'marginBottom': 15}),
        # Header Bar
        html.Div([
            html.H6(["Nanostring Level Metrics"], className="gs-header gs-text-header padded", style={'marginTop': 15})
        ]),

    html.Div(children='''
    Pick a Hamilton
    '''),
    dcc.Dropdown(
        id='dropdown-input-hamilton',
        options=[{'label': i, 'value': i} for i in unique_serial_numbers],
        value=unique_serial_numbers[0]
    ),
        # Radio Button
        # html.Div([
        #     dcc.RadioItems(
        #         options=[
        #             {'label': 'Condensed Data Table', 'value': 'Condensed'},
        #             {'label': 'Complete Data Table', 'value': 'Complete'},
        #         ], value='Condensed',
        #         labelStyle={'display': 'inline-block', 'width': '20%', 'margin': 'auto', 'marginTop': 15,
        #                     'paddingLeft': 15},
        #         id='radio-button-hamilton-category'
        #     )]),
        html.Div([
            dash_table.DataTable(
                id='datatable-hamilton-summary',
                columns=[{"name": i, "id": i} for i in summary_columns],
                style_table={'maxWidth': '1500px'},
                row_selectable="single",
                style_cell={"fontFamily": "Arial", "size": 10, 'textAlign': 'left'},
                css=[{'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'}]
                #,style_cell_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#D5DBDB'}]
            ),
        ], className=" twelve columns"),
        # First Data Table
        html.Div([
            dash_table.DataTable(
                id='datatable-hamilton-category',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                style_table={'maxWidth': '1500px'},
                row_selectable="multi",
                style_cell={"fontFamily": "Arial", "size": 10, 'textAlign': 'left'},
                css=[{'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'}]
                #,style_cell_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#D5DBDB'}]
            ),
        ], className=" twelve columns"),
        # Download Button
        html.Div([
            html.A(html.Button('Download Data', id='download-button'), id='download-link-hamilton-category')
        ]),
        # GRAPHS
        html.Div([
            html.Div(
                id='update_graph_1'
            ),
            html.Div([
                dcc.Graph(id='hamilton-category'),
            ], className=" twelve columns"
            ), ], className="row "
        ),
    ], className="subpage")
], className="page")

######################## END Hamilton Category Layout ########################

######################## START Extra Category Layout ########################
layout_extra_category = html.Div([
    html.Div([
        # CC Header
        Header(),
        # Date Picker
        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range-ga-category',
                # with_portal=True,
                min_date_allowed=dt(2018, 1, 1),
                max_date_allowed=df['Time End'].max().to_pydatetime(),
                initial_visible_month=dt( df['Time End'].max().to_pydatetime().year, df['Time End'].max().to_pydatetime().month, 1),
                start_date=(df['Time Start'].max() - timedelta(6)).to_pydatetime(),
                end_date=df['Time End'].max().to_pydatetime(),
            ),
            html.Div(id='output-container-date-picker-range-extra-category')
        ], className="row ", style={'marginTop': 30, 'marginBottom': 15}),
        # Header Bar
        html.Div([
            html.H6(["Extra Level Metrics"], className="gs-header gs-text-header padded", style={'marginTop': 15})
        ]),
        # Radio Button
        html.Div([
            dcc.RadioItems(
                options=[
                    {'label': 'Condensed Data Table', 'value': 'Condensed'},
                    {'label': 'Complete Data Table', 'value': 'Complete'},
                ], value='Condensed',
                labelStyle={'display': 'inline-block', 'width': '20%', 'margin': 'auto', 'marginTop': 15,
                            'paddingLeft': 15},
                id='radio-button-extra-category'
            )]),
        # First Data Table
        html.Div([
            dash_table.DataTable(
                id='datatable-extra-category',
                columns=[{"name": i, "id": i, 'deletable': True} for i in dt_columns],
                editable=True,
                style_table={'maxWidth': '1500px'},
                row_selectable="multi",
                selected_rows=[0],
                style_cell={"fontFamily": "Arial", "size": 10, 'textAlign': 'left'},
                css=[{'selector': '.dash-cell div.dash-cell-value',
                      'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'}],
                style_cell_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#D5DBDB'}]
            ),
        ], className=" twelve columns"),
        # Download Button
        html.Div([
            html.A(html.Button('Download Data', id='download-button'), id='download-link-extra-category')
        ]),
        # GRAPHS
        html.Div([
            html.Div(
                id='update_graph_1'
            ),
            html.Div([
                dcc.Graph(id='extra-category'),
            ], className=" twelve columns"
            ), ], className="row "
        ),
    ], className="subpage")
], className="page")

######################## END Extra Category Layout ########################

######################## 404 Page ########################
noPage = html.Div([
    # CC Header
    Header(),
    html.P(["404 Page not found"])
], className="no-page")