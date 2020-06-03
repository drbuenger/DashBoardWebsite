from datetime import datetime as dt
from datetime import date, timedelta
from datetime import datetime
import plotly.graph_objs as go
from plotly import tools
import numpy as np
import pandas as pd
import csv
import os
pd.options.mode.chained_assignment = None

# Read in Hamilton Data
df = pd.read_csv('C:\\Users\\dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\data\\Hamilton.csv')

df['Time Start'] = pd.to_datetime(df['Time Start'])
df['Time End'] = pd.to_datetime(df['Time End'])

now = datetime.now()
datestamp = now.strftime("%Y%m%d")

df['Duration'] = df['Time End'] - df['Time Start']

unique_serial_numbers = df['Serial Number'].unique()

columns = ['Time Start', 'Time End', 'Serial Number', 'Method Name', 'Duration', 'User Name']


# Define Formatters
def formatter_currency(x):
    return "${:,.0f}".format(x) if x >= 0 else "(${:,.0f})".format(abs(x))


def formatter_currency_with_cents(x):
    return "${:,.2f}".format(x) if x >= 0 else "(${:,.2f})".format(abs(x))


def formatter_percent(x):
    return "{:,.1f}%".format(x) if x >= 0 else "({:,.1f}%)".format(abs(x))


def formatter_percent_2_digits(x):
    return "{:,.2f}%".format(x) if x >= 0 else "({:,.2f}%)".format(abs(x))


def formatter_number(x):
    return "{:,.0f}".format(x) if x >= 0 else "({:,.0f})".format(abs(x))

# Read Text File
def read_trace_file(file):
    method_name = "NA"
    serialnumber = "NA"
    username = "NA"
    date_start = "NA"
    date_end = "NA"
    if file is not None:
        f = open(file, 'r')
        for readline in f:
            if 'Analyze method - start' in readline:
                array_read_line = readline.split("\\")
                length = len(array_read_line)
                method_name = array_read_line[length-1].rstrip("'\n\t’")
            if 'Analyze method - start' in readline:
                date_start = readline[0:19]
            if 'User name' in readline:
                array_read_line = readline.split(" ")
                length = len(array_read_line)
                username = array_read_line[length-1].rstrip("'\n\t’")
            if 'Serial number of Instrument' in readline:
                array_read_line = readline.split(" ")
                length = len(array_read_line)
                serialnumber= array_read_line[length - 1].rstrip("'\n\t’")
            if 'End method - complete' in readline:
                date_end = readline[0:19]
        f.close()
    if method_name is not None:
        with open('C:\\Users\\dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\data\\Hamilton.csv', 'a',newline='') as file_write:
            writer = csv.writer(file_write)
            writer.writerow([method_name, date_start, username, serialnumber, date_end])

# First Data Table Update Function
def update_first_datatable(start_date, end_date, serial_number):

    if start_date is not None:
        start_date = dt.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
        start_date_string = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    if end_date is not None:
        end_date = dt.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
        end_date_string = end_date.strftime('%Y-%m-%dT%H:%M:%S')
    days_selected = (end_date - start_date).days

    prior_start_date = start_date - timedelta(days_selected + 1)
    prior_start_date_string = datetime.strftime(prior_start_date, '%Y-%m-%dT%H:%M:%S')
    prior_end_date = end_date - timedelta(days_selected + 1)
    prior_end_date_string = datetime.strftime(prior_end_date, '%Y-%m-%dT%H:%M:%S')

    df1 = df[(df['Serial Number'] == serial_number)].reset_index()
    data_df = df1.to_dict("rows")
    return data_df


# First Data Table Download Function
def update_first_download(start_date, end_date, serial_number):
    if start_date is not None:
        start_date = dt.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
        start_date_string = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    if end_date is not None:
        end_date = dt.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
        end_date_string = end_date.strftime('%Y-%m-%dT%H:%M:%S')
    days_selected = (end_date - start_date).days

    prior_start_date = start_date - timedelta(days_selected + 1)
    prior_start_date_string = datetime.strftime(prior_start_date, '%Y-%m-%dT%H:%M:%S')
    prior_end_date = end_date - timedelta(days_selected + 1)
    prior_end_date_string = datetime.strftime(prior_end_date, '%Y-%m-%dT%H:%M:%S')
    df1 = df[(df['Serial Number'] == serial_number)].reset_index()
    data_df = df1.to_dict("rows")
    return data_df


