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

        # html.Div([
        #     dcc.Link('Full View   ', href='/cc-travel-report/full-view')
        # ], className="two columns page-view no-print")

    ], className="row gs-header")
    return logo


def get_header():
    header = html.Div([

        html.Div([
            html.H5(
                'House Stark Performance Marketing Report')
        ], className="twelve columns padded")

    ], className="row gs-header gs-text-header")
    return header


def get_menu():
    menu = html.Div([

        dcc.Link('Overview - Birst   ', href='/cc-travel-report/overview-birst/', className="tab first"),

        dcc.Link('Overview - GA   ', href='/cc-travel-report/overview-ga/', className="tab"),

        dcc.Link('Paid Search   ', href='/cc-travel-report/paid-search/', className="tab"),

        dcc.Link('Display   ', href='/cc-travel-report/display/', className="tab"),

        dcc.Link('Publishing   ', href='/cc-travel-report/publishing/', className="tab"),

        dcc.Link('Metasearch and Travel Ads   ', href='/cc-travel-report/metasearch-and-travel-ads/', className="tab"),

    ], className="row ")
    return menu