import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, suppress_callback_exceptions=False, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

indices = ['SUBJECTKEY', 'EVENTNAME']
graph_types = ['Scatter', 'Bar']
scatter_graph_dimensions = {"x": "x",
                            "y": "y",
                            "color": "color (will drop NAs)",
                            "facet_col": "split horizontally",
                            "facet_row": "split vertically"}
bar_graph_dimensions = {"x": "x",
                        "split_by": "split by"}
default_marker_color = "crimson"
style_dict = {
        'width': '13%',
        'display': 'inline-block',
        'verticalAlign': "middle",
        'margin-right': '2em',
    }
