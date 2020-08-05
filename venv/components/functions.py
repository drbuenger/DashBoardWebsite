from datetime import datetime as dt
from datetime import date, timedelta
from datetime import datetime
import plotly.graph_objs as go
import plotly.express as px
from plotly import tools
import numpy as np
import pandas as pd
import csv
import os
import pyodbc
import time

pd.options.mode.chained_assignment = None

# Read in Hamilton Data
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

unique_serial_numbers = df['Serial Number'].unique()

#Read in BarTender data
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=labels-internal\BARTENDER;"
                      "Database=BarTender_UNREG;"
                      "Trusted_Connection=yes;")

bt_df = pd.read_sql_query('SELECT btff.Name , p.Name as PrinterName, btp.TotalLabels, btp.CreatedDateTime FROM BtPrintJobs btp \
inner join BtFormatFileNames btff on btp.FormatFileNameID = btff.FileNameID \
inner join Printers p on btp.FormatID = p.PrinterID', cnxn)
bt_df['CreatedDateTime']= bt_df['CreatedDateTime'] - 621355968000000000
bt_df['CreatedDateTime']= bt_df['CreatedDateTime']/10
bt_df['CreatedDateTime'] = pd.to_datetime(bt_df['CreatedDateTime'],unit='us')
bt_df['Server'] = 'Internal'

cnxn_controlled = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=lbl-controlled\BARTENDER_REG;"
                      "Database=BarTender_REG;"
                      "Trusted_Connection=yes;")

bt_df_controlled = pd.read_sql_query('SELECT btff.Name, p.Name as PrinterName, btp.TotalLabels, btp.CreatedDateTime \
FROM [BarTender_REG].[dbo].[BtPrintJobs] btp \
inner join [BarTender_REG].[dbo].BtFormatFileNames btff on btp.FormatFileNameID = btff.FileNameID \
inner join [BarTender_REG].[dbo].[Printers] p on btp.PrinterID = p.PrinterID', cnxn_controlled)
bt_df_controlled['CreatedDateTime']= bt_df_controlled['CreatedDateTime'] - 621355968000000000
bt_df_controlled['CreatedDateTime']= bt_df_controlled['CreatedDateTime']/10
bt_df_controlled['CreatedDateTime'] = pd.to_datetime(bt_df_controlled['CreatedDateTime'],unit='us')
bt_df_controlled['Server'] = 'Controlled'

bt_df = bt_df.append(bt_df_controlled)
bartender_summary = ['PrinterName', 'Name', 'TotalLabels', 'CreatedDateTime']
bartender_summary2 =  ['PrinterName', 'Name', 'TotalLabels', 'CreatedDateTime']
bartender_table = ['PrinterName', 'Name', 'TotalLabels', 'CreatedDateTime']

def get_es_data(start_date, end_date):
    es_data_location = 'C:\\Users\\Dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\data\\ES'
    new_df = pd.DataFrame(columns=['Stretcher','CreatedDateTime','File Path','t(s)','L1 Voltage(v)','L1 Current(uA)',
                                            'L2 Voltage(v)','L2 Current(uA)',
                      'L3 Voltage(v)','L3 Current(uA)',
                      'L4 Voltage(v)','L4 Current(uA)',
                                    'L5 Voltage(v)', 'L5 Current(uA)',
                                    'L6 Voltage(v)', 'L6 Current(uA)'])
    es_data_gather = [new_df]
    for r,d,f in os.walk(es_data_location):
        for filename in f:
            fullpath = os.path.join(os.path.abspath(r), filename)
            modified_time = os.path.getmtime(fullpath)
            z_date = dt.fromtimestamp(modified_time)
            if str(z_date) > start_date and str(z_date) < end_date:
                try:
                    nm,ext = os.path.splitext(filename)
                    if ext.lower().endswith('.csv'):

                        es_temp_df = pd.read_csv(fullpath)
                        if es_temp_df.empty == False:
                            if es_temp_df.at[0,'t(s)']==5:
                                fullpath_split =fullpath.split('\\')
                                list_length =len(fullpath_split)
                                z_stretcher = fullpath_split[list_length-2]
                                es_average_df = es_temp_df.mean()
                                df_temp = pd.DataFrame(data=es_average_df)
                                df_temp2 = df_temp.T
                                df_temp2['Stretcher'] = z_stretcher
                                df_temp2['CreatedDateTime'] = z_date
                                df_temp2['File Path'] = fullpath
                                es_data_gather.append(df_temp2)
                except pd.errors.EmptyDataError:
                    print("Found empty file: {file}".format(file=filename))
    new_df_list = [new_df]
    if len(es_data_gather) == 1:
        return new_df
    else:
        es_df = pd.concat(es_data_gather)
        es_df.dropna(axis=1,inplace=True,how='all')
        es_df['CreatedDateTime'] = pd.to_datetime(es_df['CreatedDateTime'])
        es_df.columns = es_df.columns.str.strip()
    return es_df

