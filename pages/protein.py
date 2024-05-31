from logging import disable
from typing import DefaultDict
import dash
from dash import Dash, dcc, html, Input, Output, callback, State, dash_table
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Col import Col

import pandas as pd
import plotly.express as px
import os

import pandas as pd
import numpy as np
import re
from collections import defaultdict

from util import layoutFunctions as lf

import zipfile
from io import BytesIO

# ------------------------------------------------------------------------------
# Initialize utility objects and useful functions
# ------------------------------------------------------------------------------
# id function that helps manage component id names. It pre-pends
# the name of the page to a string so that writing ids specific for each page is easier 
id = lf.id_factory('protein')

# ------------------------------------------------------------------------------
# Load the necessary data
# ------------------------------------------------------------------------------
# read web info excel
df_web_info = pd.read_excel("./data/web_info.xlsx", sheet_name=0)
# df_web_info = df_web_info.set_index("Folder_Name", drop=False)

df_res_mass = pd.read_excel('./data/residue_mass.xlsx', sheet_name=0)
df_res_mass = df_res_mass.set_index('Letter1', drop=False)

df_atom_mass = pd.read_excel('./data/residue_mass.xlsx', sheet_name=1)
df_atom_mass = df_atom_mass.set_index('atom_name', drop=False)

# the color scheme for ms2 ions search display
df_ions_color = pd.read_excel('./data/residue_mass.xlsx', sheet_name=2)
df_ions_color = df_ions_color.set_index('ions_type', drop=False)

# ------------------------------------------------------------------------------
# Perform some preprocessing
# ------------------------------------------------------------------------------
# generate the information list to be searched
# print("df_web_info", df_web_info)
search_info_list = []
# and generate multiple default dicts of web information
web_info_dict = defaultdict(dict) # dict of protein dict of r_seq dict of r_seq info dict (species-sample : protein : r_seq : {'partition': partition, 'charge': charge, 'calcmy': calcmy})
for row in df_web_info.itertuples():
    protein = row.Protein
    species = row.Species
    sample = row.Sample
    r_seq = row.R_sequence
    partition = row.Partition
    charge = str(row.z)
    calcmy = row.Calcmass_y

    # concate the above info with "-"
    par_seq = ",".join(["_".join(x.split('_')[-2:]) for x in partition.split(',')])
    search_info = "-".join([protein, species, sample, r_seq, par_seq, charge])
    search_info_list.append(search_info)

    # generate protein_info_dict
    # protein_info_dict["-".join([species, sample])].add(protein)
    # web_info_dict["-".join([species, sample])][protein] = {r_seq : {'partition': partition, 'charge': charge, 'calcmy': calcmy}}
    # print("r_seq", r_seq)
    ss = "-".join([species, sample])
    if ss not in web_info_dict or protein not in web_info_dict[ss]:
        web_info_dict[ss][protein] = {r_seq : {'partition': partition, 'charge': charge, 'calcmy': calcmy}}
    else:
        web_info_dict[ss][protein][r_seq] = {'partition': partition, 'charge': charge, 'calcmy': calcmy}
    # print("web_info_dict:", web_info_dict)

# print("search_info_list:", search_info_list)
# print("web_info_dict:", web_info_dict)

# calculate residue mass for each element - res_mass_dict (residue_name : residue_mass)
res_mass_dict = defaultdict(float)
for row in df_res_mass.itertuples():
    elem_mass_list = []
    elem_weight_list = []

    # print(row)
    formula = row.Formula
    residue = row.Letter1

    match_form = re.findall(r'([A-Za-z]+)(\d+)', formula)
    
    for elem in match_form:
        elem_mass_list.append(df_atom_mass.loc[elem[0]]['mass'])
        elem_weight_list.append(int(elem[1]))
    
    res_mass = sum(np.multiply(elem_mass_list, elem_weight_list))
    res_mass_dict[residue] = res_mass # residue_name : residue_mass


# create a rainbow color map for all the ms2 ions
# color_list = ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, len(df_ions_color['ions_type']))]
# color_map = defaultdict(str) # the rainbow color map (ions_type : color)
# for i, ions_type in enumerate(df_ions_color['ions_type']):
#     color_map[ions_type] = color_list[i]
# print("color_map", color_map)
df_ions_color['color'] = ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, len(df_ions_color['ions_type']))]

# ------------------------------------------------------------------------------
# LAYOUT
# ------------------------------------------------------------------------------

