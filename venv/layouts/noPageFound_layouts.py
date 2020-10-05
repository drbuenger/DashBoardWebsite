import dash_html_components as html
from components import Header

######################## 404 Page ########################

######################## 404 Page ########################
noPage = html.Div([
    # CC Header
    Header(),
    html.P(["404 Page not found"])
], className="no-page")
