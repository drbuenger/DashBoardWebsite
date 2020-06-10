from dash.dependencies import Input, Output
from app import app
import plotly.graph_objs as go
from plotly import tools

from datetime import datetime as dt
from datetime import date, timedelta
from datetime import datetime

import numpy as np
import pandas as pd

import io
import xlsxwriter
import flask
from flask import send_file

from components import formatter_currency, formatter_currency_with_cents, formatter_percent, formatter_percent_2_digits, formatter_number
from components import update_first_datatable, update_first_download, update_second_datatable, update_graph, update_summary_datatable
from components import update_first_datatable_time , update_summary_datatable_time , update_summary_datatable_time2

pd.options.mode.chained_assignment = None

df = pd.read_csv('C:\\Users\\dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\data\\Hamilton.csv',
                 na_values=['Null','NA','nan'],
                 keep_default_na=False)

df['Time Start'] = pd.to_datetime(df['Time Start'])
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
now = datetime.now()
datestamp = now.strftime("%Y%m%d")

current_year = df['Time End'].max().to_pydatetime().year

now = datetime.now()
datestamp = now.strftime("%Y%m%d")

unique_serial_numbers = df['Serial Number'].unique()

columns = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name']

columns_complete = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name']

columns_condensed = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name' ]

conditional_columns = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name' ]

dt_columns_total =['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name' ]


######################## Hamilton Category Callbacks ########################

# Callback and update first data table
@app.callback([Output('datatable-hamilton-category', 'data'),
                Output('datatable-hamilton-category', 'tooltip_data'),
               ],
	[Input('my-date-picker-range-hamilton-category', 'start_date'),
	 Input('my-date-picker-range-hamilton-category', 'end_date'),
     Input('dropdown-input-hamilton', 'value')
     ])
def update_data_1(start_date, end_date, serial_number):
	return update_first_datatable(start_date, end_date, serial_number)

# Callback and update first data table
@app.callback([Output('datatable-hamilton-summary', 'data'),
                Output('datatable-hamilton-summary', 'tooltip_data'),
               ],
	[Input('my-date-picker-range-hamilton-category', 'start_date'),
	 Input('my-date-picker-range-hamilton-category', 'end_date'),
     Input('dropdown-input-hamilton', 'value')
     ])
def update_data_summary(start_date, end_date, serial_number):
	return update_summary_datatable(start_date, end_date, serial_number)

# Callback and update data table columns
@app.callback(Output('datatable-hamilton-category', 'columns'),
    [Input('radio-button-hamilton-category', 'value')])
def update_columns(value):
    if value == 'Complete':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_complete]
    elif value == 'Condensed':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_condensed]
    return column_set

# Callback for excel download
@app.callback(
    Output('download-link-hamilton-category', 'href'),
    [Input('my-date-picker-range-hamilton-category', 'start_date'),
	 Input('my-date-picker-range-hamilton-category', 'end_date'),
    Input('dropdown-input-hamilton', 'serial_number')
     ])
def update_link(start_date, end_date, serial_number):
	return '/Reports/Hamilton/urlToDownload?value={}/{}'.format(dt.strptime(start_date,'%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M'),dt.strptime(end_date,'%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M'))
@app.server.route("/Reports/Hamilton/urlToDownload")
def download_excel_hamilton_category():
    value = flask.request.args.get('value')
    #here is where I split the value
    value = value.split('/')
    start_date = value[0]
    end_date = value[1]

    filename = datestamp + '_hamilton_category_' + start_date + '_to_' + end_date + '.xlsx'
	# Dummy Dataframe
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)

    buf = io.BytesIO()
    excel_writer = pd.ExcelWriter(buf, engine="xlsxwriter")
    download_1 = update_first_download(start_date, end_date, serial_number)
    download_1.to_excel(excel_writer, sheet_name="sheet1", index=False)
    # df.to_excel(excel_writer, sheet_name="sheet1", index=False)
    excel_writer.save()
    excel_data = buf.getvalue()
    buf.seek(0)

    return send_file(
        buf,
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        attachment_filename=filename,
        as_attachment=True,
        cache_timeout=0
    )

# Callback and update second data table
@app.callback(
	Output('datatable-hamilton-category-2', 'data'),
	[Input('my-date-picker-range-hamilton-category', 'start_date'),
	 Input('my-date-picker-range-hamilton-category', 'end_date'),
     Input('dropdown-input-hamilton', 'serial_number')
     ])
def update_data_2(start_date, end_date, serial_number):
	data_2 = update_second_datatable(start_date, end_date, serial_number)
	return data_2

# Callback for the Graphs
@app.callback(
   Output('hamilton-category', 'figure'),
   [Input('my-date-picker-range-hamilton-category', 'start_date'),
    Input('my-date-picker-range-hamilton-category', 'end_date'),
    Input('dropdown-input-hamilton', 'value')])
def update_hamilton_category(start_date,end_date, serial_number):
    filtered_df = update_first_datatable(start_date, end_date, serial_number)
    fig = update_graph(filtered_df)
    return fig

######################## Hamilton TIME Category Callbacks ########################
# Callback and update first data table
@app.callback([Output('datatable-hamilton-category-time', 'data'),
                Output('datatable-hamilton-category-time', 'tooltip_data'),
               ],
	[Input('my-date-picker-range-hamilton-category-time', 'start_date'),
	 Input('my-date-picker-range-hamilton-category-time', 'end_date'),
     Input('dropdown-input-hamilton-time', 'value')
     ])
def update_data_time(start_date, end_date, serial_number):
	return update_first_datatable_time(start_date, end_date, serial_number)

# Callback and update first data table
@app.callback([Output('datatable-hamilton-summary-time', 'data'),
                Output('datatable-hamilton-summary-time', 'tooltip_data'),
               ],
	[Input('my-date-picker-range-hamilton-category-time', 'start_date'),
	 Input('my-date-picker-range-hamilton-category-time', 'end_date'),
     Input('dropdown-input-hamilton-time', 'value')
     ])
def update_data_summary_time(start_date, end_date, serial_number):
	return update_summary_datatable_time(start_date, end_date, serial_number)

# Callback and update first data table
@app.callback([Output('datatable-hamilton-summary-time2', 'data'),
                Output('datatable-hamilton-summary-time2', 'tooltip_data'),
               ],
	[Input('my-date-picker-range-hamilton-category-time', 'start_date'),
	 Input('my-date-picker-range-hamilton-category-time', 'end_date'),
     Input('dropdown-input-hamilton-time', 'value')
     ])
def update_data_summary_time2(start_date, end_date, serial_number):
	return update_summary_datatable_time2(start_date, end_date, serial_number)

# Callback for the Graphs
@app.callback(
   Output('extra-category', 'figure'),
   [Input('datatable-extra-category', "selected_rows"),
   Input('my-date-picker-range-extra-category', 'end_date')])
def update_extra_category(selected_rows, end_date):
	travel_product = []
	travel_product_list = sorted(df['Extra Category'].unique().tolist())
	for i in selected_rows:
		travel_product.append(travel_product_list[i])
		# Filter by specific product
	filtered_df = df[(df['Extra Category'].isin(travel_product))].groupby(['Year', 'Week']).sum()[['Spend TY', 'Spend LY', 'Sessions - TY', 'Sessions - LY', 'Bookings - TY', 'Bookings - LY', 'Revenue - TY', 'Revenue - LY']].reset_index()
	fig = update_graph(filtered_df, end_date)
	return fig