layout = dbc.Container([
    dbc.Row(lf.make_NavBar()), # Navigation Bar
    dbc.Row(lf.make_proteinHeader(id)), # Big header
    
    # first portion(search engin)
    dbc.Row([lf.make_Subtitle("Global Search")]),
    dbc.Row([
        # html.Datalist(id="search_suggestion_list", children=[html.Option(value=x) for x in search_info_list]),
        # dbc.InputGroup([
        #     dbc.InputGroupText(html.I(className="fas fa-search")),
        #     dbc.Input(id='global_search', type='search', placeholder='Enter search term...', list="search_suggestion_list"),
        # ], className="mb-3"),

        html.Div([
            dbc.InputGroup([
                dbc.InputGroupText(html.I(className="fas fa-search")),
                html.Div([
                    dcc.Dropdown(
                        id='global_search',
                        options={x: x for x in search_info_list},
                        placeholder="Input information to be searched",
                    )
                ], style={'flex-grow':'1'})
            ]),
        ], className='mt-1 mb-5')
    ], className='mt-5'),

    # second portion (general ocnfiguration dropdowns)
    dbc.Row([lf.make_Subtitle("General Configuration")]),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H6("Select a species:", className='my-1'),

                dbc.InputGroup([
                    html.Div([
                        dcc.Dropdown(
                            id='first_level', 
                            options={'./data/' + x: x for x in os.listdir('./data') if(os.path.isdir('./data/' + x))}, 
                            value="./data/Human")
                    ], style={'flex-grow':'1'}),
                    html.Div([
                        # dbc.Button([html.I(className="fa-solid fa-info")],id='first_level_btn_info')
                        dbc.Button([html.I(className="fa-solid fa-download")],id='download_species_button',  n_clicks=0),
                        dcc.Download(id="download_species_file"),
                    ])
                ])
            ], className='mt-1 mb-5')
        ], xs=12, lg=4, className='mt-5'),
        dbc.Col([
            html.Div([
                html.H6("Select a cell, tissue, or patient sample:", className='my-1'),

                dbc.InputGroup([
                    html.Div([
                        dcc.Dropdown(id='second_level')
                    ], style={'flex-grow':'1'}),
                    html.Div([
                        # dbc.Button([html.I(className="fa-solid fa-info")],id='second_level_btn_info')
                        dbc.Button([html.I(className="fa-solid fa-download")],id='download_sample_button',  n_clicks=0),
                        dcc.Download(id="download_sample_file"),
                    ])
                ])
            ], className='mt-1 mb-5')
        ],xs=12, lg=4, className='mt-5'),

        dbc.Col([
            html.Div([
                html.H6("Select a protein:", className='my-1'),

                dbc.InputGroup([
                    html.Div([
                        dcc.Dropdown(id='third_level')
                    ], style={'flex-grow':'1'}),
                    # html.Div([
                    #     dbc.Button([html.I(className="fa-solid fa-info")],id='third_level_btn_info')
                    # ])
                ])
            ], className='mt-1 mb-5')
        ],xs=12, lg=4, className='mt-5')
    ]),

    dbc.Row([
        dbc.Col([
            html.Div([
                html.H6("Select a sequence", className='my-1'),

                dbc.InputGroup([
                    html.Div([
                        dcc.Dropdown(id='sequence')
                    ], style={'flex-grow':'1'}),
                    # html.Div([
                    #     dbc.Button([html.I(className="fa-solid fa-info")],id='partition_btn_info')
                    # ])
                ])
            ], className='mt-1 mb-5')
        ],xs=12, lg=4, className='mt-5'),
        dbc.Col([
            html.Div([
                html.H6("Select a fraction of a sample", className='my-1'),

                dbc.InputGroup([
                    html.Div([
                        dcc.Dropdown(id='partition')
                    ], style={'flex-grow':'1'}),
                    # html.Div([
                    #     dbc.Button([html.I(className="fa-solid fa-info")],id='partition_btn_info')
                    # ])
                ])
            ], className='mt-1 mb-5')
        ],xs=12, lg=4, className='mt-5'),

        dbc.Col([
            html.Div([
                html.H6("Select a charge state", className='my-1'),

                dbc.InputGroup([
                    html.Div([
                        dcc.Dropdown(id='charge')
                    ], style={'flex-grow':'1'}),
                    # html.Div([
                    #     dbc.Button([html.I(className="fa-solid fa-info")],id='charge_btn_info')
                    # ])
                ])
            ], className='mt-1 mb-5')
        ], xs=12, lg=4, className='mt-5'),

        dcc.Store(id='pl_list_dict'), # dict of mass list of peptide.L
        dcc.Store(id='ph_list_dict'), # dict of mass list of peptide.H
        dcc.Store(id='found_idxl_list_dict'), # dict of found ions index list for peptide.L
        dcc.Store(id='found_idxh_list_dict'), # dict of found ions index list for peptide.H
        dcc.Store(id='ms1_mass_list'),
    ]),

    # third portion (MS1 confugration dropdowns)
    dbc.Row([lf.make_Subtitle("MS1 Spectrum")]),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H6("Select a MS1 scan:", className='my-1'),

                dbc.InputGroup([
                    html.Div([
                        dcc.Dropdown(id='forth_level')
                    ], style={'flex-grow':'1'}),
                    # html.Div([
                    #     dbc.Button([html.I(className="fa-solid fa-info")],id='forth_level_btn_info')
                    # ])
                ]),
                dbc.InputGroup([
                    dbc.InputGroupText("MS1 MZ Error Margin:"),
                    dbc.Input(id='mz_error_margin_ms1', type='number', value=20),
                    dbc.InputGroupText('ppm')
                ]),
            ], className='mt-1 mb-5')
        ], xs=12, lg=4, className='mt-5'),

        # dbc.Col([
        #     html.Div([
        #         dbc.InputGroup([
        #             dbc.InputGroupText("MZ Error Margin:"),
        #             dbc.Input(id='mz_error_margin_ms1', type='number', value=20),
        #             dbc.InputGroupText('ppm')
        #         ]),
        #     ], className='mt-1 mb-5')
        # ], xs=12, lg=4, className='mt-5')
    
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Spinner(
                dcc.Graph(id='graph_ms1', config={'displaylogo':False}),
                color='primary'
            )
        ]),
        dbc.Col([
                dbc.Spinner(
                dcc.Graph(id='graph_ms1_summary', config={'displaylogo':False}),
                color='primary'
            )
        ])
    ]),

    # forth portion (MS2 configuration dropdowns)
    dbc.Row([lf.make_Subtitle("MS2 Spectrum")]),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H6("Check ion types (click on OK button after selection):", className='my-1'),

                # dbc.InputGroup([
                #     # html.Div([
                #     #     dbc.Button(id='ms2_ion_type_button', n_clicks=0, children='OK'),
                #     #     dbc.Button(id='ms2_ion_type_button_all', n_clicks=0, children='ALL'),
                #     #     # dbc.Button(id='ms2_ion_type_button_reset', n_clicks=0, children='RESET'),
                #     # ]),
                #     html.Div([
                #         dbc.ButtonGroup([
                #             dbc.Button(id='ms2_ion_type_button', n_clicks=0, outline=True, color="primary", children='OK'),
                #             dbc.Button(id='ms2_ion_type_button_all', n_clicks=0, outline=True, color="primary", children='ALL'),
                #             dbc.Button(id='ms2_ion_type_button_reset', n_clicks=0, outline=True, color="primary", children='RESET'),
                #         ])
                #     ], style={'textAlign': 'center'}),
                #     html.Div([
                #         dcc.Checklist(id='ms2_ion_type_checklist', value=['b', 'b-H2O', 'b-NH3', 'b++', 'b++-H2O', 'b++-NH3', 'y', 'y-H2O', 'y-NH3', 'y++', 'y++-H2O', 'y++-NH3'], options={x : x for x in df_ions_color['ions_type'] if x != 'Seq.'}, inline=True),
                #         # dcc.Dropdown(id='ms2_ion_type_checklist', value=['b', 'y'], options={x : x for x in df_ions_color['ions_type'] if x != 'Seq.'}, multi = True,),
                #     ], # style={'flex-grow':'1', "marginRight": 15,"width": 350, 'margin': '30px'}
                #     style={'flex-grow':'1','padding': '10px', "width": "100%"}),
                # ])
                dbc.Row([
                    html.Div([
                        dbc.ButtonGroup([
                            dbc.Button(id='ms2_ion_type_button', n_clicks=0, outline=True, color="primary", children='OK'),
                            dbc.Button(id='ms2_ion_type_button_all', n_clicks=0, outline=True, color="primary", children='ALL'),
                            dbc.Button(id='ms2_ion_type_button_reset', n_clicks=0, outline=True, color="primary", children='RESET'),
                        ])
                    ], style={'textAlign': 'center'}),
                ]),
                dbc.Row([
                    html.Div([
                        dcc.Checklist(id='ms2_ion_type_checklist', value=['b', 'b-H2O', 'b-NH3', 'b++', 'b++-H2O', 'b++-NH3', 'y', 'y-H2O', 'y-NH3', 'y++', 'y++-H2O', 'y++-NH3'], options={x : x for x in df_ions_color['ions_type'] if x != 'Seq.'}, inline=True),
                        # dcc.Dropdown(id='ms2_ion_type_checklist', value=['b', 'y'], options={x : x for x in df_ions_color['ions_type'] if x != 'Seq.'}, multi = True,),
                    ], # style={'flex-grow':'1', "marginRight": 15,"width": 350, 'margin': '30px'}
                    style={'flex-grow':'1','padding': '10px', "width": "100%"}),
                ]),
            ], className='mt-1 mb-5')
        ], xs=12, lg=4, className='mt-5'),

        dbc.Col([
            html.Div([
                html.H6("Select a light MS2 spectrum (Arg0 modified):", className='my-1'),

                dbc.InputGroup([
                    html.Div([
                        dcc.Dropdown(id='ms2l'),
                    ], style={'flex-grow':'1'})
                    # html.Div([
                    #     dbc.Button([html.I(className="fa-solid fa-info")],id='ms2l_btn_info')
                    # ])
                ]),

                dbc.InputGroup([
                    dbc.InputGroupText("MS2 MZ Error Margin:"),
                    dbc.Input(id='mz_error_margin', type='number', value=20),
                    dbc.InputGroupText('ppm')
                ]),
            ], className='mt-1 mb-5')
        ], xs=12, lg=4, className='mt-5'),

        dbc.Col([
            html.Div([
                html.H6("Select a heavy MS2 spectrum (Arg10 modified):", className='my-1'),

                dbc.InputGroup([
                    html.Div([
                        dcc.Dropdown(id='ms2h'),
                    ], style={'flex-grow':'1'}),
                    # html.Div([
                    #     dbc.Button([html.I(className="fa-solid fa-info")],id='ms2l_btn_info')
                    # ])
                ])
            ], className='mt-1 mb-5')
        ], xs=12, lg=4, className='mt-5')
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Spinner(
                dcc.Graph(id='graph_ms2l', config={'displaylogo':False}),
                color='primary'
            ),
        ]),
        dbc.Col([
            dbc.Spinner(
                dcc.Graph(id='graph_ms2h', config={'displaylogo':False}),
                color='primary'
            ),
        ]),
    ]),
    dbc.Row([
        # dbc.Col([
        html.Div([
            html.H5("MS2L Ion Mass Table", style={'text-align': 'center'}),
            dash_table.DataTable(
                id='ms2l_calInos_tab',
                # virtualization=True,
                # style_table={
                #     'height': '450px'
                # },
                style_cell={
                    # 'font-family': 'Arial',
                    'text-align': 'center'
                },
                style_data={
                    'color': 'black',
                    # 'backgroundColor': 'white',
                    'border': '1px solid grey'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(220, 220, 220)'
                    }
                ],
               style_header={
                    'backgroundColor': 'rgb(210, 210, 210)',
                    'color': 'black',
                    'fontWeight': 'bold',
                    'border': '1px solid grey'
                },
            ),
        # ], xs=12, lg=4, className='mt-5'),
        ]),
    ], className='mt-5'),
    dbc.Row([
        # dbc.Col([
        html.Div([
            html.H5("MS2H Ion Mass Table", style={'text-align': 'center'}),
            dash_table.DataTable(
                id='ms2h_calInos_tab',
                style_cell={
                    # 'font-family': 'Arial',
                    'text-align': 'center'
                },
                style_data={
                    'color': 'black',
                    # 'backgroundColor': 'white',
                    'border': '1px solid grey'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(220, 220, 220)'
                    }
                ],
               style_header={
                    'backgroundColor': 'rgb(210, 210, 210)',
                    'color': 'black',
                    'fontWeight': 'bold',
                    'border': '1px solid grey'
                },
            )
        # ], xs=12, lg=4, className='mt-5'),
        ]),
    ], className='mt-5 mb-5') 
])

# ------------------------------------------------------------------------------
# CALLBACKS
# ------------------------------------------------------------------------------
@callback(
    Output('first_level', 'value'),
    Output('second_level', 'value'),
    Output('third_level', 'value'),
    Output('sequence', 'value'),
    Output('partition', 'value'),
    Output('charge', 'value'),
    Output('forth_level', 'value'),
    Output('ms2l', 'value'),
    Output('ms2h', 'value'),
    Output('ms2_ion_type_button', 'n_clicks'),
    Input('global_search', 'value'),
    prevent_initial_call=True
)
def fillin_search_result(search_result):
    """Use selected search result to fill in configurations
    Parameters
    ----------
    search_result : str
        the selected search result string
    
    Returns
    -------
    _type_
        _description_
    """
    if search_result is None:
        # return dash.no_update, dash.no_update, dash.no_update
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    res_elem_list = search_result.split("-")
    protein = res_elem_list[0]
    species = res_elem_list[1]
    sample = res_elem_list[2]
    r_seq = res_elem_list[3]

    species_val = './data/' + species
    sample_val = species_val + '/' + sample
    # protein_val = sample_val + '/' + folder_name
    protein_val = protein

    # generate default partition value (The first partition value in the excel)
    par_seq = web_info_dict["-".join([species, sample])][protein][r_seq]['partition']
    partition_value = par_seq.split(',')[0]

    print("partition_value", partition_value)

    # generate default charge value (The first charge value in the excel)
    charge_seq = web_info_dict["-".join([species, sample])][protein][r_seq]['charge']
    charge_value = charge_seq.split(',')[0]

    # generate default ms1 excel file
    fp = sample_val + '/' + partition_value + "_" + charge_value + "_" + r_seq
    # ms1_default_file = fp + '/' + [x for x in os.listdir(fp) if x.split('_')[0] == 'ms1'][0]
    # print("ms1_default_file", ms1_default_file)
    ms1_rt_list = [float('.'.join(x.split('_')[-1].split('.')[0:2])) for x in os.listdir(fp) if x.split('_')[0] == 'ms1']
    ms1_rt_list.sort()
    ms1_default_file = fp + '/' + 'ms1_' + partition_value + '_' + charge_value + '_' + r_seq + '_' + str(ms1_rt_list[0]) + '.xlsx'

    # generate default ms2l excel file
    # ms2l_default_file = fp + '/' + [x for x in os.listdir(fp) if x.split('_')[0] == 'ms2L'][0]
    ms2l_scanNum_list = [int(x.split('_')[-1].split('.')[0]) for x in os.listdir(fp) if x.split('_')[0] == 'ms2L']
    ms2l_scanNum_list.sort()
    ms2l_default_file = fp + '/' + 'ms2L_' + partition_value + "_" + charge_value + "_" + r_seq + '_' + str(ms2l_scanNum_list[0]) + '.xlsx'

    # generate default ms2h excel file
    # ms2h_default_file = fp + '/' + [x for x in os.listdir(fp) if x.split('_')[0] == 'ms2H'][0]
    ms2h_scanNum_list = [int(x.split('_')[-1].split('.')[0]) for x in os.listdir(fp) if x.split('_')[0] == 'ms2H']
    ms2h_scanNum_list.sort()
    ms2h_default_file = fp + '/' + 'ms2H_' +  partition_value + "_" + charge_value + "_" + r_seq + '_' + str(ms2h_scanNum_list[0]) + '.xlsx'

    # click the ms2_ion_type_button
    ms2_ion_type_button_nclick = 1

    # return species, sample, protein
    return species_val, sample_val, protein_val, r_seq, partition_value, charge_value, ms1_default_file, ms2l_default_file, ms2h_default_file, ms2_ion_type_button_nclick

