import dash_core_components as dcc
import dash_html_components as html
import dash_table
from components import (Header, print_button)
from datetime import datetime as dt
from datetime import date, timedelta
import pandas as pd

# Read in Travel Report Data
df = pd.read_csv('data/performance_analytics_cost_and_ga_metrics.csv')

df.rename(columns={
    'Travel Product': 'Placement type',
    'Spend - This Year': 'Spend TY',
    'Spend - Last Year': 'Spend LY',
    'Sessions - This Year': 'Sessions - TY',
    'Sessions - Last Year': 'Sessions - LY',
    'Bookings - This Year': 'Bookings - TY',
    'Bookings - Last Year': 'Bookings - LY',
    'Revenue - This Year': 'Revenue - TY',
    'Revenue - Last Year': 'Revenue - LY',
}, inplace=True)

df['Date'] = pd.to_datetime(df['Date'])
current_year = df['Year'].max()

dt_columns = ['Placement type', 'Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY',
              'Spend YoY (%)', \
              'Sessions - TY', 'Sessions - LP', 'Sessions - LY', 'Sessions PoP (%)', 'Sessions YoY (%)', \
              'Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)', 'Bookings PoP (Abs)', 'Bookings - LY',
              'Bookings YoY (%)', 'Bookings YoY (Abs)', \
              'Revenue - TY', 'Revenue - LP', 'Revenue PoP (Abs)', 'Revenue PoP (%)', 'Revenue - LY', 'Revenue YoY (%)',
              'Revenue YoY (Abs)', ]

conditional_columns = ['Spend_PoP_abs_conditional', 'Spend_PoP_percent_conditional', 'Spend_YoY_percent_conditional',
                       'Sessions_PoP_percent_conditional', 'Sessions_YoY_percent_conditional',
                       'Bookings_PoP_abs_conditional', 'Bookings_YoY_abs_conditional',
                       'Bookings_PoP_percent_conditional', 'Bookings_YoY_percent_conditional',
                       'Revenue_PoP_abs_conditional', 'Revenue_YoY_abs_conditional', 'Revenue_PoP_percent_conditional',
                       'Revenue_YoY_percent_conditional', ]

dt_columns_total = ['Placement type', 'Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY',
                    'Spend YoY (%)', \
                    'Sessions - TY', 'Sessions - LP', 'Sessions - LY', 'Sessions PoP (%)', 'Sessions YoY (%)', \
                    'Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)', 'Bookings PoP (Abs)', 'Bookings - LY',
                    'Bookings YoY (%)', 'Bookings YoY (Abs)', \
                    'Revenue - TY', 'Revenue - LP', 'Revenue PoP (Abs)', 'Revenue PoP (%)', 'Revenue - LY',
                    'Revenue YoY (%)', 'Revenue YoY (Abs)',
                    'Spend_PoP_abs_conditional', 'Spend_PoP_percent_conditional', 'Spend_YoY_percent_conditional',
                    'Sessions_PoP_percent_conditional', 'Sessions_YoY_percent_conditional',
                    'Bookings_PoP_abs_conditional', 'Bookings_YoY_abs_conditional', 'Bookings_PoP_percent_conditional',
                    'Bookings_YoY_percent_conditional',
                    'Revenue_PoP_abs_conditional', 'Revenue_YoY_abs_conditional', 'Revenue_PoP_percent_conditional',
                    'Revenue_YoY_percent_conditional', ]

df_columns_calculated = ['Placement type', 'CPS - TY',
                         'CPS - LP', 'CPS PoP (Abs)', 'CPS PoP (%)',
                         'CPS - LY', 'CPS YoY (Abs)', 'CPS YoY (%)',
                         'CVR - TY',
                         'CVR - LP', 'CVR PoP (Abs)', 'CVR PoP (%)',
                         'CVR - LY', 'CVR YoY (Abs)', 'CVR YoY (%)',
                         'CPA - TY',
                         'CPA - LP', 'CPA PoP (Abs)', 'CPA PoP (%)',
                         'CPA - LY', 'CPA YoY (Abs)', 'CPA YoY (%)']