stretcher_summary = ['Stretcher', 'Lane 1 (uA)', 'Lane 1 (V)', 'Lane 2 (uA)', 'Lane 2 (V)', 'Lane 3 (uA)', 'Lane 3 (V)', 'Lane 4 (uA)', 'Lane 4 (V)', 'Lane 5 (uA)', 'Lane 5 (V)', 'Lane 6 (uA)', 'Lane 6 (V)']
stretcher_table = ['Stretcher', 'Lane 1 (uA)', 'Lane 1 (V)', 'Lane 2 (uA)', 'Lane 2 (V)', 'Lane 3 (uA)', 'Lane 3 (V)', 'Lane 4 (uA)', 'Lane 4 (V)', 'Lane 5 (uA)', 'Lane 5 (V)', 'Lane 6 (uA)', 'Lane 6 (V)', 'CreatedDateTime']

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
    file_name = ""

    if file is not None:
        f = open(file, 'r')
        file_name = f.name
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
                             user_time,
                             file_name
                             ])

# Read Text File
def read_trace_file_detail(file):
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
    file_name = ""
    df_detail= pd.DataFrame(columns=['Time Since Start (sec)','Step Type', 'Message'])
    tip_total = 0
    if file is not None:
        f = open(file, 'r')
        file_name = f.name
        for readline in f:
            if 'Analyze method - start' in readline:
                array_read_line = readline.split("\\")
                length = len(array_read_line)
                method_name = array_read_line[length-1].rstrip("'.hsl\n\t’")
            if 'Analyze method - start' in readline:
                date_start = readline[0:19]
                time_start = readline[11:19]
                time_since_start = '0'
                s= pd.Series([time_since_start,"Method Start", date_start],index=['Time Since Start (sec)','Step Type', 'Message'])
                df_detail = df_detail.append(s,ignore_index=True)
            if 'User name' in readline:
                array_read_line = readline.split(" ")
                length = len(array_read_line)
                username = array_read_line[length-1].rstrip("'\n\t’")
            if 'Serial number of Instrument' in readline:
                array_read_line = readline.split(" ")
                length = len(array_read_line)
                serialnumber= array_read_line[length - 1].rstrip("'\n\t’")
                read_event_time = readline[11:19]
                time_since_start = (dt.strptime(read_event_time, '%H:%M:%S') - dt.strptime(time_start, '%H:%M:%S')).seconds
                s= pd.Series([time_since_start,"Method Start", 'Serial Number: ' + serialnumber],index=['Time Since Start (sec)','Step Type', 'Message'])
                df_detail = df_detail.append(s,ignore_index=True)
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
                read_event_time = readline[11:19]
                time_since_start = (dt.strptime(read_event_time, '%H:%M:%S') - dt.strptime(time_start, '%H:%M:%S')).seconds
                s= pd.Series([time_since_start,"Method Aborted", "Aborted By User"],index=['Time Since Start (sec)','Step Type', 'Message'])
                df_detail = df_detail.append(s,ignore_index=True)
            if 'Aspirate (Single Step) - start' in readline:
                aspirating_start = readline[11:19]
                read_event_time = readline[11:19]
            if 'Aspirate (Single Step) - complete' in readline:
                aspirating_end = readline[11:19]
                read_event_time = readline[11:19]
                readline_split = readline.split('uL')
                time_since_start = (dt.strptime(read_event_time, '%H:%M:%S') - dt.strptime(time_start, '%H:%M:%S')).seconds
                s= pd.Series([time_since_start,"Aspirate", "Ended"],index=['Time Since Start (sec)','Step Type', 'Message'])
                df_detail = df_detail.append(s,ignore_index=True)
            if aspirating_end != "" and aspirating_start != "":
                aspirating_count = aspirating_count + 1
                aspirating_time = aspirating_time + (dt.strptime(aspirating_end, '%H:%M:%S') - dt.strptime(aspirating_start, '%H:%M:%S')).seconds
                aspirating_start = ""
                aspirating_end = ""
            if 'Dispense (Single Step) - start' in readline:
                dispensing_start = readline[11:19]
                read_event_time = readline[11:19]
            if 'Dispense (Single Step) - complete' in readline:
                dispensing_end = readline[11:19]
                read_event_time = readline[11:19]
                time_since_start = (dt.strptime(read_event_time, '%H:%M:%S') - dt.strptime(time_start, '%H:%M:%S')).seconds
                s= pd.Series([time_since_start,"Dispense", 'Ended'],index=['Time Since Start (sec)','Step Type', 'Message'])
                df_detail = df_detail.append(s,ignore_index=True)
            if dispensing_end != "" and dispensing_start != "":
                dispensing_count = dispensing_count + 1
                dispensing_time = dispensing_time + (dt.strptime(dispensing_end, '%H:%M:%S') - dt.strptime(dispensing_start, '%H:%M:%S')).seconds
                dispensing_start = ""
                dispensing_end = ""
            if 'Tip Pick Up (Single Step) - start' in readline:
                pickup_start = readline[11:19]
                read_event_time = readline[11:19]
            if 'Tip Pick Up (Single Step) - complete' in readline:
                pickup_end = readline[11:19]
                read_event_time = readline[11:19]
                tip_total = tip_total
                time_since_start = (dt.strptime(read_event_time, '%H:%M:%S') - dt.strptime(time_start, '%H:%M:%S')).seconds
                s= pd.Series([time_since_start,"Pick Up Tips", 'Ended'],index=['Time Since Start (sec)','Step Type', 'Message'])
                df_detail = df_detail.append(s,ignore_index=True)
            if pickup_end != "" and pickup_start != "":
                pickup_count = pickup_count + 1
                pickup_time = pickup_time + (dt.strptime(pickup_end, '%H:%M:%S') - dt.strptime(pickup_start, '%H:%M:%S')).seconds
                pickup_start = ""
                pickup_end = ""
            if 'Tip Eject (Single Step) - start' in readline:
                eject_start = readline[11:19]
                read_event_time = readline[11:19]
            if 'Tip Eject (Single Step) - complete' in readline:
                eject_end = readline[11:19]
                read_event_time = readline[11:19]
                time_since_start = (dt.strptime(read_event_time, '%H:%M:%S') - dt.strptime(time_start, '%H:%M:%S')).seconds
                s= pd.Series([time_since_start,"Eject Tips", 'Total Tips Ejected: ' + str(tips_used1000uL)],index=['Time Since Start (sec)','Step Type', 'Message'])
                df_detail = df_detail.append(s,ignore_index=True)
            if eject_end != "" and eject_start != "":
                eject_count = eject_count + 1
                eject_time = eject_time + (dt.strptime(eject_end, '%H:%M:%S') - dt.strptime(eject_start, '%H:%M:%S')).seconds
                eject_start = ""
                eject_end = ""
            if 'Dialog - start' in readline:
                user_start = readline[11:19]
                read_event_time = readline[11:19]
                time_since_start = (dt.strptime(read_event_time, '%H:%M:%S') - dt.strptime(time_start, '%H:%M:%S')).seconds
                message = readline[57:]
                s= pd.Series([time_since_start,"User Step Start", message],index=['Time Since Start (sec)','Step Type', 'Message'])
                df_detail = df_detail.append(s,ignore_index=True)
            if 'Dialog - complete' in readline:
                user_end = readline[11:19]
                read_event_time = readline[11:19]
                time_since_start = (dt.strptime(read_event_time, '%H:%M:%S') - dt.strptime(time_start, '%H:%M:%S')).seconds
                message = readline[60:]
                s= pd.Series([time_since_start,"User Step Complete", message],index=['Time Since Start (sec)','Step Type', 'Message'])
                df_detail = df_detail.append(s,ignore_index=True)
            if 'HSLMapReport::GenerateMappingReport - progress' in readline:
                read_event_time = readline[11:19]
                time_since_start = (dt.strptime(read_event_time, '%H:%M:%S') - dt.strptime(time_start, '%H:%M:%S')).seconds
                message = readline[108:]
                s= pd.Series([time_since_start,"Generate Report", 'Report Mapping File: ' + message],index=['Time Since Start (sec)','Step Type', 'Message'])
                df_detail = df_detail.append(s,ignore_index=True)
            if 'Execute method - start;' in readline:
                read_event_time = readline[11:19]
                time_since_start = (dt.strptime(read_event_time, '%H:%M:%S') - dt.strptime(time_start, '%H:%M:%S')).seconds
                message = readline[66:]
                s= pd.Series([time_since_start,"Execute Method", 'Method File: ' + message],index=['Time Since Start (sec)','Step Type', 'Message'])
                df_detail = df_detail.append(s,ignore_index=True)
            if 'Initialize (Single Step) - complete;' in readline:
                read_event_time = readline[11:19]
                time_since_start = (dt.strptime(read_event_time, '%H:%M:%S') - dt.strptime(time_start, '%H:%M:%S')).seconds
                s= pd.Series([time_since_start,"Initialize Robot", 'Initialize Robot completed'],index=['Time Since Start (sec)','Step Type', 'Message'])
                df_detail = df_detail.append(s,ignore_index=True)
            if user_end != "" and user_start != "":
                user_count = user_count + 1
                user_time = user_time + (dt.strptime(user_end, '%H:%M:%S') - dt.strptime(user_start, '%H:%M:%S')).seconds
                user_start = ""
                user_end = ""
        f.close()
        return df_detail


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
    df2['Success %'] = df2['Success %'].apply(lambda x: formatter_number_one_dec(x))
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

    df2['Average Total Time (min)'] = df2['Average'].apply(lambda x: formatter_number_one_dec(x))
    df2['% Dispense'] = df2['% Dispense'].apply(lambda x: formatter_number_one_dec(x))
    df2['% Aspirate'] = df2['% Aspirate'].apply(lambda x: formatter_number_one_dec(x))
    df2['% Pickup'] = df2['% Pickup'].apply(lambda x: formatter_number_one_dec(x))
    df2['% Eject'] = df2['% Eject'].apply(lambda x: formatter_number_one_dec(x))
    df2['% User'] = df2['% User'].apply(lambda x: formatter_number_one_dec(x))

    df2.sort_values(by=['Average Total Time (min)'],inplace=True)

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

