from scrape import get_data
from get_graph import get_elements , getG

import asyncio
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto



async def get_dash_data(channel_name , total_messages):
    texts_df , edge_df = await get_data(channel_name, total_messages)
    my_elements = get_elements(getG(edge_df))
    return my_elements


app = dash.Dash('Telegraph' , external_stylesheets=[dbc.themes.BOOTSTRAP])

input_groups = html.Div(
    [
        dbc.InputGroup(
            [
                dbc.InputGroupAddon("@", addon_type="prepend"),
                dbc.Input(id='input_channel_name' , placeholder="Username" , type='text')
            ],
        ),
        dbc.InputGroup(
            [
                dbc.Input(id='input_total_messages' , placeholder="Number of" , type='number'),
                dbc.InputGroupAddon("messages", addon_type="append")
            ],
        ),
        dbc.Button("Submit", outline=True, color="primary", type="submit" , style={"top":"1rem" , "position":"relative"})
    ]
)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}



sidebar = html.Div(
    [
        html.H2("Telegraph", className="Title"),
        html.Hr(),
        html.P(
            "Enter your querry data", className="lead"
        ),
        input_groups,
    ],
    style=SIDEBAR_STYLE,
)


app.layout = html.Div([
        
    cyto.Cytoscape(
        id='network-graph',
        elements = {},
        style={'width': '100%', 'height': '500'},
        layout={'name': 'preset'}
    ),
    sidebar
])

@app.callback(
    Output('network-graph', 'elements'),
    [Input('input_channel_name', 'value')],
    [Input('input_total_messages' , 'value')],
    prevent_initial_call=True
)

def update_graph(input_channel_name , input_total_messages):
    return asyncio.run(get_dash_data(input_channel_name , input_total_messages))


if __name__ == '__main__':
    app.run_server(debug=True)