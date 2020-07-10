import dash_html_components as html
import dash_core_components as dcc
import base64

import dash_bootstrap_components as dbc

image_filename = 'C:\\Users\\Dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\assets\\NanostringLogo.jpg' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

def Header(navSelector):
    return html.Div([
        get_header(),
        get_logo(),
        html.Br([]),
        get_menu(navSelector)
    ])

def get_logo():
    logo = html.Div([
            html.Img(src='data:image/jpg;base64,{}'.format(encoded_image.decode())),

        ],
        style={'marginTop': 0, 'marginBottom': 0, 'marginLeft': -25})
    return logo

def get_header():
    header = html.Div([

        html.Div([
            html.H3(
                'Nanostring MFG Reports'
            )
        ], className="twelve columns padded", style={'marginTop': 0, 'marginBottom': 0, 'marginLeft': 15} )

    ], className="row gs-header gs-text-header" )
    return header

def get_menu(navSelector):
    bitmask = list(navSelector)
    array_of_bools = []
    count = 0
    for char in bitmask:
        if char == '1':
            array_of_bools.append(True)
        else:
            array_of_bools.append(False)
        count += 1

    nav = dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink("Home", href='/Reports/Hamilton/',active=array_of_bools[0])),
            dbc.NavItem(dbc.NavLink("Time Study",href='/Reports/HamiltonTime/',active=array_of_bools[1])),
            dbc.NavItem(dbc.NavLink("BarTender", href='/Reports/BarTender/', active=array_of_bools[2])),
            dbc.NavItem(dbc.NavLink("Electrostretcher", href='/Reports/Electrostretcher/', active=array_of_bools[3])),
        ],
        pills=True,
        horizontal=True,
    )

    return nav