########################## BARTENDER ########################
def update_bartender_summary(start_date,end_date,server_list):
    df1 = bt_df.loc[(bt_df['CreatedDateTime'] >= start_date) & (bt_df['CreatedDateTime'] <= end_date)]
    df3 = df1[df1['Server'].isin(server_list)]
    df3['Print Time'] = df3['CreatedDateTime'].dt.strftime("%Y/%m/%d %H:%M:%S")

    df2 = df3.groupby('PrinterName').agg(
        Total=pd.NamedAgg(column='TotalLabels', aggfunc=np.sum),
        LastUsed=pd.NamedAgg(column='Print Time', aggfunc=np.max)).reset_index()

    df2.sort_values(by=['Total'], inplace=True, ascending=False)

    tooltip_data = [
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in df2.to_dict('rows')
    ]
    return df2.to_dict('records'), tooltip_data

def update_bartender_summary2(start_date,end_date,server_list):
    df1 = bt_df.loc[(bt_df['CreatedDateTime'] >= start_date) & (bt_df['CreatedDateTime'] <= end_date)]
    df3 = df1[df1['Server'].isin(server_list)]
    df3['Print Time'] = df3['CreatedDateTime'].dt.strftime("%Y/%m/%d %H:%M:%S")

    df2 = df3.groupby(['Name']).agg(
        Total=pd.NamedAgg(column='TotalLabels', aggfunc=np.sum),
        LastUsed=pd.NamedAgg(column='Print Time', aggfunc=np.max)).reset_index()

    df2.sort_values(by=['Total'], inplace=True, ascending=False)

    tooltip_data = [
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in df2.to_dict('rows')
    ]
    return df2.to_dict('records'), tooltip_data

