from dash.dependencies import Input, Output, State
from app import app
import plotly.graph_objs as go
from plotly import tools
import dash
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
from components import update_first_datatable, update_first_download, update_second_datatable, update_graph, update_summary_datatable, read_trace_file_detail
from components import update_first_datatable_time , update_summary_datatable_time , update_summary_datatable_time2
from components import update_bartender_table , update_bartender_summary , update_bartender_summary2
from components import update_summary_stretcher, update_datatable_stretcher, es_graph
from components import update_generator_table, update_generator_duplicates, update_generator_duplicates2

pd.options.mode.chained_assignment = None

df = pd.read_csv('C:\\Users\\dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\data\\Hamilton.csv',
                 na_values=['Null','NA','nan'],
                 keep_default_na=False)

df['Time Start'] = pd.to_datetime(df['Time Start'])
df['Time End'] = pd.to_datetime(df['Time End'])
df['Duration'] = df['Time End'].sub(df['Time Start']).dt.total_seconds().div(60)
df = df.drop(columns=['Tips Used 50uL','Tips Used 300uL'])
df = df.loc[(df!=0).any(axis=1)]
df = df[df['Serial Number'] != '0']
df = df[df['Serial Number'] != '0000']
df = df.rename(columns={'Tips Used 1000uL': 'Tips Used'})

columns = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name', 'File Name']

columns_complete = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name']

columns_condensed = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name' ]


######################## Nav Bar Callbacks ########################

######################## Nav Bar Callbacks ########################

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

@app.callback(
    [Output("run-detail-page", "is_open"),
     Output("run-detail-data", "data")],
    [Input("run-detail-button", "n_clicks"),
     Input("close-detail-button", "n_clicks"),
    Input('datatable-hamilton-category', 'data'),
     ],
    [State("run-detail-page", "is_open"),
     State('datatable-hamilton-category', 'selected_rows')]
)
def toggle_modal(n1, n2,rows,is_open, selected_rows):

    df_temp = pd.DataFrame(rows)

    if selected_rows:
        dff = df_temp.loc[selected_rows]
        dff.reset_index(inplace=True)
        filename_col = dff.columns.get_loc('File Name')
        name = dff.iloc[0, filename_col]
        df_detail = read_trace_file_detail(name)
    else:
        df_detail = pd.DataFrame()


    if n1 or n2:
        return not is_open, df_detail.to_dict('records')
    return is_open, df_detail.to_dict('records')

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

# Callback and update BarTender Tables
@app.callback([Output('datatable-bartender-summary', 'data'),
               Output('datatable-bartender-summary', 'tooltip_data')],
	[Input('my-date-picker-range-bartender', 'start_date'),
     Input('my-date-picker-range-bartender', 'end_date'),
Input('bartender-server-select', 'value'),
     ])
def update_data_bartender_summary(start_date, end_date, server_list):
	return update_bartender_summary(start_date, end_date, server_list)

# Callback and update BarTender Tables
@app.callback([Output('datatable-bartender-summary-2', 'data'),
                Output('datatable-bartender-summary-2', 'tooltip_data')],
	[Input('my-date-picker-range-bartender', 'start_date'),
	 Input('my-date-picker-range-bartender', 'end_date'),
Input('bartender-server-select', 'value'),
     ])
def update_data_bartender_summary2(start_date, end_date,server_list):
	return update_bartender_summary2(start_date, end_date,server_list)

# Callback and update BarTender Tables


@app.callback([Output('datatable-bartender-table','data'),
               Output('datatable-bartender-table','tooltip_data')],
              [Input('my-date-picker-range-bartender','start_date'),
               Input('my-date-picker-range-bartender', 'end_date'),
Input('bartender-server-select', 'value'),])
def update_data_bartender_table(start_date, end_date,server_list):
	return update_bartender_table(start_date, end_date,server_list)

#Update Electrostretcher
# Callback and update first data table
@app.callback([Output('datatable-stretcher-table', 'data'),
                Output('datatable-stretcher-table', 'tooltip_data'),
               ],
	[Input('my-date-picker-range-stretcher', 'start_date'),
	 Input('my-date-picker-range-stretcher', 'end_date'),
    Input('stretcher-color-select', 'value')
     ])
def update_data_stretcher(start_date, end_date, colors):
	return update_datatable_stretcher(start_date, end_date, colors)

# Callback and update first data table
@app.callback([Output('datatable-stretcher-summary', 'data'),
                Output('datatable-stretcher-summary', 'tooltip_data'),
               ],
	[Input('my-date-picker-range-stretcher', 'start_date'),
	 Input('my-date-picker-range-stretcher', 'end_date')
     ])
def update_data_summary_stretcher(start_date, end_date):
	return update_summary_stretcher(start_date, end_date)


# Callback for the Graphs
@app.callback(
   Output('es-graph', 'figure'),
    [Input('datatable-stretcher-table', 'derived_virtual_data'),
     Input('datatable-stretcher-table', 'derived_virtual_selected_rows')])

def update_figure(rows, derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
    df_temp = pd.DataFrame() if rows is None else pd.DataFrame(rows)
    all_files = []
    for index,row in df_temp.iterrows():
        if index in derived_virtual_selected_rows:
            name = row['File Path']
            all_files.append(name)
    if len(all_files) > 0:
        df_combine = pd.concat([pd.read_csv(f).assign(name=f) for f in all_files])
        df_combine.columns = df_combine.columns.str.strip()
        new_name = df_combine['name'].str.split("\\", expand=True)
        new_name_count = len(new_name.columns)
        df_combine['File Name'] = new_name[new_name_count - 2] + '\\' + new_name[new_name_count - 1]
        df_combine['Lane 1'] = 'Lane 1'
        df_combine['Lane 2'] = 'Lane 2'
        df_combine['Lane 3'] = 'Lane 3'
        df_combine['Lane 4'] = 'Lane 4'
        df_combine['Lane 5'] = 'Lane 5'
        df_combine['Lane 6'] = 'Lane 6'
    else:
        df_combine = pd.DataFrame()

    fig = es_graph(df_combine)
    return fig

# Callback and update first data table
@app.callback([Output('datatable-generator-duplicates', 'data'),
                Output('datatable-generator-duplicates', 'tooltip_data'),
                              ],
	[Input('my-date-picker-range-generator', 'start_date'),
	 Input('my-date-picker-range-generator', 'end_date')
     ])
def update_gen_duplicates(start_date, end_date):
	return update_generator_duplicates()

# Callback and update first data table
@app.callback([Output('datatable-generator-duplicates2', 'data'),
                Output('datatable-generator-duplicates2', 'tooltip_data'),
                              ],
	[Input('my-date-picker-range-generator', 'start_date'),
	 Input('my-date-picker-range-generator', 'end_date')
     ])
def update_gen_duplicates2(start_date, end_date):
	return update_generator_duplicates2(start_date, end_date)

# Callback and update first data table
@app.callback([Output('datatable-generator', 'data'),
                Output('datatable-generator', 'tooltip_data'),
               ],
	[Input('my-date-picker-range-generator', 'start_date'),
	 Input('my-date-picker-range-generator', 'end_date')
     ])
def update_data_table_generator(start_date, end_date):
	return update_generator_table(start_date, end_date)
