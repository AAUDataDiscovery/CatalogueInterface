from dash import html, dcc
from dash import Input, Output
import dash_bootstrap_components as dbc
from utils.component_decorators import component, callback


@component(name="filesystem_view", required_data=["local_data_catalogue"])
class FilesystemViewer:
    def __init__(self, data_catalogue):
        self.data_catalogue = data_catalogue
        self.layout = html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.Div(
                        id="catalogue-fileviewer-card"
                    )
                ])
            ]),
            dcc.Interval(id="catalogue-fileviewer-poll-update", interval=10*1000)
        ])

    def _build_filesystem_items(self):
        # self.data_catalogue.load_files()
        file_list = self.data_catalogue.get_loaded_files()
        return dbc.ListGroup([
            dbc.ListGroupItem(
                filename, n_clicks=0, action=True,
                id={
                    "type": "catalogue-fileviewer",
                    "index": filename
                }
            )
            for filename in sorted(file_list)
        ],
            flush=True
        )

    @callback(
        Output("catalogue-fileviewer-card", 'children'),
        Input("catalogue-fileviewer-poll-update", 'n_intervals')
    )
    def update_file_viewer(self, _):
        """
        Periodically update the loaded files
        """
        return self._build_filesystem_items()