conditional_columns_calculated_calculated = ['CPS_PoP_abs_conditional', 'CPS_PoP_percent_conditional',
                                             'CPS_YoY_abs_conditional', 'CPS_PoP_percent_conditional',
                                             'CVR_PoP_abs_conditional', 'CVR_PoP_percent_conditional',
                                             'CVR_YoY_abs_conditional', 'CVR_YoY_percent_conditional',
                                             'CPA_PoP_abs_conditional', 'CPA_PoP_percent_conditional',
                                             'CPA_YoY_abs_conditional', 'CPA_YoY_percent_conditional']

######################## START Hamilton Category Layout ########################
layout_hamilton = html.Div([

    #    print_button(),

    html.Div([
        # CC Header
        Header(),
        # Date Picker
        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range-birst-category',
                # with_portal=True,
                min_date_allowed=dt(2018, 1, 1),
                max_date_allowed=df['Date'].max().to_pydatetime(),
                initial_visible_month=dt(current_year, df['Date'].max().to_pydatetime().month, 1),
                start_date=(df['Date'].max() - timedelta(6)).to_pydatetime(),
                end_date=df['Date'].max().to_pydatetime(),
            ),
            html.Div(id='output-container-date-picker-range-birst-category')
        ], className="row ", style={'marginTop': 30, 'marginBottom': 15}),
        # Header Bar
        html.Div([
            html.H6(["Nanostring Level Metrics"], className="gs-header gs-text-header padded", style={'marginTop': 15})
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
                id='radio-button-birst-category'
            )]),
        # First Data Table
        html.Div([
            dash_table.DataTable(
                id='datatable-birst-category',
                columns=[{"name": i, "id": i, 'deletable': True} for i in dt_columns],
                editable=True,
                fixed_columns=2,
                style_table={'maxWidth': '1500px'},
                row_selectable="multi",
                selected_rows=[0],
                style_cell={"fontFamily": "Arial", "size": 10, 'textAlign': 'left'},
                css=[{'selector': '.dash-cell div.dash-cell-value',
                      'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'}],
                style_cell_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#D5DBDB'}]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#EAFAF1'} for c in
                                          ['Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY',
                                           'Spend YoY (%)', ]]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#D5F5E3'} for
                                          c in
                                          ['Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY',
                                           'Spend YoY (%)', ]]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#FEF9E7'} for c in
                                          ['Sessions - TY', 'Sessions - LP', 'Sessions - LY', 'Sessions PoP (%)',
                                           'Sessions YoY (%)', ]]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#FCF3CF'} for
                                          c in ['Sessions - TY', 'Sessions - LP', 'Sessions - LY', 'Sessions PoP (%)',
                                                'Sessions YoY (%)', ]]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#EBF5FB'} for c in
                                          ['Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)', 'Bookings PoP (Abs)',
                                           'Bookings - LY', 'Bookings YoY (%)', 'Bookings YoY (Abs)', ]]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#D6EAF8'} for
                                          c in
                                          ['Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)', 'Bookings PoP (Abs)',
                                           'Bookings - LY', 'Bookings YoY (%)', 'Bookings YoY (Abs)', ]]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#F4ECF7'} for c in
                                          ['CVR - TY', 'CVR - LP', 'CVR PoP (Abs)', 'CVR - LY', 'CVR YoY (Abs)',
                                           'CVR PoP (%)', 'CVR YoY (%)']]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#E8DAEF'} for
                                          c in ['CVR - TY', 'CVR - LP', 'CVR PoP (Abs)', 'CVR - LY', 'CVR YoY (Abs)',
                                                'CVR PoP (%)', 'CVR YoY (%)']]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#FDEDEC'} for c in
                                          ['CPA - TY', 'CPA - LP', 'CPA PoP (Abs)', 'CPA - LY', 'CPA YoY (Abs)',
                                           'CPA PoP (%)', 'CPA YoY (%)']]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#FADBD8'} for
                                          c in ['CPA - TY', 'CPA - LP', 'CPA PoP (Abs)', 'CPA - LY', 'CPA YoY (Abs)',
                                                'CPA PoP (%)', 'CPA YoY (%)']]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#F6DDCC'} for c in
                                          ['CPS - TY', 'CPS - LP', 'CPS PoP (Abs)', 'CPS - LY', 'CPS YoY (Abs)',
                                           'CPS PoP (%)', 'CPA YoY (%)']]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#E59866'} for
                                          c in ['CPS - TY', 'CPS - LP', 'CPS PoP (Abs)', 'CPS - LY', 'CPS YoY (Abs)',
                                                'CPS PoP (%)', 'CPA YoY (%)']]
                                       + [{'if': {'column_id': c}, 'minWidth': '0px', 'maxWidth': '80px',
                                           'whiteSpace': 'normal'} for c in
                                          ['Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY',
                                           'Spend YoY (%)', 'Sessions - TY', 'Sessions - LP', 'Sessions - LY',
                                           'Sessions PoP (%)',
                                           'Sessions YoY (%)', 'Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)',
                                           'Bookings PoP (Abs)', 'Bookings - LY', 'Bookings YoY (%)',
                                           'Bookings YoY (Abs)', 'Revenue - TY', 'Revenue - LP', 'Revenue PoP (Abs)',
                                           'Revenue PoP (%)', 'Revenue - LY', 'Revenue YoY (%)', 'Revenue YoY (Abs)', ]]
            ),
        ], className=" twelve columns"),
        # Download Button
        html.Div([
            html.A(html.Button('Download Data', id='download-button'), id='download-link-birst-category')
        ]),
        # Second Data Table
        html.Div([
            dash_table.DataTable(
                id='datatable-birst-category-2',
                columns=[{"name": i, "id": i} for i in df_columns_calculated],
                editable=True,
                fixed_columns=1,
                style_table={'maxWidth': '1500px'},
                # sorting=True,
                # sorting_type="multi",
                style_cell={"fontFamily": "Arial", "size": 10, 'textAlign': 'left'},
                style_cell_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#D5DBDB'}]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#F4ECF7'} for c in
                                          ['CVR - TY', 'CVR - LP', 'CVR PoP (Abs)', 'CVR - LY', 'CVR YoY (Abs)',
                                           'CVR PoP (%)', 'CVR YoY (%)']]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#E8DAEF'} for
                                          c in ['CVR - TY', 'CVR - LP', 'CVR PoP (Abs)', 'CVR - LY', 'CVR YoY (Abs)',
                                                'CVR PoP (%)', 'CVR YoY (%)']]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#FDEDEC'} for c in
                                          ['CPA - TY', 'CPA - LP', 'CPA PoP (Abs)', 'CPA - LY', 'CPA YoY (Abs)',
                                           'CPA PoP (%)', 'CPA YoY (%)']]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#FADBD8'} for
                                          c in ['CPA - TY', 'CPA - LP', 'CPA PoP (Abs)', 'CPA - LY', 'CPA YoY (Abs)',
                                                'CPA PoP (%)', 'CPA YoY (%)']]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#F6DDCC'} for c in
                                          ['CPS - TY', 'CPS - LP', 'CPS PoP (Abs)', 'CPS - LY', 'CPS YoY (Abs)',
                                           'CPS PoP (%)', 'CPS YoY (%)', ]]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#E59866'} for
                                          c in ['CPS - TY', 'CPS - LP', 'CPS PoP (Abs)', 'CPS - LY', 'CPS YoY (Abs)',
                                                'CPS PoP (%)', 'CPS YoY (%)', ]]
                                       + [{'if': {'column_id': c}, 'minWidth': '0px', 'maxWidth': '80px',
                                           'whiteSpace': 'normal'} for c in
                                          ['CPS - TY', 'CPS - LP', 'CPS PoP (Abs)', 'CPS - LY', 'CPS YoY (Abs)',
                                           'CPS PoP (%)', 'CPS YoY (%)', 'CVR - TY', 'CVR - LP', 'CVR PoP (Abs)',
                                           'CVR - LY', 'CVR YoY (Abs)', 'CVR PoP (%)', 'CVR YoY (%)', 'CPA - TY',
                                           'CPA - LP', 'CPA PoP (Abs)', 'CPA - LY', 'CPA YoY (Abs)', 'CPA PoP (%)',
                                           'CPA YoY (%)']],
            ),
        ], className=" twelve columns"),
        # GRAPHS
        html.Div([
            html.Div(
                id='update_graph_1'
            ),
            html.Div([
                dcc.Graph(id='birst-category'),
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
                max_date_allowed=df['Date'].max().to_pydatetime(),
                initial_visible_month=dt(current_year, df['Date'].max().to_pydatetime().month, 1),
                start_date=(df['Date'].max() - timedelta(6)).to_pydatetime(),
                end_date=df['Date'].max().to_pydatetime(),
            ),
            html.Div(id='output-container-date-picker-range-ga-category')
        ], className="row ", style={'marginTop': 30, 'marginBottom': 15}),
        # Header Bar
        html.Div([
            html.H6(["GA Level Metrics"], className="gs-header gs-text-header padded", style={'marginTop': 15})
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
                id='radio-button-ga-category'
            )]),
        # First Data Table
        html.Div([
            dash_table.DataTable(
                id='datatable-ga-category',
                columns=[{"name": i, "id": i, 'deletable': True} for i in dt_columns],
                editable=True,
                style_table={'maxWidth': '1500px'},
                row_selectable="multi",
                selected_rows=[0],
                style_cell={"fontFamily": "Arial", "size": 10, 'textAlign': 'left'},
                css=[{'selector': '.dash-cell div.dash-cell-value',
                      'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'}],
                style_cell_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#D5DBDB'}]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#EAFAF1'} for c in
                                          ['Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY',
                                           'Spend YoY (%)', ]]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#D5F5E3'} for
                                          c in
                                          ['Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY',
                                           'Spend YoY (%)', ]]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#FEF9E7'} for c in
                                          ['Sessions - TY', 'Sessions - LP', 'Sessions - LY', 'Sessions PoP (%)',
                                           'Sessions YoY (%)', ]]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#FCF3CF'} for
                                          c in ['Sessions - TY', 'Sessions - LP', 'Sessions - LY', 'Sessions PoP (%)',
                                                'Sessions YoY (%)', ]]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#EBF5FB'} for c in
                                          ['Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)', 'Bookings PoP (Abs)',
                                           'Bookings - LY', 'Bookings YoY (%)', 'Bookings YoY (Abs)', ]]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#D6EAF8'} for
                                          c in
                                          ['Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)', 'Bookings PoP (Abs)',
                                           'Bookings - LY', 'Bookings YoY (%)', 'Bookings YoY (Abs)', ]]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#F4ECF7'} for c in
                                          ['CVR - TY', 'CVR - LP', 'CVR PoP (Abs)', 'CVR - LY', 'CVR YoY (Abs)',
                                           'CVR PoP (%)', 'CVR YoY (%)']]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#E8DAEF'} for
                                          c in ['CVR - TY', 'CVR - LP', 'CVR PoP (Abs)', 'CVR - LY', 'CVR YoY (Abs)',
                                                'CVR PoP (%)', 'CVR YoY (%)']]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#FDEDEC'} for c in
                                          ['CPA - TY', 'CPA - LP', 'CPA PoP (Abs)', 'CPA - LY', 'CPA YoY (Abs)',
                                           'CPA PoP (%)', 'CPA YoY (%)']]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#FADBD8'} for
                                          c in ['CPA - TY', 'CPA - LP', 'CPA PoP (Abs)', 'CPA - LY', 'CPA YoY (Abs)',
                                                'CPA PoP (%)', 'CPA YoY (%)']]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#F6DDCC'} for c in
                                          ['CPS - TY', 'CPS - LP', 'CPS PoP (Abs)', 'CPS - LY', 'CPS YoY (Abs)',
                                           'CPS PoP (%)', 'CPA YoY (%)']]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#E59866'} for
                                          c in ['CPS - TY', 'CPS - LP', 'CPS PoP (Abs)', 'CPS - LY', 'CPS YoY (Abs)',
                                                'CPS PoP (%)', 'CPA YoY (%)']]
                                       + [{'if': {'column_id': c}, 'minWidth': '0px', 'maxWidth': '80px',
                                           'whiteSpace': 'normal'} for c in
                                          ['Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY',
                                           'Spend YoY (%)', 'Sessions - TY', 'Sessions - LP', 'Sessions - LY',
                                           'Sessions PoP (%)',
                                           'Sessions YoY (%)', 'Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)',
                                           'Bookings PoP (Abs)', 'Bookings - LY', 'Bookings YoY (%)',
                                           'Bookings YoY (Abs)', 'Revenue - TY', 'Revenue - LP', 'Revenue PoP (Abs)',
                                           'Revenue PoP (%)', 'Revenue - LY', 'Revenue YoY (%)',
                                           'Revenue YoY (Abs)', ]],
            ),
        ], className=" twelve columns"),
        # Download Button
        html.Div([
            html.A(html.Button('Download Data', id='download-button'), id='download-link-ga-category')
        ]),
        # Second Data Table
        html.Div([
            dash_table.DataTable(
                id='datatable-ga-category-2',
                columns=[{"name": i, "id": i} for i in df_columns_calculated],
                editable=True,
                style_table={'maxWidth': '1500px'},
                # sorting=True,
                # sorting_type="multi",
                style_cell={"fontFamily": "Arial", "size": 10, 'textAlign': 'left'},
                style_cell_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#D5DBDB'}]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#F4ECF7'} for c in
                                          ['CVR - TY', 'CVR - LP', 'CVR PoP (Abs)', 'CVR - LY', 'CVR YoY (Abs)',
                                           'CVR PoP (%)', 'CVR YoY (%)']]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#E8DAEF'} for
                                          c in ['CVR - TY', 'CVR - LP', 'CVR PoP (Abs)', 'CVR - LY', 'CVR YoY (Abs)',
                                                'CVR PoP (%)', 'CVR YoY (%)']]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#FDEDEC'} for c in
                                          ['CPA - TY', 'CPA - LP', 'CPA PoP (Abs)', 'CPA - LY', 'CPA YoY (Abs)',
                                           'CPA PoP (%)', 'CPA YoY (%)']]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#FADBD8'} for
                                          c in ['CPA - TY', 'CPA - LP', 'CPA PoP (Abs)', 'CPA - LY', 'CPA YoY (Abs)',
                                                'CPA PoP (%)', 'CPA YoY (%)']]
                                       + [{'if': {'column_id': c}, 'backgroundColor': '#F6DDCC'} for c in
                                          ['CPS - TY', 'CPS - LP', 'CPS PoP (Abs)', 'CPS - LY', 'CPS YoY (Abs)',
                                           'CPS PoP (%)', 'CPS YoY (%)', ]]
                                       + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#E59866'} for
                                          c in ['CPS - TY', 'CPS - LP', 'CPS PoP (Abs)', 'CPS - LY', 'CPS YoY (Abs)',
                                                'CPS PoP (%)', 'CPS YoY (%)', ]]
                                       + [{'if': {'column_id': c}, 'minWidth': '0px', 'maxWidth': '80px',
                                           'whiteSpace': 'normal'} for c in
                                          ['CPS - TY', 'CPS - LP', 'CPS PoP (Abs)', 'CPS - LY', 'CPS YoY (Abs)',
                                           'CPS PoP (%)', 'CPS YoY (%)', 'CVR - TY', 'CVR - LP', 'CVR PoP (Abs)',
                                           'CVR - LY', 'CVR YoY (Abs)', 'CVR PoP (%)', 'CVR YoY (%)', 'CPA - TY',
                                           'CPA - LP', 'CPA PoP (Abs)', 'CPA - LY', 'CPA YoY (Abs)', 'CPA PoP (%)',
                                           'CPA YoY (%)']],
            ),
        ], className=" twelve columns"),
        # GRAPHS
        html.Div([
            html.Div(
                id='update_graph_1'
            ),
            html.Div([
                dcc.Graph(id='ga-category'),
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