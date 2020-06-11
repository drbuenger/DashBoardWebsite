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
#df.astype({'Duration': 'float64'}).dtypes
now = datetime.now()
datestamp = now.strftime("%Y%m%d")

unique_serial_numbers = df['Serial Number'].unique()


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

def formatter_number_one_dec(x):
    return "{:,.1f}".format(x) if x >= 0 else "({:,.1f})".format(abs(x))

# Read Text File
def read_trace_file(file):
    method_name = "NA"
    serialnumber = "NA"
    username = "NA"
    date_start = "NA"
    date_end = "NA"
    method_aborted = "No"
    tips_used50uL = 0
    tips_used300uL = 0
    tips_used1000uL = 0
    aspirating_count = 0
    aspirating_time = 0
    aspirating_start = ""
    aspirating_end =  ""
    dispensing_count = 0
    dispensing_time = 0
    dispensing_start = ""
    dispensing_end =  ""
    pickup_count = 0
    pickup_time = 0
    pickup_start = ""
    pickup_end =  ""
    eject_count = 0
    eject_time = 0
    eject_start = ""
    eject_end =  ""
    user_start = ""
    user_end =  ""
    user_count = 0
    user_time = 0

    if file is not None:
        f = open(file, 'r')
        for readline in f:
            if 'Analyze method - start' in readline:
                array_read_line = readline.split("\\")
                length = len(array_read_line)
                method_name = array_read_line[length-1].rstrip("'.hsl\n\t’")
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
            if '1000µl Channel Tip Eject (Single Step) - complete' in readline:
                tips_used1000uL += 8
            if '300µl Channel Tip Eject (Single Step) - complete' in readline:
                tips_used300uL += 8
            if '50µl Channel Tip Eject (Single Step) - complete' in readline:
                tips_used50uL += 8
            if 'CO-RE 96 Head Tip Eject (Single Step) - complete' in readline:
                tips_used1000uL += 96
            if 'End method - complete' in readline:
                date_end = readline[0:19]
            if 'Abort command - complete' in readline:
                method_aborted = "Yes"
            if 'Aspirate (Single Step) - start' in readline:
                aspirating_start = readline[11:19]
            if 'Aspirate (Single Step) - complete' in readline:
                aspirating_end = readline[11:19]
            if aspirating_end != "" and aspirating_start != "":
                aspirating_count = aspirating_count + 1
                aspirating_time = aspirating_time + (dt.strptime(aspirating_end, '%H:%M:%S') - dt.strptime(aspirating_start, '%H:%M:%S')).seconds
                aspirating_start = ""
                aspirating_end = ""
            if 'Dispense (Single Step) - start' in readline:
                dispensing_start = readline[11:19]
            if 'Dispense (Single Step) - complete' in readline:
                dispensing_end = readline[11:19]
            if dispensing_end != "" and dispensing_start != "":
                dispensing_count = dispensing_count + 1
                dispensing_time = dispensing_time + (dt.strptime(dispensing_end, '%H:%M:%S') - dt.strptime(dispensing_start, '%H:%M:%S')).seconds
                dispensing_start = ""
                dispensing_end = ""
            if 'Tip Pick Up (Single Step) - start' in readline:
                pickup_start = readline[11:19]
            if 'Tip Pick Up (Single Step) - complete' in readline:
                pickup_end = readline[11:19]
            if pickup_end != "" and pickup_start != "":
                pickup_count = pickup_count + 1
                pickup_time = pickup_time + (dt.strptime(pickup_end, '%H:%M:%S') - dt.strptime(pickup_start, '%H:%M:%S')).seconds
                pickup_start = ""
                pickup_end = ""
            if 'Tip Eject (Single Step) - start' in readline:
                eject_start = readline[11:19]
            if 'Tip Eject (Single Step) - complete' in readline:
                eject_end = readline[11:19]
            if eject_end != "" and eject_start != "":
                eject_count = eject_count + 1
                eject_time = eject_time + (dt.strptime(eject_end, '%H:%M:%S') - dt.strptime(eject_start, '%H:%M:%S')).seconds
                eject_start = ""
                eject_end = ""
            if 'Dialog - start' in readline:
                user_start = readline[11:19]
            if 'Dialog - complete' in readline:
                user_end = readline[11:19]
            if user_end != "" and user_start != "":
                user_count = user_count + 1
                user_time = user_time + (dt.strptime(user_end, '%H:%M:%S') - dt.strptime(user_start, '%H:%M:%S')).seconds
                user_start = ""
                user_end = ""
        f.close()
    if method_name is not None:
        with open('C:\\Users\\dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\data\\Hamilton.csv', 'a',newline='') as file_write:
            writer = csv.writer(file_write)
            writer.writerow([method_name,
                             date_start,
                             date_end,
                             username,
                             serialnumber,
                             tips_used1000uL,
                             tips_used300uL,
                             tips_used50uL,
                             method_aborted,
                             aspirating_count,
                             aspirating_time,
                             dispensing_count,
                             dispensing_time,
                             pickup_count,
                             pickup_time,
                             eject_count,
                             eject_time,
                             user_count,
                             user_time
                             ])

