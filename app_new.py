import dash
from dash import Dash, dcc, html, Input, Output, callback, State, dash_table
# from dash.dependencies import State
import dash_bootstrap_components as dbc
from pages import home, protein, blankPage

app = dash.Dash(
    __name__,
    title="Arginylation",
    external_stylesheets=[dbc.icons.FONT_AWESOME],
    # assets_folder='assets',
    suppress_callback_exceptions=True
)

indexLayout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Create a "complete" layout for validating all callbacks. Otherwise when dash tries
# to validate them, most of them will thorw an error since they are linked to
# components that are not currently on the displayed page and so are not part of the 
# current layout
app.validation_layout = html.Div([
    indexLayout,
    home.layout,
    protein.layout
])


# This is the actual layout of the app
app.layout = indexLayout

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    # print('pathname:', pathname)
    if pathname == '/home' or pathname == '/':
        # print('jump to home page')
        return home.layout
    elif pathname == '/protein':
        # print('jump to protein page')
        return protein.layout
    else:
        return blankPage.layout

# This server object will be loaded by the WSGI script to be served as a webapp
# in a production server
server = app.server

# This will only be executed during debug when run locally, since WSGI does not 
# run this as __main__ but only takes the "server" variable
if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server()