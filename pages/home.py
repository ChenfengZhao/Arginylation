import dash
from dash import dcc, html, Input, Output, State, callback
from dash.html.Col import Col
import dash_bootstrap_components as dbc

from util import layoutFunctions as lf

# ------------------------------------------------------------------------------
# Initialize utility objects and useful functions
# ------------------------------------------------------------------------------
# id function that helps manage component id names. It pre-pends
# the name of the page to a string so that writing ids specific for each page is easier 
id = lf.id_factory('home')

# ------------------------------------------------------------------------------
# LAYOUT
# ------------------------------------------------------------------------------
layout = dbc.Container([
    # html.H1('Home page')
    dbc.Row(lf.make_NavBar()), # Navigation Bar
    dbc.Row(lf.make_homeHeader(id)), # Big header

    # First portion (a button jumping to protein visulization)
    dbc.Row([
        # dbc.Button("Start Visualization", id=id("jump_to_viz"),href="/protein", color="success", outline=True)
        html.Div([
            dbc.Button("Start Visualization", id=id("jump_to_viz"),href="/protein", color="primary", style={"font-size": "2rem"}),
            dbc.Tooltip("Click to start visualization", target=id("jump_to_viz")),
        ],
        style={"margin-top": "12rem",
        "margin-bottom": "12rem"},
        className="d-grid gap-2",),
        
    ], className='mt-5 mb-4 bg-light'),

    # Second portion (Overview of the website)
    # dbc.Row(html.Div([
    #     html.P("Arginylation is an essential protein PTM installed by the ATE1 enzyme in mammalian systems. This website included isotopically labeled arginylation sites (peptides) from standard peptides, whole-proteome peptide mixtures, pure proteins, human cells, patient tissues, mouse tissues, etc. Indexed source data of MS1 and MS2 scans are available to download after the selection of a specific sample or species. Source code for website visualization is also available to download from GitHub.", className='my-1'),
    #     html.P("The differentiation of post-translational vs translational Arg using label-free proteomics is biased to predefined arginylation sites by its nature. Installing unnatural Arg (isotopic Arg) to arginylation sites allows for mass spectrometry identification of posttranslational Arg residues, leading to the unbiased discovery of protein arginylation ex vivo using proteomics profiling.", className='my-1')
    # ]), className = 'align-items-center'),
    dbc.Row(html.Div([
        html.P("The Arginylation PTM Website serves as a comprehensive database and research tool for studying the post-translational modification known as arginylation. Its purpose is to provide an indexed compilation of all arginylation sites discovered, along with ATE1 substrates, facilitating in-depth analysis and exploration for researchers in this field.", className='my-1')
    ]), className = 'align-items-center'),
    dbc.Row(html.Div([
        # "Add statics figures of the website here?"
        html.Img(src='./assets/website figures-1.svg', alt='ABAP platform diagram', className='img-fluid'),
        html.I("Activity-based arginylome profiling (ABAP) platform for arginylation discovery from biological samples. "),
        html.I(html.B("a, ")), 
        html.I("isotopic arginine labeling of proteome using ex vivo ATE1 assay. "),
        html.I(html.B("b, ")),
        html.I("computational workflow for unbiased discovery of ATE1 substrates"), 
        # className='ref text-start'
    ]), className = 'ref text-start mb-4 mt-2 align-items-center'),

    # Third portion (several figures)
    # dbc.Row(html.Div([
    #     html.Img(src='./assets/website figure 2.svg', alt='website functions and visulaization', className='img-fluid'),
    # ]),className = 'ref text-start mb-4 mt-4 align-items-center'),
    dbc.Row(html.Div([
        dbc.Carousel(
            items=[
                {'key': "1", 'src': "./assets/website figures-2.svg", 'alt': 'website functions and visulaization', "img_class_name" : 'fluid'},
                {'key': "2", 'src': "./assets/website figures-3.svg", 'alt': 'website functions and visulaization', "img_class_name" : 'fluid'},
                {'key': "3", 'src': "./assets/website figures-4.svg", 'alt': 'website functions and visulaization', "img_class_name" : 'fluid'},
            ],
            # style={'height': '445px', 'position': 'center'},
            controls=True,
            indicators=True,
            variant="dark",
            # className="carousel-fade",
            ride="carousel",
            interval=5000,
        ),
    ]), className = 'ref text-start mb-4 mt-4 align-items-center'),

    # license banner
    dbc.Row([lf.make_CC_licenseBanner(id)]),
    dbc.Row([],style={"margin-top": "500px"}),
])

# ------------------------------------------------------------------------------
# CALLBACKS
# ------------------------------------------------------------------------------
@callback(
    Output(component_id=id('moreInfoCollapse'), component_property='is_open'),
    Input(component_id=id('moreInfoIcon'), component_property='n_clicks'),
    State(component_id=id('moreInfoCollapse'), component_property='is_open'),
    prevent_initial_call=True
)
def invertMoreInfoVisibility(n_clicks, is_open):
    if n_clicks:
            return not is_open
    return is_open
