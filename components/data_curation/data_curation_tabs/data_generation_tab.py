from dash import dcc, html
from dash import Input, Output, State
from utils.component_decorators import component, page, callback
import dash_bootstrap_components as dbc


@component(name="data_generator", required_data=["local_data_generator"])
class DataGeneratorTab:
    def __init__(self, data_generator):
        self.data_generator = data_generator
        index_types = ['datetime', 'counter', 'categoric']
        self.layout = dbc.Card([
            dbc.Form([
                self._build_form_field(
                    "File Name",
                    dbc.Input(type="text", id="data-generation-file-name", placeholder="spam")
                ),
                self._build_form_field(
                    "Row Count",
                    dbc.Input(type="number", id="data-generation-row-count", placeholder="100")
                ),
                self._build_form_field(
                    "Index Type",
                    dbc.Select(
                        id="data-generation-index-type",
                        options=[{"label": index_type, "value": index_type} for index_type in index_types]
                    )
                ),
                self._build_form_field(
                    "Continuous Column Count",
                    dbc.Input(type="number", id="data-generation-continuous-column-count", placeholder="1")
                ),
                self._build_form_field(
                    "Categoric Column Count",
                    dbc.Input(type="number", id="data-generation-categoric-column-count", placeholder="1")
                ),
                self._build_form_field(
                    "File Spread",
                    dbc.Input(type="number", id="data-generation-file-spread", placeholder="1")
                )
            ]),
            dcc.Loading([
                dbc.Button("Generate", id="data-generation-generate-data", style={'width': '100%'})
            ])
        ], style={"padding": "10px"}
        )

    @staticmethod
    def _build_form_field(label, input_obj):
        """
        Row/label abstraction to help make the layout more DRY
        """
        return dbc.Row([
            dbc.Label(label, width=3),
            dbc.Col(input_obj, width=9)
        ], className="mb-3")

    @callback(
        Output("data-generation-stub", 'value'),
        Input("data-generation-generate-data", 'n_clicks'),
        State("data-generation-row-count", 'value'),
        State("data-generation-file-name", 'value'),
        State("data-generation-index-type", 'value'),
        State("data-generation-continuous-column-count", 'value'),
        State("data-generation-categoric-column-count", 'value'),
        State("data-generation-file-spread", 'value'),
        prevent_initial_call=True
    )
    def generate_data(self, n_clicks, *generation_arguments):
        if all(generation_arguments):
            self.data_generator.generate_fake_data(*generation_arguments)