@callback(
    Output('download_species_file', 'data'),
    Input('download_species_button', 'n_clicks'),
    State('first_level', 'value'),
    prevent_initial_call=True,
)
def download_species_files(download_species_button_nclick, species_path):
    """download all the files of the selected species

    Parameters
    ----------
    download_species_button_nclick : int
        click number of download_species_button
    species_path : str
        the path of all the file s of the selected species

    Returns
    -------
    species_file : dcc.Download.data
        The data to be downloaded
    """

    if download_species_button_nclick == 0 or species_path is None:
        return dash.no_update
    
    # print("species_path:", species_path)
    
    species = species_path.split("/")[-1] # species name

    files_to_download = [] # the paths of all the files
    # Walk through the directory tree and collect all files
    for root, dirs, files in os.walk(species_path):
        for file in files:
            file_path = os.path.join(root, file)
            files_to_download.append(file_path)

    # 1st argument of send_bytes is a funciton instead of a ByteIO object
    def create_zip(bytes_io):
        with zipfile.ZipFile(bytes_io, 'w') as zipf:
            for file_path in files_to_download:
                zipf.write(file_path, os.path.relpath(file_path, species_path))
    
    return dcc.send_bytes(create_zip, species+".zip")

# @app.callback(
@callback(
    Output('second_level', 'options'),
    Input('first_level', 'value'),
    # prevent_initial_call=True
)
def gen_second_level_list(curLevel_val):
    """generate the sample list (second level) based on the selected Species

    Parameters
    ----------
    curLevel_val : dcc.Dropdown.value
        The value of the Species dropdown

    Returns
    -------
    nextLevel_options : dcc.Dropdown.options
        The options of the Sample dropdown
    """
    if curLevel_val is None:
        return dash.no_update
    
    fp = curLevel_val # the (relative) path of the xlsx file
    nextLevel_options = {fp + "/" + x : x for x in os.listdir(fp) if(os.path.isdir(fp + "/" + x))}
    return nextLevel_options

@callback(
    Output('download_sample_file', 'data'),
    Input('download_sample_button', 'n_clicks'),
    State('second_level', 'value'),
    prevent_initial_call=True,
)
def download_sample_files(download_sample_button_nclick, sample_path):
    """download all the files of the selected sample

    Parameters
    ----------
    download_sample_button_nclick : int
        click number of download_sample_button
    sample_path : str
        the path of all the file s of the selected sample

    Returns
    -------
    sample_file : dcc.Download.data
        The data to be downloaded
    """

    if download_sample_button_nclick == 0 or sample_path is None:
        return dash.no_update
    
    sample = sample_path.split("/")[-1] # sample name

    files_to_download = [] # the paths of all the files
    # Walk through the directory tree and collect all files
    for root, dirs, files in os.walk(sample_path):
        for file in files:
            file_path = os.path.join(root, file)
            files_to_download.append(file_path)

    # 1st argument of send_bytes is a funciton instead of a ByteIO object
    def create_zip(bytes_io):
        with zipfile.ZipFile(bytes_io, 'w') as zipf:
            for file_path in files_to_download:
                zipf.write(file_path, os.path.relpath(file_path, sample_path))
    
    return dcc.send_bytes(create_zip, sample+".zip")



@callback(
    Output('third_level', 'options'),
    Input('first_level', 'value'),
    Input('second_level', 'value'),
    prevent_initial_call=True
)
def gen_third_level(species_path, sample_path):
    """generate the protein list (thrid level) based on the selected Sample

    Parameters
    ----------
    species_path : str
        path of species folder
    sample_path : str
        path of sample folder

    Returns
    -------
    nextLevel_options : dcc.Dropdown.options
        The options of the Protein dropdown
    """
    if species_path is None or sample_path is None:
        return dash.no_update

    species = species_path.split("/")[-1]
    sample = sample_path.split("/")[-1]
    # print("species", species, "sample", sample)
    nextLevel_options = {x: x for x in web_info_dict["-".join([species, sample])].keys()}

    return nextLevel_options

@callback(
    Output('sequence', 'options'),
    Input('first_level', 'value'),
    Input('second_level', 'value'),
    Input('third_level', 'value'),
    prevent_initial_call=True
)
def gen_sequence_level(species_path, sample_path, protein):
    """generate sequence information based on species, sample, protein
    Parameters
    ----------
    species_path : str
        path of species folder
    sample_path : str
        path of sample folder
    protein : str
        The name of protein
    
    Returns
    -------
    seq_options : dcc.Dropdown.options
        The options of sequence Dropdown
    """
    if species_path is None or sample_path is None or protein is None:
        return dash.no_update
    
    species = species_path.split("/")[-1]
    sample = sample_path.split("/")[-1]
    # print("species", species, "sample", sample, "protein", protein)
    # print("web_info_dict",web_info_dict)
    
    seq_options = {x : x for x in web_info_dict["-".join([species, sample])][protein].keys()}
    # print("seq_options", seq_options)
    return seq_options