# Second Data Table Update Function
def update_second_datatable(start_date, end_date,serial_number):
    if start_date is not None:
        start_date = dt.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
        start_date_string = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    if end_date is not None:
        end_date = dt.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
        end_date_string = end_date.strftime('%Y-%m-%dT%H:%M:%S')
    days_selected = (end_date - start_date).days

    prior_start_date = start_date - timedelta(days_selected + 1)
    prior_start_date_string = datetime.strftime(prior_start_date, '%Y-%m-%dT%H:%M:%S')
    prior_end_date = end_date - timedelta(days_selected + 1)
    prior_end_date_string = datetime.strftime(prior_end_date, '%Y-%m-%dT%H:%M:%S:%S')

    df1 = df[(df['Serial Number'] == serial_number)].reset_index()
    data_df = df1.to_dict("rows")
    return data_df


######################## FOR GRAPHS  ########################

def update_graph(filtered_df, end_date):

    if end_date is not None:
        end_date = dt.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
        end_date_string = end_date.strftime('%Y-%m-%dT%H:%M:%S')
    current_year = end_date_string[0:3]

    # Sessions Graphs
    sessions_ty = go.Scatter(
        x=[1,2,3,4,5],
        y=[2,4,6,8,10],
        text='Test Scatter'
    )
    # sessions_ly = go.Scatter(
    #     x=filtered_df[(filtered_df['Year'] == current_year - 1)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year - 1)]['Sessions - TY'],
    #     text='Sessions - LY'
    # )
    # sessions_yoy = go.Bar(
    #     x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year)]['Sessions YoY (%)'],
    #     text='Sessions YoY (%)', opacity=0.6
    # )
    # # Spend Graphs
    # spend_ty = go.Scatter(
    #     x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year)]['Spend TY'],
    #     text='Spend TY'
    # )
    # spend_ly = go.Scatter(
    #     x=filtered_df[(filtered_df['Year'] == current_year - 1)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year - 1)]['Spend TY'],
    #     text='Spend LY'
    # )
    # spend_yoy = go.Bar(
    #     x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year)]['Spend YoY (%)'],
    #     text='Spend YoY (%)', opacity=0.6
    # )
    # # Bookings Graphs
    # bookings_ty = go.Scatter(
    #     x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year)]['Bookings - TY'],
    #     text='Bookings - TY'
    # )
    # bookings_ly = go.Scatter(
    #     x=filtered_df[(filtered_df['Year'] == current_year - 1)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year - 1)]['Bookings - TY'],
    #     text='Bookings - LY'
    # )
    # bookings_yoy = go.Bar(
    #     x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year)]['Bookings - % - PY'],
    #     text='Bookings - % - PY', opacity=0.6
    # )
    # cpa_ty = go.Scatter(
    #     x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year)]['CPA - TY'],
    #     text='CPA - TY'
    # )
    # cpa_ly = go.Scatter(
    #     x=filtered_df[(filtered_df['Year'] == current_year - 1)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year - 1)]['CPA - TY'],
    #     text='CPA - LY'
    # )
    # cpa_yoy = go.Bar(
    #     x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year)]['% YoY_CPA'],
    #     text='% CPA - YoY', opacity=0.6
    # )
    # cps_ty = go.Scatter(
    #     x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year)]['CPS - TY'],
    #     text='CPS - TY'
    # )
    # cps_ly = go.Scatter(
    #     x=filtered_df[(filtered_df['Year'] == current_year - 1)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year - 1)]['CPS - TY'],
    #     text='CPS - LY'
    # )
    # cps_yoy = go.Bar(
    #     x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year)]['% YoY_CPS'],
    #     text='% CPS - YoY', opacity=0.6
    # )
    # cr_ty = go.Scatter(
    #     x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year)]['CVR - TY'],
    #     text='CVR - TY'
    # )
    # cr_ly = go.Scatter(
    #     x=filtered_df[(filtered_df['Year'] == current_year - 1)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year - 1)]['CVR - TY'],
    #     text='CVR - LY'
    # )
    # cr_yoy = go.Bar(
    #     x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
    #     y=filtered_df[(filtered_df['Year'] == current_year)]['CVR YoY (Abs)'],
    #     text='CVR YoY (Abs)', opacity=0.6
    # )

    fig = tools.make_subplots(
        rows=1,
        cols=1,
        shared_xaxes=True,
        subplot_titles=(  # Be sure to have same number of titles as number of graphs
            'Sessions',
            'Spend',
            'Bookings',
            'Cost per Acquisition',
            'CPS',
            'Conversion Rate'
        ))

    fig.append_trace(sessions_ty, 1, 1)  # 0
    # fig.append_trace(sessions_ly, 1, 1)  # 1
    # fig.append_trace(sessions_yoy, 1, 1)  # 2
    # fig.append_trace(spend_ty, 2, 1)  # 3
    # fig.append_trace(spend_ly, 2, 1)  # 4
    # fig.append_trace(spend_yoy, 2, 1)  # 5
    # fig.append_trace(bookings_ty, 3, 1)  # 6
    # fig.append_trace(bookings_ly, 3, 1)  # 7
    # fig.append_trace(bookings_yoy, 3, 1)  # 8
    # fig.append_trace(cpa_ty, 4, 1)  # 9
    # fig.append_trace(cpa_ly, 4, 1)  # 10
    # fig.append_trace(cpa_yoy, 4, 1)  # 11
    # fig.append_trace(cps_ty, 5, 1)  # 12
    # fig.append_trace(cps_ly, 5, 1)  # 13
    # fig.append_trace(cps_yoy, 5, 1)  # 14
    # fig.append_trace(cr_ty, 6, 1)  # 15
    # fig.append_trace(cr_ly, 6, 1)  # 16
    # fig.append_trace(cr_yoy, 6, 1)  # 17

    # integer index below is the index of the trace
    # yaxis indices below need to start from the number of total graphs + 1 since they are on right-side
    # overlaing and anchor axes correspond to the graph number
    #
    # fig['data'][2].update(yaxis='y7')
    # fig['layout']['yaxis7'] = dict(overlaying='y1', anchor='x1', side='right', showgrid=False, title='% Change YoY')
    #
    # fig['data'][5].update(yaxis='y8')
    # fig['layout']['yaxis8'] = dict(overlaying='y2', anchor='x2', side='right', showgrid=False, title='% Change YoY')
    #
    # fig['data'][8].update(yaxis='y9')
    # fig['layout']['yaxis9'] = dict(overlaying='y3', anchor='x3', side='right', showgrid=False, title='% Change YoY')
    #
    # fig['data'][11].update(yaxis='y10')
    # fig['layout']['yaxis10'] = dict(overlaying='y4', anchor='x4', side='right', showgrid=False, title='% Change YoY')
    #
    # fig['data'][14].update(yaxis='y11')
    # fig['layout']['yaxis11'] = dict(overlaying='y5', anchor='x5', side='right', showgrid=False, title='% Change YoY')
    #
    # fig['data'][17].update(yaxis='y12')
    # fig['layout']['yaxis12'] = dict(overlaying='y6', anchor='x6', side='right', showgrid=False, title='% Change YoY')

    fig['layout']['xaxis'].update(title='Week of the Year' + ' - ' + str(current_year))
    for i in fig['layout']['annotations']:
        i['font'] = dict(size=12,
                         # color='#ff0000'
                         )
    fig['layout'].update(
        height=1500,
        # width=750,
        showlegend=False,
        xaxis=dict(
            # tickmode='linear',
            # ticks='outside',
            # tick0=1,
            dtick=5,
            ticklen=8,
            tickwidth=2,
            tickcolor='#000',
            showgrid=True,
            zeroline=True,
            # showline=True,
            # mirror='ticks',
            # gridcolor='#bdbdbd',
            gridwidth=2
        ),
    )
    updated_fig = fig
    return updated_fig
