import dash_html_components as html
import dash_core_components as dcc
import base64

image_filename = 'C:\\Users\\Dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\assets\\NanostringLogo.jpg' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

def Header():
    return html.Div([
        get_logo(),
        get_header(),
        html.Br([]),
        get_menu()
    ])

def get_logo():
    logo = html.Div([
            html.Img(src='data:image/jpg;base64,{}'.format(encoded_image.decode()))
        ])
    return logo

def get_header():
    header = html.Div([

        html.Div([
            html.H5(
                'Nanostring Reports')
        ], className="twelve columns padded")

    ], className="row gs-header gs-text-header")
    return header


def get_menu():
    menu = html.Div([

        dcc.Link('Overview - Hamilton      ', href='/Reports/Hamilton/', className="tab first"),

        dcc.Link('Extra   ', href='/Reports/Extra/', className="tab"),

    ], className="row ")
    return menu