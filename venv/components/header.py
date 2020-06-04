import dash_html_components as html
import dash_core_components as dcc

def Header():
    return html.Div([
        get_logo(),
        get_header(),
        html.Br([]),
        get_menu()
    ])

def get_logo():
    logo = html.Div([

        html.Div([
            html.Img(src='C:\\Users\\dbuenger\\PycharmProjects\\DashBoardWebsite\\venv\\assets\\NanostringLogo.jpg',height="150",width = "200",title="Logo")
        ], className="ten columns padded"),

    ], className="row gs-header")
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