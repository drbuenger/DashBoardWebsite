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
from components import update_first_datatable, update_first_download, update_second_datatable, update_graph


pd.options.mode.chained_assignment = None

df = pd.read_csv('C:\\Users\\dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\data\\Hamilton.csv')

df['Time Start'] = pd.to_datetime(df['Time Start'])
df['Time End'] = pd.to_datetime(df['Time End'])

now = datetime.now()
datestamp = now.strftime("%Y%m%d")

current_year = df['Time End'].max().to_pydatetime().year

now = datetime.now()
datestamp = now.strftime("%Y%m%d")

columns = ['Spend TY', 'Spend LY', 'Sessions - TY', 'Sessions - LY', 'Bookings - TY', 'Bookings - LY', 'Revenue - TY', 'Revenue - LY']

columns_complete = ['Placement type', 'Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY', 'Spend YoY (%)', \
                        'Sessions - TY', 'Sessions - LP', 'Sessions - LY', 'Sessions PoP (%)', 'Sessions YoY (%)', \
                        'Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)', 'Bookings PoP (Abs)', 'Bookings - LY', 'Bookings YoY (%)', 'Bookings YoY (Abs)', \
                        'Revenue - TY', 'Revenue - LP', 'Revenue PoP (Abs)', 'Revenue PoP (%)', 'Revenue - LY', 'Revenue YoY (%)', 'Revenue YoY (Abs)']

columns_condensed = ['Placement type', 'Spend TY', 'Spend PoP (%)', 'Spend YoY (%)', 'Sessions - TY', 'Sessions PoP (%)', 'Sessions YoY (%)', \
                        'Bookings - TY',  'Bookings PoP (%)', 'Bookings YoY (%)',]

conditional_columns = ['Spend_PoP_abs_conditional', 'Spend_PoP_percent_conditional', 'Spend_YoY_percent_conditional',
'Sessions_PoP_percent_conditional', 'Sessions_YoY_percent_conditional',
'Bookings_PoP_abs_conditional', 'Bookings_YoY_abs_conditional', 'Bookings_PoP_percent_conditional', 'Bookings_YoY_percent_conditional',
'Revenue_PoP_abs_conditional', 'Revenue_YoY_abs_conditional', 'Revenue_PoP_percent_conditional', 'Revenue_YoY_percent_conditional',]

dt_columns_total = ['Placement type', 'Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY', 'Spend YoY (%)', \
                        'Sessions - TY', 'Sessions - LP', 'Sessions - LY', 'Sessions PoP (%)', 'Sessions YoY (%)', \
                        'Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)', 'Bookings PoP (Abs)', 'Bookings - LY', 'Bookings YoY (%)', 'Bookings YoY (Abs)', \
                        'Revenue - TY', 'Revenue - LP', 'Revenue PoP (Abs)', 'Revenue PoP (%)', 'Revenue - LY', 'Revenue YoY (%)', 'Revenue YoY (Abs)',
                        'Spend_PoP_abs_conditional', 'Spend_PoP_percent_conditional', 'Spend_YoY_percent_conditional',
'Sessions_PoP_percent_conditional', 'Sessions_YoY_percent_conditional',
'Bookings_PoP_abs_conditional', 'Bookings_YoY_abs_conditional', 'Bookings_PoP_percent_conditional', 'Bookings_YoY_percent_conditional',
'Revenue_PoP_abs_conditional', 'Revenue_YoY_abs_conditional', 'Revenue_PoP_percent_conditional', 'Revenue_YoY_percent_conditional',]

######################## Hamilton Category Callbacks ########################

#### Date Picker Callback
@app.callback(Output('output-container-date-picker-range-hamilton-category', 'children'),
	[Input('my-date-picker-range-hamilton-category', 'start_date'),
	 Input('my-date-picker-range-hamilton-category', 'end_date')])
def update_output(start_date, end_date):
    string_prefix = 'You have selected '
    if start_date is not None:
        start_date = dt.strptime(start_date, '%Y-%m-%d')
        start_date_string = start_date.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'a Start Date of ' + start_date_string + ' | '
    if end_date is not None:
        end_date = dt.strptime(end_date, '%Y-%m-%d')
        end_date_string = end_date.strftime('%B %d, %Y')
        days_selected = (end_date - start_date).days
        prior_start_date = start_date - timedelta(days_selected + 1)
        prior_start_date_string = datetime.strftime(prior_start_date, '%B %d, %Y')
        prior_end_date = end_date - timedelta(days_selected + 1)
        prior_end_date_string = datetime.strftime(prior_end_date, '%B %d, %Y')
        string_prefix = string_prefix + 'End Date of ' + end_date_string + ', for a total of ' + str(days_selected + 1) + ' Days. The prior period Start Date was ' + \
		prior_start_date_string + ' | End Date: ' + prior_end_date_string + '.'
    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here'
    else:
        return string_prefix

