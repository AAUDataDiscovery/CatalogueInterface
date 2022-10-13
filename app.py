import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
import dash
import yaml

from utils.component_initialiser import initialise

BASE_PATH = '/catalogue/'


class App:
    """
    The main application
    """

    def __init__(self, launch_config):
        self.app = dash.Dash(__name__,
                             suppress_callback_exceptions=True,
                             routes_pathname_prefix=BASE_PATH,
                             external_stylesheets=[dbc.themes.BOOTSTRAP]
                             )
        self.app.title = "Catalogue"
        self.server = self.app.server
        app_context = initialise(self.app, launch_config, BASE_PATH)
        navbar = app_context.components['navigation_bar']

        # Use the navbar as the launch layout for the app
        self.app.layout = html.Div([
            navbar.layout,
            dcc.Location(id='url', refresh=False),
            html.Div(id="page-content")
        ])

    def __call__(self, port=7245):
        """
        When the app instance is called, this will run
        """
        self.app.run_server(debug=True, port=port, dev_tools_hot_reload=True, use_reloader=True)


if __name__ == "__main__":
    launch_config = yaml.safe_load(open("launch_config.yaml"))
    app = App(launch_config)
    app()