# First Data Table Update Function
def update_first_datatable(start_date, end_date, serial_number):

    df1 = df.loc[(df['Serial Number'] == serial_number) & (df['Time Start'] >= start_date) & (df['Time End'] <= end_date)]
    df1['Time Start'] = df1['Time Start'].dt.strftime("%Y/%m/%d %H:%M:%S")
    df1['Time End'] = df1['Time End'].dt.strftime("%Y/%m/%d %H:%M:%S")
    df1.sort_values(by=['Time End'],inplace=True, ascending=False)
    df1['Duration']= df1['Duration'].apply(lambda x:formatter_number_one_dec(x))
    tooltip_data = [
                       {
                           column: {'value': str(value), 'type': 'markdown'}
                           for column, value in row.items()
                       } for row in df1.to_dict('rows')
                   ]
    return df1.to_dict('records'), tooltip_data

def count_nos(col):
    return np.sum(col == 'No')

# First Data Table Update Function
def update_summary_datatable(start_date, end_date, serial_number):
    df1 = df.loc[(df['Serial Number'] == serial_number) & (df['Time Start'] >= start_date) & (df['Time End'] <= end_date)]
    df1['Time Start'] = df1['Time Start'].dt.strftime("%Y/%m/%d %H:%M:%S")
    df1['Time End'] = df1['Time End'].dt.strftime("%Y/%m/%d %H:%M:%S")

    df2 = df1.groupby('Method Name').agg(
        Total=pd.NamedAgg(column='Method Name', aggfunc='count'),
        Average = pd.NamedAgg(column='Duration', aggfunc='mean'),
        TipsUsed = pd.NamedAgg(column='Tips Used', aggfunc=np.sum),
        SuccessCount=pd.NamedAgg(column='Aborted', aggfunc=count_nos)
                               ).reset_index()

    df2['Success %'] = df2['SuccessCount']/df2['Total'] * 100
    df2['Average'] = df2['Average'].apply(lambda x: formatter_number_one_dec(x))
    df2.sort_values(by=['Method Name'],inplace=True)
    tooltip_data = [
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in df2.to_dict('rows')
    ]
    return df2.to_dict('records'), tooltip_data


# First Data Table Update Function
def update_first_datatable_time(start_date, end_date, serial_number):

    df1 = df.loc[(df['Serial Number'] == serial_number) & (df['Time Start'] >= start_date) & (df['Time End'] <= end_date)]
    df1['Time Start'] = df1['Time Start'].dt.strftime("%Y/%m/%d %H:%M:%S")
    df1['Time End'] = df1['Time End'].dt.strftime("%Y/%m/%d %H:%M:%S")
    df1.sort_values(by=['Time End'],inplace=True, ascending=False)
    tooltip_data = [
                       {
                           column: {'value': str(value), 'type': 'markdown'}
                           for column, value in row.items()
                       } for row in df1.to_dict('rows')
                   ]
    return df1.to_dict('records'), tooltip_data



# First Data Table Update Function
def update_summary_datatable_time(start_date, end_date, serial_number):
    df1 = df.loc[(df['Serial Number'] == serial_number) & (df['Time Start'] >= start_date) & (df['Time End'] <= end_date)]
    df1['Time Start'] = df1['Time Start'].dt.strftime("%Y/%m/%d %H:%M:%S")
    df1['Time End'] = df1['Time End'].dt.strftime("%Y/%m/%d %H:%M:%S")

    df2 = df1.groupby('Method Name').agg(
        TotalDispenseTime=pd.NamedAgg(column='Dispensing Time', aggfunc=np.sum),
        TotalDispenseCount = pd.NamedAgg(column='Dispensing Count', aggfunc=np.sum),
        TotalAspirateTime=pd.NamedAgg(column='Aspirating Time', aggfunc=np.sum),
        TotalAspirateCount = pd.NamedAgg(column='Aspirating Count', aggfunc=np.sum),
        TotalPickupTime=pd.NamedAgg(column='Tip Pickup Time', aggfunc=np.sum),
        TotalPickupCount=pd.NamedAgg(column='Tip Pickup Count', aggfunc=np.sum),
        TotalEjectTime=pd.NamedAgg(column='Tip Eject Time', aggfunc=np.sum),
        TotalEjectCount=pd.NamedAgg(column='Tip Eject Count', aggfunc=np.sum),
        TotalUserTime=pd.NamedAgg(column='User Time', aggfunc=np.sum),
        TotalUserCount=pd.NamedAgg(column='User Count', aggfunc=np.sum),
                               ).reset_index()

    df2['Average Dispense'] = df2['TotalDispenseTime'] / df2['TotalDispenseCount']
    df2['Average Aspirate'] =df2['TotalAspirateTime'] / df2['TotalAspirateCount']
    df2['Average Pickup'] =df2['TotalPickupTime'] / df2['TotalPickupCount']
    df2['Average Eject'] =df2['TotalEjectTime'] / df2['TotalEjectCount']
    df2['Average User'] = df2['TotalUserTime'] / df2['TotalUserCount']

    df2['Average Dispense'] = df2['Average Dispense'].apply(lambda x: formatter_number_one_dec(x))
    df2['Average Aspirate'] = df2['Average Aspirate'].apply(lambda x: formatter_number_one_dec(x))
    df2['Average Pickup'] = df2['Average Pickup'].apply(lambda x: formatter_number_one_dec(x))
    df2['Average Eject'] = df2['Average Eject'].apply(lambda x: formatter_number_one_dec(x))
    df2['Average User'] = df2['Average User'].apply(lambda x: formatter_number_one_dec(x))

    df2.sort_values(by=['Method Name'],inplace=True)

    tooltip_data = [
                       {
                           column: {'value': str(value), 'type': 'markdown'}
                           for column, value in row.items()
                       } for row in df2.to_dict('rows')
                   ]
    return df2.to_dict('records'), tooltip_data