@callback(
    Output('partition', 'options'),
    Output('charge', 'options'),
    # Output('bl_mass_list', 'data'),
    # Output('yl_mass_list', 'data'),
    Output('pl_list_dict', 'data'),
    Output('ph_list_dict', 'data'),
    Input('second_level', 'value'),
    Input('third_level', 'value'),
    Input('sequence', 'value'),
    prevent_initial_call=True
)
def gen_protein_info(sample_path, protein, r_seq):
    """generate the partition list, charge list, b_mass list for piptite.L, y_mass list for peptite.L, based on the selected Protein

    Parameters
    ----------
    sample_path : str
        path of sample folder
    protein : str
        The name of protein
    r_seq : str
        Selected R sequence

    Returns
    -------
    partition_options : dcc.Dropdown.options
        The options of the Partition dropdown
    charge_options : dcc.Dropdown.options
        The options of the Charge dropdown
    pl_list_dict : list
        dict of calculated ions list of peptite.L
    ph_list_dict : list
        dict of calculated ions list of peptite.H
    """
    if sample_path is None or protein is None or r_seq is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # generate partition list
    # fd_name = curLevel_val.split('/')[-1]
    # partition_options = {x : x for x in df_web_info.loc[fd_name]['Partition'].split(',')}

    species = sample_path.split('/')[-2]
    sample = sample_path.split('/')[-1]
    partition_seq = web_info_dict["-".join([species, sample])][protein][r_seq]['partition']
    partition_options = {x: "_".join(x.split('_')[-2:])  for x in partition_seq.split(',')}
    # print("partition_options", partition_options)
    

    # generate charge list
    # charge_options = {int(x) : x for x in df_web_info.loc[fd_name]['z'].split(',')}
    charge_seq = web_info_dict["-".join([species, sample])][protein][r_seq]['charge']
    charge_options = {int(x) : x for x in charge_seq.split(',')}

    # calculate calcmassy
    calcmy = float(web_info_dict["-".join([species, sample])][protein][r_seq]['calcmy'])

    # generate the lb_mass_list and ly_mass_list for Peptite_L
    # r_seq = df_web_info.loc[fd_name]['R_sequence']
    r_seq = [x for x in r_seq]

    # calculate the mass of commonly used compound
    h2o_mass = df_atom_mass.loc['H']['mass'] * 2 + df_atom_mass.loc['O']['mass']
    nh3_mass = df_atom_mass.loc['N']['mass'] + df_atom_mass.loc['H']['mass'] * 3
    co_mass = df_atom_mass.loc['C']['mass'] +  df_atom_mass.loc['O']['mass']
    nh_mass = df_atom_mass.loc['N']['mass'] + df_atom_mass.loc['H']['mass']

    pl_list_dict = defaultdict(np.array)
    ph_list_dict = defaultdict(np.array)
    # left ions calculation
    # calcualte b
    bl_mass_list = []
    for i in range(len(r_seq)):
        cur_res_mass = res_mass_dict[r_seq[i]]
        if i == 0:
            # b_mass = cur_res_mass + df_atom_mass.loc['H']['mass'] * 2 + df_atom_mass.loc['O']['mass']
            b_mass = cur_res_mass + df_atom_mass.loc['H+']['mass']
        else:
            prev_b_mass = bl_mass_list[-1]
            b_mass = cur_res_mass + prev_b_mass
        
        bl_mass_list.append(b_mass) # b0, b1, ..., bn
    
    pl_list_dict['b'] = np.array(bl_mass_list)
    ph_list_dict['b'] = pl_list_dict['b'] + df_atom_mass.loc['diff']['mass']

    # calculate a
    pl_list_dict['a'] = pl_list_dict['b'] - co_mass
    ph_list_dict['a'] = ph_list_dict['b'] - co_mass

    # calculate a-H2O
    pl_list_dict['a-H2O'] = pl_list_dict['a'] - h2o_mass
    ph_list_dict['a-H2O'] = ph_list_dict['a'] - h2o_mass

    # calculate a-HN3
    pl_list_dict['a-HN3'] = pl_list_dict['a'] - nh3_mass
    ph_list_dict['a-HN3'] = ph_list_dict['a'] - nh3_mass

    # calculate a++
    pl_list_dict['a++'] = (pl_list_dict['a'] + df_atom_mass.loc['H+']['mass']) / 2
    ph_list_dict['a++'] = (ph_list_dict['a'] + df_atom_mass.loc['H+']['mass']) / 2

    # calculate a++-H2O
    pl_list_dict['a++-H2O'] = pl_list_dict['a++'] - h2o_mass
    ph_list_dict['a++-H2O'] = ph_list_dict['a++'] - h2o_mass

    # calculate a++-NH3
    pl_list_dict['a++-NH3'] = pl_list_dict['a++'] - nh3_mass
    ph_list_dict['a++-NH3'] = ph_list_dict['a++'] - nh3_mass

    # calculate b-H2O
    pl_list_dict['b-H2O'] = pl_list_dict['b'] - h2o_mass
    ph_list_dict['b-H2O'] = ph_list_dict['b'] - h2o_mass

    # calculate b-NH3
    pl_list_dict['b-NH3'] = pl_list_dict['b'] - nh3_mass
    ph_list_dict['b-NH3'] = ph_list_dict['b'] - nh3_mass

    # calculate b++
    pl_list_dict['b++'] = (pl_list_dict['b'] + df_atom_mass.loc['H+']['mass']) / 2
    ph_list_dict['b++'] = (ph_list_dict['b'] + df_atom_mass.loc['H+']['mass']) / 2

    # calculate b++-H2O
    pl_list_dict['b++-H2O'] = pl_list_dict['b++'] - h2o_mass
    ph_list_dict['b++-H2O'] = ph_list_dict['b++'] - h2o_mass

    # calculate b++-NH3
    pl_list_dict['b++-NH3'] = pl_list_dict['b++'] - nh3_mass
    ph_list_dict['b++-NH3'] = ph_list_dict['b++'] - nh3_mass

    # calculate c
    pl_list_dict['c'] = pl_list_dict['b'] + nh3_mass
    ph_list_dict['c'] = ph_list_dict['b'] + nh3_mass

    # calculate c-H2O
    pl_list_dict['c-H2O'] = pl_list_dict['c'] - h2o_mass
    ph_list_dict['c-H2O'] = ph_list_dict['c'] - h2o_mass

    # calculate c-NH3
    pl_list_dict['c-NH3'] = pl_list_dict['c'] - nh3_mass
    ph_list_dict['c-NH3'] = ph_list_dict['c'] - nh3_mass

    # calculate c++
    pl_list_dict['c++'] = (pl_list_dict['c'] + df_atom_mass.loc['H+']['mass']) / 2
    ph_list_dict['c++'] = (ph_list_dict['c'] + df_atom_mass.loc['H+']['mass']) / 2

    # calculate c++-H2O
    pl_list_dict['c++-H2O'] = pl_list_dict['c++'] - h2o_mass
    ph_list_dict['c++-H2O'] = ph_list_dict['c++'] - h2o_mass

    # calculate c++-NH3
    pl_list_dict['c++-NH3'] = pl_list_dict['c++'] - nh3_mass
    ph_list_dict['c++-NH3'] = ph_list_dict['c++'] - nh3_mass

    # calcualte MH+
    pl_list_dict['MH+'] = np.array([calcmy] * len(r_seq))
    ph_list_dict['MH+'] = pl_list_dict['MH+'] + df_atom_mass.loc['diff']['mass']

    # print("pl_list_dict['MH+']", pl_list_dict['MH+'])

    # calculate MH++
    pl_list_dict['MH++'] = (pl_list_dict['MH+'] + df_atom_mass.loc['H+']['mass']) / 2
    ph_list_dict['MH++'] = (ph_list_dict['MH+'] + df_atom_mass.loc['H+']['mass']) / 2

    # calculate MH+++
    pl_list_dict['MH+++'] = (pl_list_dict['MH+'] + 2 * df_atom_mass.loc['H+']['mass']) / 3
    ph_list_dict['MH+++'] = (ph_list_dict['MH+'] + 2 * df_atom_mass.loc['H+']['mass']) / 3

    # calculate MH-H2O(+)
    pl_list_dict['MH-H2O(+)'] = pl_list_dict['MH+'] - h2o_mass
    ph_list_dict['MH-H2O(+)'] = ph_list_dict['MH+'] - h2o_mass

    # calculate MH-H2O(++)
    pl_list_dict['MH-H2O(++)'] = (pl_list_dict['MH+'] + df_atom_mass.loc['H+']['mass'] - h2o_mass) / 2
    ph_list_dict['MH-H2O(++)'] = (ph_list_dict['MH+'] + df_atom_mass.loc['H+']['mass'] - h2o_mass) / 2

    # calculate MH-H2O(+++)
    pl_list_dict['MH-H2O(+++)'] = (pl_list_dict['MH+'] + 2 * df_atom_mass.loc['H+']['mass'] - h2o_mass) / 3
    ph_list_dict['MH-H2O(+++)'] = (ph_list_dict['MH+'] + 2 * df_atom_mass.loc['H+']['mass'] - h2o_mass) / 3
    
    # calculate MH-NH3(+)
    pl_list_dict['MH-NH3(+)'] = pl_list_dict['MH+'] - nh3_mass
    ph_list_dict['MH-NH3(+)'] = ph_list_dict['MH+'] - nh3_mass

    # calculate MH-NH3(++)
    pl_list_dict['MH-NH3(++)'] = (pl_list_dict['MH+'] + df_atom_mass.loc['H+']['mass'] - nh3_mass) / 2
    ph_list_dict['MH-NH3(++)'] = (ph_list_dict['MH+'] + df_atom_mass.loc['H+']['mass'] - nh3_mass) / 2

    # calculate MH-NH3(+++)
    pl_list_dict['MH-NH3(+++)'] = (pl_list_dict['MH+'] + 2 * df_atom_mass.loc['H+']['mass'] - nh3_mass) / 3
    ph_list_dict['MH-NH3(+++)'] = (ph_list_dict['MH+'] + 2 * df_atom_mass.loc['H+']['mass'] - nh3_mass) / 3

    # calculate the mass of right ions
    # calculate y
    yl_mass_list = []
    for i in range(-1, -1-len(r_seq), -1):
        # print('elem:', r_seq[i], i)
        cur_res_mass = res_mass_dict[r_seq[i]]
        if i == -1:
            # y_mass = cur_res_mass + df_atom_mass.loc['N']['mass'] + df_atom_mass.loc['H']['mass'] * 2 - df_atom_mass.loc['O']['mass'] - df_atom_mass.loc['H']['mass'] + df_atom_mass.loc['H+']['mass']
            y_mass = cur_res_mass + df_atom_mass.loc['H']['mass'] * 2 + df_atom_mass.loc['O']['mass'] + df_atom_mass.loc['H+']['mass'] + df_atom_mass.loc['N']['mass'] + df_atom_mass.loc['H']['mass'] * 2 - df_atom_mass.loc['O']['mass'] - df_atom_mass.loc['H']['mass']
        else:
            prev_y_mass = yl_mass_list[-1]
            y_mass = cur_res_mass + prev_y_mass
        
        yl_mass_list.append(y_mass) # y0, y1, ..., yn

    pl_list_dict['y'] = np.array(yl_mass_list)
    ph_list_dict['y'] = pl_list_dict['y']

    # calcualte x
    pl_list_dict['x'] = pl_list_dict['y'] + h2o_mass + 12
    ph_list_dict['x'] = pl_list_dict['x']

    # calculate x-H2O
    pl_list_dict['x-H2O'] = pl_list_dict['x'] - h2o_mass
    ph_list_dict['x-H2O'] = pl_list_dict['x-H2O']

    # calculate x-NH3
    pl_list_dict['x-NH3'] = pl_list_dict['x'] - nh3_mass
    ph_list_dict['x-NH3'] = pl_list_dict['x-NH3']

    # calculate x++
    pl_list_dict['x++'] = (pl_list_dict['x'] + df_atom_mass.loc['H+']['mass']) / 2
    ph_list_dict['x++'] = pl_list_dict['x++']

    # calculate x++-H2O
    pl_list_dict['x++-H2O'] = pl_list_dict['x++'] - h2o_mass
    ph_list_dict['x++-H2O'] = pl_list_dict['x++-H2O']

    # calculate x++-NH3
    pl_list_dict['x++-NH3'] = pl_list_dict['x++'] - nh3_mass
    ph_list_dict['x++-NH3'] = pl_list_dict['x++-NH3']

    # calculate y-H2O
    pl_list_dict['y-H2O'] = pl_list_dict['y'] - h2o_mass
    ph_list_dict['y-H2O'] = pl_list_dict['y-H2O']

    # calculate y-NH3
    pl_list_dict['y-NH3'] = pl_list_dict['y'] - nh3_mass
    ph_list_dict['y-NH3'] = pl_list_dict['y-NH3']

    # calculate y++
    pl_list_dict['y++'] = (pl_list_dict['y'] + df_atom_mass.loc['H+']['mass']) / 2
    ph_list_dict['y++'] =  pl_list_dict['y++']

    # calculate y++-H2O
    pl_list_dict['y++-H2O'] = pl_list_dict['y++'] - h2o_mass
    ph_list_dict['y++-H2O'] = pl_list_dict['y++-H2O']

    # calculate y++-NH3
    pl_list_dict['y++-NH3'] = pl_list_dict['y++'] - nh3_mass
    ph_list_dict['y++-NH3'] = pl_list_dict['y++-NH3']

    # calculate z
    pl_list_dict['z'] = pl_list_dict['y'] - nh3_mass + df_atom_mass.loc['H+']['mass']
    ph_list_dict['z'] = pl_list_dict['z']

    # calculate z-H2O
    pl_list_dict['z-H2O'] = pl_list_dict['z'] - h2o_mass
    ph_list_dict['z-H2O'] = pl_list_dict['z-H2O']

    # calculate z-NH3
    pl_list_dict['z-NH3'] = pl_list_dict['z'] - nh3_mass
    ph_list_dict['z-NH3'] =pl_list_dict['z-NH3']

    # calculate z++
    pl_list_dict['z++'] = (pl_list_dict['z'] + df_atom_mass.loc['H+']['mass']) / 2
    ph_list_dict['z++'] = pl_list_dict['z++']

    # calculate z++-H2O
    pl_list_dict['z++-H2O'] = pl_list_dict['z++'] - h2o_mass
    ph_list_dict['z++-H2O'] = pl_list_dict['z++-H2O']

    # calculate z++-NH3
    pl_list_dict['z++-NH3'] = pl_list_dict['z++'] - nh3_mass
    ph_list_dict['z++-NH3'] = pl_list_dict['z++-NH3']

    return partition_options, charge_options, pl_list_dict, ph_list_dict

    # print("bl_mass_list:", bl_mass_list)
    # print("yl_mass_list:", yl_mass_list)

    # return partition_options, charge_options, bl_mass_list, yl_mass_list
    