# Callback and update first data table
@app.callback(Output('datatable-hamilton-category', 'data'),
	[Input('my-date-picker-range-hamilton-category', 'start_date'),
	 Input('my-date-picker-range-hamilton-category', 'end_date')])
def update_data_1(start_date, end_date):
	data_1 = update_first_datatable(start_date, end_date, None, 'Hamilton Category')
	return data_1

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
	 Input('my-date-picker-range-hamilton-category', 'end_date')])
def update_link(start_date, end_date):
	return '/Reports/Hamilton/urlToDownload?value={}/{}'.format(dt.strptime(start_date,'%Y-%m-%d').strftime('%Y-%m-%d'),dt.strptime(end_date,'%Y-%m-%d').strftime('%Y-%m-%d'))
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
    download_1 = update_first_download(start_date, end_date, None, 'Hamilton Category')
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
	 Input('my-date-picker-range-hamilton-category', 'end_date')])
def update_data_2(start_date, end_date):
	data_2 = update_second_datatable(start_date, end_date, None, 'Hamilton Category')
	return data_2

# Callback for the Graphs
@app.callback(
   Output('hamilton-category', 'figure'),
   [Input('datatable-hamilton-category', "selected_rows"),
   Input('my-date-picker-range-hamilton-category', 'end_date'),
    Input('dropdown-input-hamilton', 'selected_hamilton')])
def update_hamilton_category(selected_rows, end_date, selected_hamilton):
	travel_product = []
	travel_product_list = sorted(df['Hamilton Category'].unique().tolist())
	for i in selected_rows:
		travel_product.append(travel_product_list[i])
		# Filter by specific product
	filtered_df = df[(df['Hamilton Category'].isin(travel_product))].groupby(['Year', 'Week']).sum()[['Spend TY', 'Spend LY', 'Sessions - TY', 'Sessions - LY', 'Bookings - TY', 'Bookings - LY', 'Revenue - TY', 'Revenue - LY']].reset_index()
	fig = update_graph(filtered_df, end_date)
	return fig

######################## Extra Category Callbacks ########################

#### Date Picker Callback
@app.callback(Output('output-container-date-picker-range-extra-category', 'children'),
	[Input('my-date-picker-range-extra-category', 'start_date'),
	 Input('my-date-picker-range-extra-category', 'end_date')])
def update_output(start_date, end_date):
	string_prefix = 'You have selected '
	if start_date is not None:
		start_date = dt.strptime(start_date, '%Y-%m-%d')
		start_date_string = start_date.strftime('%B %d, %Y')
		string_prefix = string_prefix + 'a Start Date of ' + start_date_string + ' | '
	if end_date is not None:
		end_date = dt.strptime(end_date, '%Y-%m-%d')
		end_date_string = end_date.strftime('%B %d, %Y')
		days_selected = (end_date - start_date).days
		prior_start_date = start_date - timedelta(days_selected + 1)
		prior_start_date_string = datetime.strftime(prior_start_date, '%B %d, %Y')
		prior_end_date = end_date - timedelta(days_selected + 1)
		prior_end_date_string = datetime.strftime(prior_end_date, '%B %d, %Y')
		string_prefix = string_prefix + 'End Date of ' + end_date_string + ', for a total of ' + str(days_selected + 1) + ' Days. The prior period Start Date was ' + \
		prior_start_date_string + ' | End Date: ' + prior_end_date_string + '.'
	if len(string_prefix) == len('You have selected: '):
		return 'Select a date to see it displayed here'
	else:
		return string_prefix

# Callback and update first data table
@app.callback(Output('datatable-extra-category', 'data'),
	[Input('my-date-picker-range-extra-category', 'start_date'),
	 Input('my-date-picker-range-extra-category', 'end_date')])
def update_data_1(start_date, end_date):
	data_1 = update_first_datatable(start_date, end_date, None, 'Extra Category')
	return data_1

# Callback and update data table columns
@app.callback(Output('datatable-extra-category', 'columns'),
    [Input('radio-button-extra-category', 'value')])
def update_columns(value):
    if value == 'Complete':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_complete]
    elif value == 'Condensed':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_condensed]
    return column_set