def update_summary_datatable_time2(start_date, end_date, serial_number):
    df1 = df.loc[(df['Serial Number'] == serial_number) & (df['Time Start'] >= start_date) & (df['Time End'] <= end_date)]
    df1['Time Start'] = df1['Time Start'].dt.strftime("%Y/%m/%d %H:%M:%S")
    df1['Time End'] = df1['Time End'].dt.strftime("%Y/%m/%d %H:%M:%S")

    df2 = df1.groupby('Method Name').agg(
        TotalDispenseTime=pd.NamedAgg(column='Dispensing Time', aggfunc=np.sum),
        TotalDispenseCount = pd.NamedAgg(column='Dispensing Count', aggfunc=np.sum),
        TotalAspirateTime=pd.NamedAgg(column='Aspirating Time', aggfunc=np.sum),
        TotalAspirateCount = pd.NamedAgg(column='Aspirating Count', aggfunc=np.sum),
        TotalPickupTime=pd.NamedAgg(column='Tip Pickup Time', aggfunc=np.sum),
        TotalPickupCount=pd.NamedAgg(column='Tip Pickup Count', aggfunc=np.sum),
        TotalEjectTime=pd.NamedAgg(column='Tip Eject Time', aggfunc=np.sum),
        TotalEjectCount=pd.NamedAgg(column='Tip Eject Count', aggfunc=np.sum),
        TotalUserTime=pd.NamedAgg(column='User Time', aggfunc=np.sum),
        TotalUserCount=pd.NamedAgg(column='User Count', aggfunc=np.sum),
        Average=pd.NamedAgg(column='Duration', aggfunc='mean'),
                               ).reset_index()
    df2['Total Time Seconds'] = df2['TotalDispenseTime'] + df2['TotalAspirateTime'] + df2['TotalPickupTime'] + df2['TotalEjectTime'] + df2['TotalUserTime']

    df2['% Dispense'] =df2['TotalDispenseTime'] / df2['Total Time Seconds'] * 100
    df2['% Aspirate'] =df2['TotalAspirateTime'] / df2['Total Time Seconds'] * 100
    df2['% Pickup'] =df2['TotalPickupTime'] / df2['Total Time Seconds'] * 100
    df2['% Eject'] = df2['TotalEjectTime'] / df2['Total Time Seconds'] * 100
    df2['% User'] = df2['TotalUserTime'] / df2['Total Time Seconds'] * 100

    df2['Average Total Time (sec)'] = df2['Average'].apply(lambda x: formatter_number_one_dec(x))
    df2['% Dispense'] = df2['% Dispense'].apply(lambda x: formatter_number_one_dec(x))
    df2['% Aspirate'] = df2['% Aspirate'].apply(lambda x: formatter_number_one_dec(x))
    df2['% Pickup'] = df2['% Pickup'].apply(lambda x: formatter_number_one_dec(x))
    df2['% Eject'] = df2['% Eject'].apply(lambda x: formatter_number_one_dec(x))
    df2['% User'] = df2['% User'].apply(lambda x: formatter_number_one_dec(x))

    df2.sort_values(by=['Average Total Time (sec)'],inplace=True)

    tooltip_data = [
                       {
                           column: {'value': str(value), 'type': 'markdown'}
                           for column, value in row.items()
                       } for row in df2.to_dict('rows')
                   ]
    return df2.to_dict('records'), tooltip_data

# First Data Table Download Function
def update_first_download(start_date, end_date, serial_number):
    df1 = df.loc[(df['Serial Number'] == serial_number) & (df['Time Start'] >= start_date) & (df['Time End'] <= end_date)]
    data_df = df1.to_dict("record")
    return data_df


# Second Data Table Update Function
def update_second_datatable(start_date, end_date,serial_number):
    df1 = df.loc[
        (df['Serial Number'] == serial_number) & (df['Time Start'] >= start_date) & (df['Time End'] <= end_date)]
    data_df = df1.to_dict("record")
    return data_df


######################## FOR GRAPHS  ########################

def update_graph(filtered_df):

    # Sessions Graphs
    bar_graph = go.Bar(
        x=filtered_df[(filtered_df['Method Name'])],
        y=filtered_df[(filtered_df['Duration'])],
        text='Duration per Method'
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