# @callback(
#     Output('graph_ms2l', 'figure'),
#     Output('found_idxl_list_dict', 'data'),
#     # Input('bl_mass_list', 'data'),
#     # Input('yl_mass_list', 'data'),
#     Input('pl_list_dict', 'data'),
#     Input('ms2l','value'),
#     Input('mz_error_margin', 'value')
# )
# def gen_ms2l_fig(p_list_dict, ms2_fn, ppm):
#     """generate the figure of ms2L

#     Returns
#     -------
#     p_list_dict : dict of list
#         dict of calculated ions list of peptite.L
#     ms2l_fn: str
#         The path of the selected ms2L excel file
#     ppm : float
#         The selected mz error margin (ppm)

#     Returns
#     -------
#     fig: px figure
#         The MS2L mz-intensity figure
#     """

#     if p_list_dict is None or ms2_fn is None or ppm is None:
#         return dash.no_update, dash.no_update
    
#     b_mass_list = p_list_dict['b']
#     y_mass_list = p_list_dict['y']
#     fp = ms2_fn
#     ppm = float(ppm)
#     b_delta_list = np.array([ppm * x / 1e6 for x in b_mass_list])
#     y_delta_list = np.array([ppm * x / 1e6 for x in y_mass_list])
#     df = pd.read_excel(fp, sheet_name=0)
#     fig = px.scatter(df, x='fragmz', y='int')
#     found_idx_list_dict = defaultdict(list) # record the found calculated ions index (ions type : the list of found ions indices)
#     for x, y in zip(df['fragmz'], df['int']):

#         flag_by = False # True if x is in b_mass_list or y_mass_list
#         for i in range(len(b_mass_list)):
#             # check if x is b mass 
#             if abs(b_mass_list[i] - x) <= b_delta_list[i]:
#                 fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="LightSeaGreen",width=3))
#                 flag_by = True
#                 # record the found calculated ions index
#                 found_idx_list_dict['b'].append(i)
#                 break
#             # check if x is y mass 
#             elif abs(y_mass_list[i] - x) <= y_delta_list[i]:
#                 fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="Red",width=3))
#                 flag_by = True
#                 # record the found calculated ions index
#                 found_idx_list_dict['y'].append(i)
#                 break
        
#         if not flag_by:
#             fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="RoyalBlue",width=3))

#     return fig, found_idx_list_dict

@callback(
    Output('ms2_ion_type_checklist', 'value'),
    # Output("ms2_ion_type_button_all", 'n_clicks'),
    # Output('ms2_ion_type_button_reset', 'n_clicks'),
    [Input("ms2_ion_type_button_all", 'n_clicks'),
    Input('ms2_ion_type_button_reset', 'n_clicks')],
    prevent_initial_call=True,
)
def ms2_ion_checklist_all(ion_type_button_all_click, ion_type_button_reset_click):
    """selct all or clear the ms2_ion_type_checklist values

    Parameters
    ----------
    ion_type_button_all_click : int
        number of ion_type_button_all_click
    ion_type_button_reset_click : int
        number of ion_type_button_reset_click

    Returns
    -------
    ms2_ion_type_checklist: dcc.Dropdown.value
        The value of ms2_ion_type_checklist
    """

    # if ion_type_button_all_click == 0 or ion_type_button_reset_click == 0:
    #     return dash.no_update
    
    ctx = dash.callback_context
    button_id = ctx.triggered_id
    
    if "ms2_ion_type_button_all" in button_id:
        ion_type_checklist_value = [x for x in df_ions_color['ions_type'] if x != 'Seq.']
        return ion_type_checklist_value
    
    elif "ms2_ion_type_button_reset" in button_id:
        return []
    
    else:
        return dash.no_update



# @callback(
#     Output('ms2_ion_type_checklist', 'value'),
#     Input('ms2_ion_type_button_reset', 'n_clicks'),
#     prevent_initial_call=True
# )
# def ms2_ion_checklist_reset(ion_type_button_reset_click):
#     """clear the ms2_ion_type_checklist values

#     Parameters
#     ----------
#     ion_type_button_reset_click : int
#         number of ion_type_button_reset_click

#     Returns
#     -------
#     ms2_ion_type_checklist: dcc.Dropdown.value
#         The value of ms2_ion_type_checklist
#     """
#     if ion_type_button_reset_click == 0:
#         return dash.no_update
    
#     return None