def update_bartender_table(start_date, end_date, server_list):
    df1 = bt_df.loc[(bt_df['CreatedDateTime'] >= start_date) & (bt_df['CreatedDateTime'] <= end_date)]
    df3 = df1[df1['Server'].isin(server_list)]
    df3['Print Time'] = df3['CreatedDateTime'].dt.strftime("%Y/%m/%d %H:%M:%S")

    df3.sort_values(by=['Print Time'], inplace=True,ascending=False)

    tooltip_data = [
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in df3.to_dict('rows')
    ]
    return df3.to_dict('records'), tooltip_data


########################### BARTENDER ##########################

############################ELECTROSTRETCHER###################
# First Data Table Update Function
def update_datatable_stretcher(start_date, end_date, colors):
    es_df = get_es_data(start_date,end_date)
    if es_df.empty == False:
        df1 = es_df.loc[(es_df['CreatedDateTime'] >= start_date) & (es_df['CreatedDateTime'] <= end_date)]
        df1['Date and Time'] = df1['CreatedDateTime'].dt.strftime("%Y/%m/%d %H:%M:%S")
        df1 = df1[df1['Stretcher'].isin(colors)]
        df2 = df1.rename(columns={'L1 Current(uA)':'Lane 1 (uA)','L1 Voltage(v)':'Lane 1 (V)',
                        'L2 Current(uA)':'Lane 2 (uA)','L2 Voltage(v)':'Lane 2 (V)',
                        'L3 Current(uA)': 'Lane 3 (uA)', 'L3 Voltage(v)': 'Lane 3 (V)',
                        'L4 Current(uA)': 'Lane 4 (uA)', 'L4 Voltage(v)': 'Lane 4 (V)',
                        'L5 Current(uA)': 'Lane 5 (uA)', 'L5 Voltage(v)': 'Lane 5 (V)',
                        'L6 Current(uA)': 'Lane 6 (uA)', 'L6 Voltage(v)': 'Lane 6 (V)',
                        })

        df2['Lane 1 (uA)'] = df2['Lane 1 (uA)'].apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 1 (V)'] = df2['Lane 1 (V)'].apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 2 (uA)'] = df2['Lane 2 (uA)'].apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 2 (V)'] = df2['Lane 2 (V)'].apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 3 (uA)'] = df2['Lane 3 (uA)'].apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 3 (V)'] = df2['Lane 3 (V)'].apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 4 (uA)'] = df2['Lane 4 (uA)'].apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 4 (V)'] = df2['Lane 4 (V)'].apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 5 (uA)'] = df2['Lane 5 (uA)'].apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 5 (V)'] = df2['Lane 5 (V)'].apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 6 (uA)'] = df2['Lane 6 (uA)'].apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 6 (V)'] = df2['Lane 6 (V)'].apply(lambda x: formatter_number_one_dec(x))
        df2.sort_values(by=['Date and Time'], inplace=True, ascending=False)
        tooltip_data = [
                           {
                               column: {'value': str(value), 'type': 'markdown'}
                               for column, value in row.items()
                           } for row in df2.to_dict('rows')
                       ]
        return df2.to_dict('records'), tooltip_data
    else:
        return pd.DataFrame().to_dict('records') , []

