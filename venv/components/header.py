import dash_html_components as html
import dash_core_components as dcc
import base64

import dash_bootstrap_components as dbc

image_filename = 'C:\\Users\\Dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\assets\\NanostringLogo.jpg'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

def Header():
    return html.Div([
        get_logo(),
        get_header(),
        html.Br([]),
        get_menu(),
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
                'NanoString Manufacturing Reports'
            )
        ], className="twelve columns padded", style={'marginTop': 0, 'marginBottom': 0, 'marginLeft': 15} )

    ], className="row gs-header gs-text-header" )
    return header

def get_menu():
    nav = dbc.Nav(
        [
            dbc.NavItem(
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("Hamilton Method Report", header = True,  href='/Reports/Hamilton/Methods/'),
                        dbc.DropdownMenuItem(divider=True),
                        dbc.DropdownMenuItem("Hamilton Time Study Report", header=True, href='/Reports/Hamilton/TimeStudy/'),
                        dbc.DropdownMenuItem(divider=True),
                        dbc.DropdownMenuItem("Hamilton Tip Usage Report", header=True, href='/Reports/Hamilton/Tips/'),
                    ],
                    nav=True,
                    in_navbar=False,
                    label="Hamilton",

                )
            ),
            dbc.NavItem(
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("Bartender Print Jobs", header=True, href='/Reports/BarTender/PrintJobs/'),
                    ],
                    nav=True,
                    in_navbar=False,
                    label="BarTender",

                )
            ),

            dbc.NavItem(
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("Electrostretchers", header=True, href='/Reports/Electrostretcher/RunHistory/'),
                    ],
                    nav=True,
                    in_navbar=False,
                    label="Electrostretcher",

                )
            ),

            dbc.NavItem(
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("Duplicate Codes Report", header=True, href='/Reports/DXTestCodes/Duplicates/'),
                    ],
                    nav=True,
                    in_navbar=False,
                    label="Diagnostic Test Codes",

                )
            ),

            dbc.NavItem(
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("Main Data", header=True,
                                             href='/Reports/Inventory/Main/'),
                    ],
                    nav=True,
                    in_navbar=False,
                    label="Inventory",

                )
            ),
        ],
        pills=True,
        horizontal=True,
    )



    return nav

