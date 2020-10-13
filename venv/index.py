import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

# see https://community.plot.ly/t/nolayoutexception-on-deployment-of-multi-page-dash-app-example-code/12463/2?u=dcomfort
from app import server
from app import app
from layouts.hamilton_layouts import layout_hamilton, layout_hamilton_time, layout_hamilton_tips, layout_hamilton_dashboard
from layouts.noPageFound_layouts import noPage
from layouts.dx_codes_layouts import layout_duplicate_test_codes
from layouts.bartender_layouts import layout_BarTender
from layouts.electrostretcher_layouts import layout_stretcher
from layouts.inventory_layouts import layout_Inventory
import callbacks

# see https://dash.plot.ly/external-resources to alter header, footer and favicon
app.index_string = ''' 
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Nanostring Reports</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <div>Nanostring Reports</div>
    </body>
</html>
'''

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Update page
# # # # # # # # #
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/Reports/Hamilton/Methods/':
        return layout_hamilton
    elif pathname == '/Reports/Hamilton/TimeStudy/':
        return layout_hamilton_time
    elif pathname == '/Reports/Hamilton/Tips/':
        return layout_hamilton_tips
    elif pathname == '/Reports/Hamilton/Dashboard/':
        return layout_hamilton_dashboard
    elif pathname == '/Reports/BarTender/PrintJobs/':
        return layout_BarTender
    elif pathname == '/Reports/Electrostretcher/RunHistory/':
        return layout_stretcher
    elif pathname == '/Reports/DXTestCodes/Duplicates/':
        return layout_duplicate_test_codes
    elif pathname == '/Reports/Inventory/Main/':
        return layout_Inventory
    else:
        return noPage

# # # # # # # # #

#
# for css in external_css:
#     app.css.append_css({"external_url": css})
#
# external_js = ["https://code.jquery.com/jquery-3.2.1.min.js",
#                "https://codepen.io/bcd/pen/YaXojL.js"]
#
# for js in external_js:
#     app.scripts.append_script({"external_url": js})

if __name__ == '__main__':
    app.run_server(debug=True)