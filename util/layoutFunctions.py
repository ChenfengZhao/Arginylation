from dash import dcc, html
import dash_bootstrap_components as dbc

def id_factory(page: str):
    def func(_id: str):
        """
        Dash pages require each component in the app to have a totally
        unique id for callbacks. This is easy for small apps, but harder for larger 
        apps where there is overlapping functionality on each page. 
        For example, each page might have a div that acts as a trigger for reloading;
        instead of typing "page1-trigger" every time, this function allows you to 
        just use id('trigger') on every page.
        
        How:
            prepends the page to every id passed to it
        Why:
            saves some typing and lowers mental effort
        **Example**
        # SETUP
        from utils import layoutFunctions as lf
        id = lf.id_factory('page1') # create the id function for that page
        
        # LAYOUT
        layout = html.Div(
            id=id('main-div')
        )
        # CALLBACKS
        @app.callback(
            Output(id('main-div'),'children'),
            Input(id('main-div'),'style')
        )
        def funct(this):
            ...
        """
        return f"{page}-{_id}"
    return func

def make_Subtitle(string):
    """
    Makes a subtitle with a line underneath to divide sections
    """
    subtitle = html.Div([
        html.H2(string,
            className="mt-2 mb-0 fw-bolder"),
        html.Hr(className="my-0")   
    ])
    return subtitle

def make_NavBar():
    """
    Makes the navigation bar
    """
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink('Home', href='/home')),
            dbc.NavItem(dbc.NavLink('Protein', href='/protein')),
            # dbc.NavItem(dbc.NavLink('Interactions', href='/interactions')),
            # dbc.NavItem(dbc.NavLink('Genes', href='/genes')),
            # dbc.DropdownMenu(
            #     children=[
            #         dbc.DropdownMenuItem('Cite', id='citeDropdown'),
            #         dbc.DropdownMenuItem('About Us', id='aboutUsDropdown'),
            #     ],
            #     nav=True,
            #     in_navbar=True,
            #     label='More',
            # ),
        ],
        brand='Arginylation Database',
        brand_href='/home',
        color='primary',
        fixed='top',
        dark=True,
        # brand_style={'font-size':'30px'},
        # style={'height':'55px', 'font-size':'25px'},
        style={'height':'40px'},
        class_name=''
    )
    return navbar

def make_homeHeader(idFunc):
    """Makes the header of the home page

    Parameters
    ----------
    idFunc : func
        generate the component id. For example idFunc(abc) returns home-abc as the id
    """
    # Main Title
    header = html.Div(
        dbc.Container([
            html.Div([
                html.H2("Arginylation Site Repository", className="display-4"),
                # dbc.Button("Cite", id=idFunc("btn_citeHeader"),color="success", outline=True)
            ], className='d-flex justify-content-between align-items-center mb-0'),
            
            html.Hr(className="mt-0 mb-1"),
            html.Div([
                html.P("Post-translational arginylation sites and ATE1 substrates", style={'font-size':'1.25rem'}),
                # html.H4(id=idFunc('moreInfoIcon'), className="fa-solid fa-book-open ms-3 mt-1 primary")
            ], className='d-flex mb-0'),
            # dbc.Collapse(
            #     html.Div([
            #         # "This page shows interactive visualizations of PNN data in the brain of ",
            #         # "adult mice", html.Br(), "Data (mean and SEM) come from seven mice.", 
            #         # html.Br(),"For detailed information of the procedure, see ",
            #         # html.A("here", href="https://www.biorxiv.org/content/10.1101/2023.01.24.525313", target="_blank")
            #         "Add more information here"
            #     ]),
            #     id=idFunc("moreInfoCollapse"),
            #     is_open=False,
            # ),
            # dbc.Tooltip("More info.", target=idFunc("moreInfoIcon"), className='ms-1')
            ],
            fluid=True,
            className="py-1 bg-light rounded-3",
        ),
        className="p-0 my-1",
    )
    return header

def make_proteinHeader(idFunc):
    """Makes the header of the protein page

    Parameters
    ----------
    idFunc : func
        generate the component id. For example idFunc(abc) returns home-abc as the id
    """
    # Main Title
    header = html.Div(
        dbc.Container([
            html.Div([
                html.H2("Visualization of Arginylated Proteins and Sites", className="display-4"),
                # dbc.Button("Cite", id=idFunc("btn_citeHeader"),color="success", outline=True)
            ], className='d-flex justify-content-between align-items-center mb-0'),
            
            html.Hr(className="mt-0 mb-1"),
            html.Div([
                html.P("PTM site and mass spectrometry data summary", style={'font-size':'1.25rem'}),
                # html.H4(id=idFunc('moreInfoIcon'), className="fa-solid fa-book-open ms-3 mt-1 primary")
            ], className='d-flex mb-0'),
            # dbc.Collapse(
            #     html.Div([
            #         # "This page shows interactive visualizations of PNN data in the brain of ",
            #         # "adult mice", html.Br(), "Data (mean and SEM) come from seven mice.", 
            #         # html.Br(),"For detailed information of the procedure, see ",
            #         # html.A("here", href="https://www.biorxiv.org/content/10.1101/2023.01.24.525313", target="_blank")
            #         "Add more information here"
            #     ]),
            #     id=idFunc("moreInfoCollapse"),
            #     is_open=False,
            # ),
            # dbc.Tooltip("More info.", target=idFunc("moreInfoIcon"), className='ms-1')
            ],
            fluid=True,
            className="py-1 bg-light rounded-3",
        ),
        className="p-0 my-1",
    )
    return header

def make_CollapsableTable(idFunc):
    """
    Makes the collapsable tabular data section
    """
    collapsTable = html.Div([
        dbc.Button("Open Tabular Data",
            id=idFunc("btn_openTabDiffuse"),
            className="mb-1",
            color="primary",
        ),
        dbc.Collapse(
            id=idFunc("collps_Tab"),
            is_open=False,
        )],
        className='mt-3'
    )
    return collapsTable

def make_CC_licenseBanner(idFunc):
    banner = []

    banner = html.Div([
        html.Hr(className="mt-2 mb-2"),
        html.P(["Web-app is developed by Chenfeng Zhao.",
            # dcc.Link("Chenfeng Zhao.",
            #     href="https://www.chenfengzhao.com/",
            #     target="_blank", className="me-3"),
        " Check source code at ",
            dcc.Link("Github",
                href="https://github.com/ChenfengZhao/Arginylation",
                target="_blank"),
        ]),
        html.P("Suggestions are always welcome at zongtao at wustl dot edu, we reply to every email."),
        # "Suggestions are always welcome at zongtao at wustl dot edu, we reply to every email."
        html.P(["Cite: Lin, Z., Xie, Y., Gongora, J., Liu, X., Zahn, E., Palai, B. B., ... & Garcia, B. A. An Unbiased Proteomic Platform for Activity-based Arginylation Profiling. ", html.I("bioRxiv"), ", 2024, ", html.A("https://doi.org/10.1101/2024.06.01.596974.", href = "https://doi.org/10.1101/2024.06.01.596974"), " PMID: 38854050."]),
        html.P(["This work is licensed under the ",
        html.A(["MIT License"], rel='license', href="https://opensource.org/license/mit/")]),
        # html.P("Updated on 06/29/2024."),
        html.P("Updated on 02/22/2025."),
    ], id=idFunc("licenseBanner"), className='pt-5')
    return banner