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

    # First portion (Overview of the website)
    dbc.Row(html.Div([
        html.P("Arginylation is an essential protein PTM installed by the ATE1 enzyme in mammalian systems. This website included isotopically labeled arginylation sites (peptides) from standard peptides, whole-proteome peptide mixtures, pure proteins, human cells, patient tissues, mouse tissues, etc. Indexed source data of MS1 and MS2 scans are available to download after the selection of a specific sample or species. Source code for website visualization is also available to download from GitHub.", className='my-1'),
        html.P("The differentiation of post-translational vs translational Arg using label-free proteomics is biased to predefined arginylation sites by its nature. Installing unnatural Arg (isotopic Arg) to arginylation sites allows for mass spectrometry identification of posttranslational Arg residues, leading to the unbiased discovery of protein arginylation ex vivo using proteomics profiling.", className='my-1')
    ]), className = 'align-items-center'),
    dbc.Row(html.Div([
        # "Add statics figures of the website here?"
        html.Img(src='./assets/ABAP_platform.png', alt='ABAP platform diagram', className='img-fluid'),
        html.I("Figure 1. Activity-based arginylome profiling (ABAP) platform for arginylation discovery from biological samples. "),
        html.I(html.B("a, ")), 
        html.I("isotopic arginine labeling of proteome using ex vivo ATE1 assay. "),
        html.I(html.B("b, ")),
        html.I("computational workflow for unbiased discovery of ATE1 substrates"), 
        # className='ref text-start'
    ]), className = 'ref text-start mb-4 mt-2 align-items-center'),

    # Second portion (a button jumping to protein visulization)
    dbc.Row(
        dbc.Button("Start Visualization", id=id("jump_to_viz"),href="/protein", color="success", outline=True)
    ),
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