# First Data Table Update Function
def update_summary_stretcher(start_date, end_date):
    es_df = get_es_data(start_date, end_date)
    if es_df.empty == False:

        df1 = es_df.loc[(es_df['CreatedDateTime'] >= start_date) & (es_df['CreatedDateTime'] <= end_date)]
        df1['Date and Time'] = df1['CreatedDateTime'].dt.strftime("%Y/%m/%d %H:%M:%S")

        df2 = df1.groupby('Stretcher').agg(
            Lane1uA=pd.NamedAgg(column='L1 Current(uA)', aggfunc='mean'),
            Lane1V = pd.NamedAgg(column='L1 Voltage(v)', aggfunc='mean'),
            Lane2uA=pd.NamedAgg(column='L2 Current(uA)', aggfunc='mean'),
            Lane2V=pd.NamedAgg(column='L2 Voltage(v)', aggfunc='mean'),
            Lane3uA=pd.NamedAgg(column='L3 Current(uA)', aggfunc='mean'),
            Lane3V=pd.NamedAgg(column='L3 Voltage(v)', aggfunc='mean'),
            Lane4uA=pd.NamedAgg(column='L4 Current(uA)', aggfunc='mean'),
            Lane4V=pd.NamedAgg(column='L4 Voltage(v)', aggfunc='mean'),
            Lane5uA=pd.NamedAgg(column='L5 Current(uA)', aggfunc='mean'),
            Lane5V=pd.NamedAgg(column='L5 Voltage(v)', aggfunc='mean'),
            Lane6uA=pd.NamedAgg(column='L6 Current(uA)', aggfunc='mean'),
            Lane6V=pd.NamedAgg(column='L6 Voltage(v)', aggfunc='mean'),
            Total=pd.NamedAgg(column='L6 Voltage(v)', aggfunc='count'),
                                   ).reset_index()
        df2['Lane 1 (uA)'] = df2.Lane1uA.apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 1 (V)'] = df2.Lane1V.apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 2 (uA)'] = df2.Lane2uA.apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 2 (V)'] = df2.Lane2V.apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 3 (uA)'] = df2.Lane3uA.apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 3 (V)'] = df2.Lane3V.apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 4 (uA)'] = df2.Lane4uA.apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 4 (V)'] = df2.Lane4V.apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 5 (uA)'] = df2.Lane5uA.apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 5 (V)'] = df2.Lane5V.apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 6 (uA)'] = df2.Lane6uA.apply(lambda x: formatter_number_one_dec(x))
        df2['Lane 6 (V)'] = df2.Lane6V.apply(lambda x: formatter_number_one_dec(x))
        df2.sort_values(by=['Total'],inplace=True, ascending=False)
        df2 = df2.drop(columns=['Lane1uA','Lane2uA','Lane3uA','Lane4uA','Lane5uA','Lane6uA','Lane1V','Lane2V','Lane3V','Lane4V','Lane5V','Lane6V'])

        tooltip_data = [
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in df2.to_dict('rows')
        ]
        return df2.to_dict('records'), tooltip_data
    else:
        return pd.DataFrame().to_dict('records') , []