@callback(
    Output('graph_ms2l', 'figure'),
    Output('found_idxl_list_dict', 'data'),
    # Input('bl_mass_list', 'data'),
    # Input('yl_mass_list', 'data'),
    Input('pl_list_dict', 'data'),
    Input('ms2l','value'),
    Input('mz_error_margin', 'value'),
    Input('ms2_ion_type_button', 'n_clicks'),
    State('ms2_ion_type_checklist', 'value')
    # Input('ms2_ion_type_checklist', 'value')
)
def gen_ms2l_fig(p_list_dict, ms2_fn, ppm, ion_button_click, ions_type_list):
    """generate the figure of ms2L

    Returns
    -------
    p_list_dict : list
        dict of calculated ions list of peptite.L
    ms2l_fn: str
        The path of the selected ms2L excel file
    ppm : float
        The selected mz error margin (ppm)
    ions_type_list : list
        The list of selected ions type

    Returns
    -------
    fig: px figure
        The MS2L mz-intensity figure
    """
    # print("ion_button_click", ion_button_click)

    if p_list_dict is None or ms2_fn is None or ppm is None or ions_type_list is None or ion_button_click == 0:
        return dash.no_update, dash.no_update
    
    # b_mass_list = p_list_dict['b']
    # y_mass_list = p_list_dict['y']
    # fp = ms2_fn
    # ppm = float(ppm)
    # b_delta_list = np.array([ppm * x / 1e6 for x in b_mass_list])
    # y_delta_list = np.array([ppm * x / 1e6 for x in y_mass_list])
    # df = pd.read_excel(fp, sheet_name=0)
    # fig = px.scatter(df, x='fragmz', y='int')
    # found_idx_list_dict = defaultdict(list) # record the found calculated ions index (ions type : the list of found ions indices)
    # for x, y in zip(df['fragmz'], df['int']):

    #     flag_by = False # True if x is in b_mass_list or y_mass_list
    #     for i in range(len(b_mass_list)):
    #         # check if x is b mass 
    #         if abs(b_mass_list[i] - x) <= b_delta_list[i]:
    #             fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="LightSeaGreen",width=3))
    #             flag_by = True
    #             # record the found calculated ions index
    #             found_idx_list_dict['b'].append(i)
    #             break
    #         # check if x is y mass 
    #         elif abs(y_mass_list[i] - x) <= y_delta_list[i]:
    #             fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="Red",width=3))
    #             flag_by = True
    #             # record the found calculated ions index
    #             found_idx_list_dict['y'].append(i)
    #             break
        
    #     if not flag_by:
    #         fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="RoyalBlue",width=3))
    
    # create a rainbow color map
    colormap = ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, len(ions_type_list))]
    
    fp = ms2_fn
    ppm = float(ppm)
    df = pd.read_excel(fp, sheet_name=0)
    fig = px.scatter(df, x='fragmz', y='int')
    found_idx_list_dict = defaultdict(list) # record the found calculated ions index (ions type : the list of found ions indices)
    # display all the scans first
    for x, y in zip(df['fragmz'], df['int']):
        fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="grey",width=3))
    
    fragmz_arr = np.array(df['fragmz'])
    int_arr = np.array(df['int'])
    # for ions_name in p_list_dict.keys():
    for ions_name in ions_type_list:
        p_mass_arr = p_list_dict[ions_name]
        # p_delta_arr = ppm * p_mass_arr / 1e6
        p_delta_arr = np.array([ppm * x / 1e6 for x in p_mass_arr])

        # process ions independent from r_seq elements
        # prevent annotation are added repeatedly for the ions independent from r_seq elements
        if ions_name in {'MH+', 'MH++', 'MH+++', 'MH-H2O(+)', 'MH-H2O(++)', 'MH-H2O(+++)', 'MH-NH3(+)', 'MH-NH3(++)', 'MH-NH3(+++)'}:
            # for i, p_mass in enumerate(p_mass_arr):
            p_mass = p_mass_arr[0]
            p_mass_idx_arr = np.where(abs(p_mass - fragmz_arr) <= p_delta_arr[0])[0]
            # record the p_mass if it is found
            if len(p_mass_idx_arr):
                p_mass_idx = p_mass_idx_arr[0]
                x = fragmz_arr[p_mass_idx]
                y = int_arr[p_mass_idx]
                # record the found calculated ions index
                # found_idx_list_dict[ions_name].append(i)
                found_idx_list_dict[ions_name] = list(range(len(p_mass_arr)))
                fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color=df_ions_color.loc[ions_name]['color'],width=3))

                # add anotation for each found calculated ions
                fig.add_annotation(
                    x = x,
                    y = y,
                    text=ions_name,
                    showarrow=False,
                    yshift=10,
                    font=dict(color=df_ions_color.loc[ions_name]['color']),
                )
        # process ions dependent on the r_seq elements
        else:
            for i, p_mass in enumerate(p_mass_arr):
                p_mass_idx_arr = np.where(abs(p_mass - fragmz_arr) <= p_delta_arr[i])[0]
                # record the p_mass if it is found
                if len(p_mass_idx_arr):
                    p_mass_idx = p_mass_idx_arr[0]
                    x = fragmz_arr[p_mass_idx]
                    y = int_arr[p_mass_idx]
                    # record the found calculated ions index
                    found_idx_list_dict[ions_name].append(i)
                    fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color=df_ions_color.loc[ions_name]['color'],width=3))

                    # add annotation for each found calculated ions
                    fig.add_annotation(
                        x = x,
                        y = y,
                        text=ions_name+str(i),
                        showarrow=False,
                        yshift=10,
                        font=dict(color=df_ions_color.loc[ions_name]['color']),
                    )
    
    fig.update_layout(
        font_family="arial",
        xaxis_title="mz",
        yaxis_title="Intensity",
        title={
            'text': "MS2L Figure",
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        plot_bgcolor = 'white',
    )

    fig.update_xaxes(
        title_font = {"size": 16},
        ticks = 'inside',
        # showline=True,
        linecolor='black',
        gridcolor='lightgrey',
    )

    fig.update_yaxes(
        title_font = {"size": 16},
        ticks = 'inside',
        # showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        zeroline = True,
        zerolinecolor = 'lightgrey',
    )

    return fig, found_idx_list_dict

@callback(
    Output('ms2l_calInos_tab', 'data'),
    Output('ms2l_calInos_tab', 'columns'),
    Output('ms2l_calInos_tab', 'style_data_conditional'),
    # Input('third_level', 'value'),
    Input('sequence', 'value'),
    Input('pl_list_dict', 'data'),
    Input('found_idxl_list_dict', 'data'),
    Input('ms2_ion_type_button', 'n_clicks'),
    # Input('ms2_ion_type_checklist', 'value')
    State('ms2_ion_type_checklist', 'value')
)
def gen_ms2l_ions_tab(r_seq, p_list_dict, found_idx_list_dict, ion_button_click, ions_type_list):
    """genrate the MS2 inon table for peptide.L

    Parameters
    ----------
    r_seq : dcc.Dropdown.value
        selected R sequence
    p_list_dict : dict of list
        dict of calculated ions list of peptite.L
    found_idx_list_dict : dict of list
        dict of found calulcated ions idx list
    ions_type_list : list
        The selected ions type

    Returns
    -------
    tab_data : data of table
        data of the table
    tab_col : column header of table
        column header of table
    style_data_dict_list : list of dict
        list of formating style dict to highlight found ion masses
    """
    if p_list_dict is None or r_seq is None or ions_type_list is None or ion_button_click == 0:
        return dash.no_update, dash.no_update, dash.no_update

    # round the numbers of each ions to be displayed
    pr_list_dict = {}
    # for elem in p_list_dict.keys():
    for elem in ions_type_list:
        if 'x' in elem or 'y' in elem or 'z' in elem:
            pr_list_dict[elem] = np.flip(np.round(p_list_dict[elem], 4))
        else:
            pr_list_dict[elem] = np.round(p_list_dict[elem], 4)
    
    # add R_Seq to pr_list_dict
    # fd_name = curLevel_val.split('/')[-1]
    # r_seq = df_web_info.loc[fd_name]['R_sequence']
    pr_list_dict['Seq.'] = [x for x in r_seq]

    # create a pandas dataframe for ions dict
    df = pd.DataFrame(pr_list_dict)

    # reorder columns to make table columns displayed in the order of df_ions_color['ions_type']
    col_order_lst = [x for x in df_ions_color['ions_type'] if x in pr_list_dict]
    df = df[col_order_lst]
    
    # process dataframe in the format of dash_table data
    tab_data = df.to_dict('records')
    tab_col = [{"name": i, "id": i} for i in df.columns]

    # create the hightlight format scheme to highlight the found calculated masses
    # style_data_dict_list = [{'if': {'row_index': 1, 'column_id': 'b'}, 'color': 'red'}]
    style_data_dict_list = []
    if found_idx_list_dict:
        for elem in found_idx_list_dict.keys():
            found_idx_list = found_idx_list_dict[elem]
            if 'a' in elem or 'b' in elem or 'c' in elem:
                for idx in found_idx_list:
                    style_data_dict = {'if': {'row_index': idx, 'column_id': elem}, 'color': 'red'}
                    style_data_dict_list.append(style_data_dict)
            else:
                for idx in found_idx_list:
                    style_data_dict = {'if': {'row_index': len(p_list_dict[elem]) - idx - 1, 'column_id': elem}, 'color': 'red'}
                    style_data_dict_list.append(style_data_dict)
                

    return tab_data, tab_col, style_data_dict_list

@callback(
    Output('graph_ms2h', 'figure'),
    Output('found_idxh_list_dict', 'data'),
    # Input('bl_mass_list', 'data'),
    # Input('yl_mass_list', 'data'),
    Input('ph_list_dict', 'data'),
    Input('ms2h','value'),
    Input('mz_error_margin', 'value'),
    Input('ms2_ion_type_button', 'n_clicks'),
    # Input('ms2_ion_type_checklist', 'value')
    State('ms2_ion_type_checklist', 'value')
)
def gen_ms2h_fig(p_list_dict, ms2_fn, ppm, ion_button_click, ions_type_list):
    """generate the figure of ms2H

    Returns
    -------
    p_list_dict : list
        dict of calculated ions list of peptite.H
    ms2_fn: str
        The path of the selected ms2H excel file
    ppm : float
        The selected mz error margin (ppm)
    ions_type_list : list
        The list of selected ions type

    Returns
    -------
    fig: px figure
        The MS2L mz-intensity figure
    """

    if p_list_dict is None or ms2_fn is None or ppm is None or ions_type_list is None or ion_button_click == 0:
        return dash.no_update, dash.no_update
    
    # b_mass_list = p_list_dict['b']
    # y_mass_list = p_list_dict['y']
    # fp = ms2_fn
    # ppm = float(ppm)
    # b_delta_list = np.array([ppm * x / 1e6 for x in b_mass_list])
    # y_delta_list = np.array([ppm * x / 1e6 for x in y_mass_list])
    # df = pd.read_excel(fp, sheet_name=0)
    # fig = px.scatter(df, x='fragmz', y='int')
    # found_idx_list_dict = defaultdict(list) # record the found calculated ions index (ions type : the list of found ions indices)
    # for x, y in zip(df['fragmz'], df['int']):

    #     flag_by = False # True if x is in b_mass_list or y_mass_list
    #     for i in range(len(b_mass_list)):
    #         # check if x is b mass 
    #         if abs(b_mass_list[i] - x) <= b_delta_list[i]:
    #             fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="LightSeaGreen",width=3))
    #             flag_by = True
    #             # record the found calculated ions index
    #             found_idx_list_dict['b'].append(i)
    #             break
    #         # check if x is y mass 
    #         elif abs(y_mass_list[i] - x) <= y_delta_list[i]:
    #             fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="Red",width=3))
    #             flag_by = True
    #             # record the found calculated ions index
    #             found_idx_list_dict['y'].append(i)
    #             break
        
    #     if not flag_by:
    #         fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="RoyalBlue",width=3))
    
    
    fp = ms2_fn
    ppm = float(ppm)
    df = pd.read_excel(fp, sheet_name=0)
    fig = px.scatter(df, x='fragmz', y='int')
    found_idx_list_dict = defaultdict(list) # record the found calculated ions index (ions type : the list of found ions indices)
    # display all the scans first
    for x, y in zip(df['fragmz'], df['int']):
        fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="grey",width=3))
    
    fragmz_arr = np.array(df['fragmz'])
    int_arr = np.array(df['int'])
    # for ions_name in p_list_dict.keys():
    for ions_name in ions_type_list:
        p_mass_arr = p_list_dict[ions_name]
        # p_delta_arr = ppm * p_mass_arr / 1e6
        p_delta_arr = np.array([ppm * x / 1e6 for x in p_mass_arr])

        # process ions independent from r_seq elements
        # prevent annotation are added repeatedly for the ions independent from r_seq elements
        if ions_name in {'MH+', 'MH++', 'MH+++', 'MH-H2O(+)', 'MH-H2O(++)', 'MH-H2O(+++)', 'MH-NH3(+)', 'MH-NH3(++)', 'MH-NH3(+++)'}:
            # for i, p_mass in enumerate(p_mass_arr):
            p_mass = p_mass_arr[0]
            p_mass_idx_arr = np.where(abs(p_mass - fragmz_arr) <= p_delta_arr[0])[0]
            # record the p_mass if it is found
            if len(p_mass_idx_arr):
                p_mass_idx = p_mass_idx_arr[0]
                x = fragmz_arr[p_mass_idx]
                y = int_arr[p_mass_idx]
                # record the found calculated ions index
                # found_idx_list_dict[ions_name].append(i)
                found_idx_list_dict[ions_name] = list(range(len(p_mass_arr)))
                fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color=df_ions_color.loc[ions_name]['color'],width=3))

                # add anotation for each found calculated ions
                fig.add_annotation(
                    x = x,
                    y = y,
                    text=ions_name,
                    showarrow=False,
                    yshift=10,
                    font=dict(color=df_ions_color.loc[ions_name]['color']),
                )
        # process ions dependent on the r_seq elements
        else:
            for i, p_mass in enumerate(p_mass_arr):
                p_mass_idx_arr = np.where(abs(p_mass - fragmz_arr) <= p_delta_arr[i])[0]
                # record the p_mass if it is found
                if len(p_mass_idx_arr):
                    p_mass_idx = p_mass_idx_arr[0]
                    x = fragmz_arr[p_mass_idx]
                    y = int_arr[p_mass_idx]
                    # record the found calculated ions index
                    found_idx_list_dict[ions_name].append(i)
                    fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color=df_ions_color.loc[ions_name]['color'],width=3))

                    # add annotation for each found calculated ions
                    fig.add_annotation(
                        x = x,
                        y = y,
                        text=ions_name+str(i),
                        showarrow=False,
                        yshift=10,
                        font=dict(color=df_ions_color.loc[ions_name]['color']),
                    )

    fig.update_layout(
        font_family="arial",
        xaxis_title="mz",
        yaxis_title="Intensity",
        title={
            'text': "MS2H Figure",
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        plot_bgcolor = 'white',
    )

    fig.update_xaxes(
        title_font = {"size": 16},
        ticks = 'inside',
        # showline=True,
        linecolor='black',
        gridcolor='lightgrey',
    )

    fig.update_yaxes(
        title_font = {"size": 16},
        ticks = 'inside',
        # showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        zeroline = True,
        zerolinecolor = 'lightgrey',
    )


    return fig, found_idx_list_dict

@callback(
    Output('ms2h_calInos_tab', 'data'),
    Output('ms2h_calInos_tab', 'columns'),
    Output('ms2h_calInos_tab', 'style_data_conditional'),
    # Input('third_level', 'value'),
    Input('sequence', 'value'),
    Input('ph_list_dict', 'data'),
    Input('found_idxh_list_dict', 'data'),
    Input('ms2_ion_type_button', 'n_clicks'),
    # Input('ms2_ion_type_checklist', 'value')
    State('ms2_ion_type_checklist', 'value')
)
def gen_ms2h_ions_tab(r_seq, p_list_dict, found_idx_list_dict, ion_button_click, ions_type_list):
    """genrate the MS2 inon table for peptide.L

    Parameters
    ----------
    r_seq : str
        R Sequence
    p_list_dict : dict of list
        dict of calculated ions list of peptite.L
    found_idx_list_dict : dict of list
        dict of found calulcated ions idx list
    ions_type_list : list
        The selected ions type

    Returns
    -------
    tab_data : data of table
        data of the table
    tab_col : column header of table
        column header of table
    style_data_dict_list : list of dict
        list of formating style dict to highlight found ion masses
    """
    if p_list_dict is None or r_seq is None or ions_type_list is None or ion_button_click == 0:
        return dash.no_update, dash.no_update, dash.no_update

    # round the numbers of each ions to be displayed
    pr_list_dict = {}
    # for elem in p_list_dict.keys():
    for elem in ions_type_list:
        if 'x' in elem or 'y' in elem or 'z' in elem:
            pr_list_dict[elem] = np.flip(np.round(p_list_dict[elem], 4))
        else:
            pr_list_dict[elem] = np.round(p_list_dict[elem], 4)
    
    # add R_Seq to pr_list_dict
    # fd_name = curLevel_val.split('/')[-1]
    # r_seq = df_web_info.loc[fd_name]['R_sequence']
    pr_list_dict['Seq.'] = [x for x in r_seq]

    # create a pandas dataframe for ions dict
    df = pd.DataFrame(pr_list_dict)

    # reorder columns to make table columns displayed in the order of df_ions_color['ions_type']
    col_order_lst = [x for x in df_ions_color['ions_type'] if x in pr_list_dict]
    df = df[col_order_lst]
    
    # process dataframe in the format of dash_table data
    tab_data = df.to_dict('records')
    tab_col = [{"name": i, "id": i} for i in df.columns]

    # create the hightlight format scheme to highlight the found calculated masses
    # style_data_dict_list = [{'if': {'row_index': 1, 'column_id': 'b'}, 'color': 'red'}]
    style_data_dict_list = []
    if found_idx_list_dict:
        for elem in found_idx_list_dict.keys():
            found_idx_list = found_idx_list_dict[elem]
            if 'a' in elem or 'b' in elem or 'c' in elem:
                for idx in found_idx_list:
                    style_data_dict = {'if': {'row_index': idx, 'column_id': elem}, 'color': 'red'}
                    style_data_dict_list.append(style_data_dict)
            else:
                for idx in found_idx_list:
                    style_data_dict = {'if': {'row_index': len(p_list_dict[elem]) - idx - 1, 'column_id': elem}, 'color': 'red'}
                    style_data_dict_list.append(style_data_dict)
                

    return tab_data, tab_col, style_data_dict_list

@callback(
    Output('forth_level', 'options'),
    Output('ms1_mass_list', 'data'),
    Output('ms2l', 'options'),
    Output('ms2h', 'options'),
    Input('partition', 'value'),
    Input('charge', 'value'),
    Input('sequence', 'value'),
    Input('third_level', 'value'),
    Input('second_level', 'value'),
    prevent_initial_call=True
)
def gen_forth_level(partition, z, r_seq, protein, sample_path):
    """Generated the forth level (ms1_, ms2H_, ms2L_ excel lists) based on the selected r_seq, partition and charge

    Parameters
    ----------
    partition : str
        The selected partition (full name)
    z : int
        The selected charge
    r_seq : str
        Selected R sequence
    sample_path : str
        path of sample folder

    Returns
    -------
    nextLevel_options : dcc.Dropdown.options
        The options of ms1_, ms2H_, ms2L_ excel dropdown
    """

    if partition is None or z is None or r_seq is None or protein is None or sample_path is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # generate R sequence
    # fd_name = curLevel_val.split('/')[-1]
    # r_seq = df_web_info.loc[fd_name]['R_sequence']
    # # print(type(partition), type(str(z)), type(r_seq))
    # nextLevel_path = curLevel_val + '/' + fd_name + '_' + partition + '_' + str(z) + '_' + r_seq
    nextLevel_path = sample_path + '/' + partition + '_' + str(z) + '_' + r_seq

    # generate forth-level options
    fp = nextLevel_path # the (relative) path of the xlsx file
    # unsorted:
    # nextLevel_options_ms1 = {fp + "/" + x : '.'.join(x.split('_')[-1].split('.')[0:2]) for x in os.listdir(fp) if x.split('_')[0] == 'ms1'}
    # sorted:
    ms1_rt_list = [float('.'.join(x.split('_')[-1].split('.')[0:2])) for x in os.listdir(fp) if x.split('_')[0] == 'ms1']
    ms1_rt_list.sort()
    # print("ms1_rt_list", ms1_rt_list)
    nextLevel_options_ms1 = {fp + "/" + 'ms1_' + partition + '_' + str(z) + '_' + r_seq + '_' + str(x) + '.xlsx' : x for x in ms1_rt_list}

    # generate the 12 target ms1 masses
    ms1_mass_list = []
    # fd_name = curLevel_val.split('/')[-1]
    # calculatedmass = float(df_web_info.loc[fd_name]['Calcmass.y'])
    species = sample_path.split('/')[-2]
    sample = sample_path.split('/')[-1]
    calculatedmass = float(web_info_dict["-".join([species, sample])][protein][r_seq]["calcmy"])
    z = int(z)
    m = (calculatedmass - 1.00728 + z*1.00728)/z
    diff = 10.008269
    
    ms1_mass_list += [m + i * 1.00335 / z for i in range(6)] # pair 1 ms1 masses
    ms1_mass_list += [m + diff / z + i * 1.00335 / z for i in range(6)] # pair 2 ms1 masses

    # print("ms1_mass_list", ms1_mass_list)

    # generate the ms2L scan number options
    # unsorted:
    # ms2lScanNum_options = {fp + '/' + x : x.split('_')[-1].split('.')[0] for x in os.listdir(fp) if x.split('_')[0] == 'ms2L'}
    # sorted:
    ms2l_scanNum_list = [int(x.split('_')[-1].split('.')[0]) for x in os.listdir(fp) if x.split('_')[0] == 'ms2L']
    ms2l_scanNum_list.sort()
    ms2lScanNum_options = {fp + "/" + 'ms2L_' + partition + '_' + str(z) + '_' + r_seq + '_' + str(x) + '.xlsx' : x for x in ms2l_scanNum_list}

    # generate the ms2H scan number options
    # unsorted:
    # ms2hScanNum_options = {fp + '/' + x : x.split('_')[-1].split('.')[0] for x in os.listdir(fp) if x.split('_')[0] == 'ms2H'}
    # sorted:
    ms2h_scanNum_list = [int(x.split('_')[-1].split('.')[0]) for x in os.listdir(fp) if x.split('_')[0] == 'ms2H']
    ms2h_scanNum_list.sort()
    ms2hScanNum_options = {fp + "/" + 'ms2H_' + partition + '_' + str(z) + '_' + r_seq + '_' + str(x) + '.xlsx' : x for x in ms2h_scanNum_list}

    return nextLevel_options_ms1, ms1_mass_list, ms2lScanNum_options, ms2hScanNum_options

# @callback(
#     Output('graph_ms1_summary', 'figure'),
#     Input('forth_level', 'options'),
#     Input('ms1_mass_list', 'data'),
#     Input('mz_error_margin_ms1', 'value')
# )
# def gen_ms1_summary_fig(options_ms1, ms1_mass_list, ppm):
#     """generate MS1 summary figure

#     Parameters
#     ----------
#     options_ms1 : dcc.Dropdown.options
#         The options/dict of MS1 excel (path_to_excel : RT)
#     ms1_mass_list : dcc.Store.data (i.e., list)
#         The list of target MS1 masses
#     ppm : float
#         The selected mz error margin (ppm)
    
#     Returns
#     -------
#     fig: px figure
#         The MS1 summary figure
#     """
#     if options_ms1 is None or ms1_mass_list is None or ppm is None:
#         return dash.no_update
    
#     ms1_delta_list = [ppm * x / 1e6 for x in ms1_mass_list] # the list of ms1 delta
#     ppm = float(ppm)

#     rst_mz_list = []
#     rst_inten_list = []

#     for ms1_fn in options_ms1.keys():
#         pd_ms1 = pd.read_excel(ms1_fn, sheet_name=0)
#         mz_array = np.array(pd_ms1["mz"])
#         inten_array = np.array(pd_ms1["int"])

#         tmp_mz_list = []
#         tmp_inten_list = []

#         # search all the target ms1 masses in a single ms1_ excel file
#         for i in range(len(ms1_mass_list)):
#             mz_idx_array = np.where(abs(ms1_mass_list[i] - mz_array) <= ms1_delta_list[i])[0]

#             if len(mz_idx_array) != 0:
#                 rst_mz = mz_array[mz_idx_array[0]]
#                 rst_inten = inten_array[mz_idx_array[0]]

#                 tmp_mz_list.append(rst_mz)
#                 tmp_inten_list.append(rst_inten)

#                 # print("len(mz_idx_array)", len(mz_idx_array))
#                 # print("mz_idx_array", mz_idx_array)
#                 # print("rst_mz", rst_mz, type(rst_mz))
#                 # print("rst_inten", rst_inten, type(rst_inten))
        
#         if tmp_inten_list:
#             rst_mz_list += tmp_mz_list
#             inten_0 = tmp_inten_list[0]
#             rst_inten_list += [x / inten_0 for x in tmp_inten_list]
#         else:
#             return None
    
#     # print("rst_mz_list:", rst_mz_list)
#     # print("rst_inten_list:", rst_inten_list)

#     fig = px.scatter(x=rst_mz_list, y=rst_inten_list)

#     fig.update_layout(
#         font_family="arial",
#         xaxis_title="mz",
#         yaxis_title="Intensity Ratio",
#         title={
#             'text': "MS1 Summary",
#             'x':0.5,
#             'xanchor': 'center',
#             'yanchor': 'top'
#         },
#     )

#     fig.update_xaxes(
#         title_font = {"size": 16}
#     )

#     fig.update_yaxes(
#         title_font = {"size": 16}
#     )

#     return fig

@callback(
    Output('graph_ms1_summary', 'figure'),
    Input('forth_level', 'options'),
    Input('ms1_mass_list', 'data'),
    Input('mz_error_margin_ms1', 'value')
)
def gen_ms1_summary_fig(options_ms1, ms1_mass_list, ppm):
    """generate MS1 summary figure

    Parameters
    ----------
    options_ms1 : dcc.Dropdown.options
        The options/dict of MS1 excel (path_to_excel : RT)
    ms1_mass_list : dcc.Store.data (i.e., list)
        The list of target MS1 masses
    ppm : float
        The selected mz error margin (ppm)
    
    Returns
    -------
    fig: px figure
        The MS1 summary figure
    """
    if options_ms1 is None or ms1_mass_list is None or ppm is None:
        return dash.no_update
    
    ms1_delta_list = [ppm * x / 1e6 for x in ms1_mass_list] # the list of ms1 delta
    ppm = float(ppm)

    # rst_mz_list = []
    # rst_inten_list = []
    rst_mz_inten_dict = defaultdict(list) # dict of ratioed mz_list and intensity_list

    for ms1_fn in options_ms1.keys():
        pd_ms1 = pd.read_excel(ms1_fn, sheet_name=0)
        mz_array = np.array(pd_ms1["mz"])
        inten_array = np.array(pd_ms1["int"])

        tmp_mz_list = []
        tmp_inten_list = []

        # search all the target ms1 masses in a single ms1_ excel file
        for i in range(len(ms1_mass_list)):
            mz_idx_array = np.where(abs(ms1_mass_list[i] - mz_array) <= ms1_delta_list[i])[0]

            if len(mz_idx_array) != 0:
                rst_mz = ms1_mass_list[i]
                rst_inten = inten_array[mz_idx_array[0]]

                tmp_mz_list.append(rst_mz)
                tmp_inten_list.append(rst_inten)

                # print("len(mz_idx_array)", len(mz_idx_array))
                # print("mz_idx_array", mz_idx_array)
                # print("rst_mz", rst_mz, type(rst_mz))
                # print("rst_inten", rst_inten, type(rst_inten))
        
        if tmp_inten_list:
            # rst_mz_list += tmp_mz_list
            # inten_0 = tmp_inten_list[0]
            # rst_inten_list += [x / inten_0 for x in tmp_inten_list]

            rst_mz_inten_dict['mz'] += tmp_mz_list
            inten_0 = tmp_inten_list[0]
            rst_mz_inten_dict['inten'] += [x / inten_0 for x in tmp_inten_list]
    
    # print("rst_mz_list:", rst_mz_list)
    # print("rst_inten_list:", rst_inten_list)
    if rst_mz_inten_dict:
        fig = px.box(rst_mz_inten_dict, x='mz', y='inten', points="outliers", color='mz')
        
        # add points which overlapps with the boxes
        point_trace = px.scatter(rst_mz_inten_dict, x="mz", y="inten").data[0]
        point_trace.marker.update(size=6, opacity=0.1, color='grey')

        # add a horizontal line at y=1
        fig.add_trace(point_trace)
        fig.add_hline(y=1, line_width=1.5, line_dash="dash", line_color="red")

        fig.update_layout(
            font_family="arial",
            xaxis_title="mz",
            yaxis_title="Intensity Ratio",
            title={
                'text': "MS1 Summary",
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            plot_bgcolor = 'white',
        )

        fig.update_xaxes(
            title_font = {"size": 16},
            ticks = 'inside',
            # showline=True,
            linecolor='black',
            gridcolor='lightgrey',
        )

        fig.update_yaxes(
            title_font = {"size": 16},
            ticks = 'inside',
            linecolor='black',
            gridcolor='lightgrey',
            # zeroline = True,
            # zerolinecolor = 'lightgrey',
            range = [0, 2],
        )

        return fig
    else:
        return None



@callback(
    Output('graph_ms1', 'figure'),
    Input('forth_level', 'value'),
    Input('ms1_mass_list', 'data'),
    Input('mz_error_margin_ms1', 'value'),
    prevent_initial_call=True
)
def gen_ms1_fig(curLevel_val, ms1_mass_list, ppm):
    """genrate the MS1 mz-intensity figure based on the selected ms1_*** excel file

    Parameters
    ----------
    curLevel_val : dcc.Dropdown.value
        The path of the selected ms1 excel file (forth level)
    ms1_mass_list : dcc.Store.data (i.e., list)
        The list of target MS1 masses
    ppm : float
        The selected mz error margin (ppm)

    Returns
    -------
    fig: px figure
        The MS1 mz-intensity figure
    """
    if curLevel_val is None or ms1_mass_list is None or ppm is None:
        return dash.no_update
    
    fp = curLevel_val # the (relative) path of the xlsx file
    ms1_mass_pair1_list = ms1_mass_list[0:6]
    ms1_mass_pair2_list = ms1_mass_list[6:12]
    ppm = float(ppm)
    ms1_delta_pair1_list = [ppm * x / 1e6 for x in ms1_mass_pair1_list]
    ms1_delta_pair2_list = [ppm * x / 1e6 for x in ms1_mass_pair2_list]

    # generate the MS scan figure based on df
    df = pd.read_excel(fp, sheet_name=0) # read the first worksheet
    fig = px.scatter(df, x="mz", y="int")
    found_mz_list = [] # found mz in either pair 1 and pair 2
    found_inten_list = [] # found intensity in either pair 1 and pair 2
    for x, y in zip(df["mz"], df["int"]):
        # print(x, y)

        # check if mz is in pair 1
        if (any([abs(ms1_mass_pair1_list[i] - x) <= ms1_delta_pair1_list[i] for i in range(len(ms1_mass_pair1_list))])):
            fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="LightSeaGreen",width=3))
            found_mz_list.append(x)
            found_inten_list.append(y)
        # check if mz is in pair 2
        elif(any([abs(ms1_mass_pair2_list[i] - x) <= ms1_delta_pair2_list[i] for i in range(len(ms1_mass_pair2_list))])):
            fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="Red",width=3))
            found_mz_list.append(x)
            found_inten_list.append(y)
        else:
            fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color="grey",width=3))
    
    fig.update_layout(
        font_family="arial",
        xaxis_title="mz",
        yaxis_title="Intensity",
        title={
            'text': "MS1 Figure",
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        plot_bgcolor = 'white',
    )

    # calculate ranges of x-axis and y-axis
    if not found_mz_list or not found_inten_list:
        x_range = [None, None]
        y_range = [0, None]
    else:
        x_range = [min(found_mz_list)-1, max(found_mz_list)+1]
        y_range = [0, max(found_inten_list)*1.25]
        # add a horizontal line 
        fig.add_hline(y=found_inten_list[0], line_width=1.5, line_dash="dash", line_color="LightSeaGreen")

    fig.update_xaxes(
        title_font = {"size": 16},
        ticks = 'inside',
        # showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        range = x_range,
    )

    fig.update_yaxes(
        title_font = {"size": 16},
        ticks = 'inside',
        linecolor='black',
        gridcolor='lightgrey',
        zeroline = True,
        zerolinecolor = 'lightgrey',
        range= y_range,
    )

    return fig