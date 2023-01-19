from dash import dcc, html
from dash import Input, Output, State
from utils.component_decorators import component, page, callback
import dash_bootstrap_components as dbc


@component(name="data_input",
           children=[
               "data_generator",
               "data_uploader"
           ],
           required_data=["local_data_catalogue"])
class DataInputPage:
    def __init__(self, data_generator, data_uploader, data_catalogue):
        self.data_catalogue = data_catalogue
        self.datagen_tab = data_generator.layout
        self.data_uploader_tab = data_uploader.layout
        self.layout = dbc.Row([
            dbc.Col(
                dbc.Card(id="data-generation-directory-tree"), width=4, style={"height": "94vh", "overflow": "scroll"}
            ),
            dbc.Col([
                dbc.Tabs(
                    [
                        dbc.Tab(label="Data Generator", tab_id="data-curation-generator-tab"),
                        dbc.Tab(label="Data Uploader", tab_id="data-curation-uploader-tab")
                    ],
                    id="data-curation-tabs",
                    active_tab="data-curation-generator-tab"
                ),
                html.Div(id="data-curation-tab-content"),
            ]),
            html.Div(id="data-generation-stub", hidden=True)  # placeholder component as a required output
        ], className="g-0")

    @callback(
        Output("data-curation-tab-content", "children"),
        Input("data-curation-tabs", "active_tab")
    )
    def switch_curation_tab(self, current_tab):
        return {
            "data-curation-generator-tab": self.datagen_tab,
            "data-curation-uploader-tab": self.data_uploader_tab
        }.get(current_tab)

    @callback(
        Output("data-generation-directory-tree", 'children'),
        Input("data-generation-stub", 'value')
    )
    def build_directory_tree(self, _):
        return [
            html.Div(line.displayable())
            for line in self.data_catalogue.get_directory_tree()
        ]

    @page("datain", "Data Input")
    def return_page(self):
        return self.layout