########################ELECTROSTRETCHER########################

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

def es_graph(es_filtered_df):
    if es_filtered_df.empty == False:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=es_filtered_df['t(s)'], y=es_filtered_df['L1 Current(uA)'], name='Lane 1', line=dict(color='firebrick', width=2)))
        fig.add_trace(go.Scatter(x=es_filtered_df['t(s)'], y=es_filtered_df['L2 Current(uA)'], name='Lane 2', line=dict(color='royalblue', width=2)))
        fig.add_trace(go.Scatter(x=es_filtered_df['t(s)'], y=es_filtered_df['L3 Current(uA)'], name='Lane 3', line=dict(color='green', width=2)))
        fig.add_trace(go.Scatter(x=es_filtered_df['t(s)'], y=es_filtered_df['L4 Current(uA)'], name='Lane 4', line=dict(color='orange', width=2)))
        fig.add_trace(go.Scatter(x=es_filtered_df['t(s)'], y=es_filtered_df['L5 Current(uA)'], name='Lane 5', line=dict(color='pink', width=2)))
        fig.add_trace(go.Scatter(x=es_filtered_df['t(s)'], y=es_filtered_df['L6 Current(uA)'], name='Lane 6', line=dict(color='grey', width=2)))
        fig.update_layout(title=go.layout.Title(text="Amperage throughout run by Lane"),xaxis_title="Time (s)",yaxis_title="Amps (uA)")

    else:
        fig = px.line()
    return fig