# Callback for excel download
@app.callback(
    Output('download-link-extra-category', 'href'),
    [Input('my-date-picker-range-extra-category', 'start_date'),
	 Input('my-date-picker-range-extra-category', 'end_date')])
def update_link(start_date, end_date):
	return '/Reports/Extra/urlToDownload?value={}/{}'.format(dt.strptime(start_date,'%Y-%m-%d').strftime('%Y-%m-%d'),dt.strptime(end_date,'%Y-%m-%d').strftime('%Y-%m-%d'))
@app.server.route("/Reports/Extra/urlToDownload")
def download_excel_extra_category():
    value = flask.request.args.get('value')
    #here is where I split the value
    value = value.split('/')
    start_date = value[0]
    end_date = value[1]

    filename = datestamp + '_extra_category_' + start_date + '_to_' + end_date + '.xlsx'
	# Dummy Dataframe
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)

    buf = io.BytesIO()
    excel_writer = pd.ExcelWriter(buf, engine="xlsxwriter")
    download_1 = update_first_download(start_date, end_date, None, 'Extra Category')
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
	Output('datatable-extra-category-2', 'data'),
	[Input('my-date-picker-range-extra-category', 'start_date'),
	 Input('my-date-picker-range-extra-category', 'end_date')])
def update_data_2(start_date, end_date):
	data_2 = update_second_datatable(start_date, end_date, None, 'Extra Category')
	return data_2

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

# Callback and update first data table
@app.callback(Output('datatable-metasearch', 'data'),
	[Input('my-date-picker-range-metasearch', 'start_date'),
	 Input('my-date-picker-range-metasearch', 'end_date')])
def update_data_1_metasearch(start_date, end_date):
	data_1 = update_first_datatable(start_date, end_date, 'Metasearch and Travel Ads', 'Placement type')
	return data_1

# Callback and update data table columns
@app.callback(Output('datatable-metasearch', 'columns'),
    [Input('radio-button-metasearch', 'value')])
def update_columns(value):
    if value == 'Complete':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_complete]
    elif value == 'Condensed':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_condensed]
    return column_set

# Callback for excel download
@app.callback(
    Output('download-link-metasearch-1', 'href'),
    [Input('my-date-picker-range-metasearch', 'start_date'),
	 Input('my-date-picker-range-metasearch', 'end_date')])
def update_link(start_date, end_date):
	return '/cc-travel-report/metasearch/urlToDownload?value={}/{}'.format(dt.strptime(start_date,'%Y-%m-%d').strftime('%Y-%m-%d'),dt.strptime(end_date,'%Y-%m-%d').strftime('%Y-%m-%d'))
@app.server.route("/cc-travel-report/metasearch/urlToDownload")
def download_excel_metasearch_1():
    value = flask.request.args.get('value')
    #here is where I split the value
    value = value.split('/')
    start_date = value[0]
    end_date = value[1]

    filename = datestamp + '_metasearch_' + start_date + '_to_' + end_date + '.xlsx'
	# Dummy Dataframe
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)

    buf = io.BytesIO()
    excel_writer = pd.ExcelWriter(buf, engine="xlsxwriter")
    download_1 = update_first_download(start_date, end_date, 'Metasearch and Travel Ads', 'Placement type')
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
	Output('datatable-metasearch-2', 'data'),
	[Input('my-date-picker-range-metasearch', 'start_date'),
	 Input('my-date-picker-range-metasearch', 'end_date')])
def update_data_2_metasearch(start_date, end_date):
	data_2 = update_second_datatable(start_date, end_date, 'Metasearch and Travel Ads', 'Placement type')
	return data_2

# Callback for the Graphs
@app.callback(
   Output('metasearch', 'figure'),
   [Input('datatable-metasearch', "selected_rows"),
	 Input('my-date-picker-range-metasearch', 'end_date')])
def update_metasearch(selected_rows, end_date):
	travel_product = []
	travel_product_list = df[(df['Category'] == 'Metasearch and Travel Ads')]['Placement type'].unique().tolist()
	for i in selected_rows:
		travel_product.append(travel_product_list[i])
		# Filter by specific product
	filtered_df = df[(df['Placement type'].isin(travel_product))].groupby(['Year', 'Week']).sum()[['Spend TY', 'Spend LY', 'Sessions - TY', 'Sessions - LY', 'Bookings - TY', 'Bookings - LY', 'Revenue - TY', 'Revenue - LY']].reset_index()
	fig = update_graph(filtered_df, end_date)
	return fig