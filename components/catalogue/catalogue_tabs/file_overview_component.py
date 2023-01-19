import copy

import dash
from dash import html, dash_table, dcc
from dash import Input, Output, State, ctx, ALL
import dash_bootstrap_components as dbc

from discovery.metadata import NumericColMetadata
from utils.component_decorators import component, callback


@component(name="catalogue_file_overview", required_data=["local_data_catalogue"])
class CatalogueFileOverview:
    def __init__(self, catalogue_data):
        self.catalogue_data = catalogue_data

    @staticmethod
    def build_table_view(file_catalogue):
        """
        Create an overview for a given dataframe
        """
        file_data = file_catalogue.get_data()
        file_metadata = file_catalogue.get_metadata()
        data_head = file_data.head().to_dict('records')
        numeric_file_catalogue = [x for x in file_metadata.columns if isinstance(x, NumericColMetadata)]
        numeric_display_columns = ['name', 'mean', 'maximum', 'minimum']
        numeric_display_records = [{col_name: getattr(metadata, col_name) for col_name in numeric_display_columns} for
                                   metadata in numeric_file_catalogue]

        metadata_tags = copy.copy(file_metadata.tags)
        bonus_tags = {
            "val1": "first_val",
            "val2": "second_val",
            "val3": "third_val"
        }
        metadata_tags.update(bonus_tags)

        return html.Div([
            html.H2("Metadata Overview: "),
            html.Div(f"File size: {file_metadata.data_manifest['data_size']['no_of_bytes']} bytes"),
            html.Div(f"Row count: {file_metadata.data_manifest['data_size']['no_of_rows']}"),
            dash_table.DataTable(numeric_display_records),
            html.Hr(),
            html.H2("Metadata Tags: "),
            dbc.ListGroup(
                [
                    dbc.Row([
                        dbc.Col(dbc.ListGroupItem(tag_name, color="secondary"), width=4),
                        dbc.Col(dbc.Row([
                            dbc.Col(dbc.ListGroupItem(tag_value), width=11),
                            dbc.Col(dbc.Button("x", color="secondary"))
                        ], className='g-0')),
                    ], className='g-0')
                    for tag_name, tag_value in metadata_tags.items()
                ]
            ),
            html.Hr(),
            dbc.Row([
                dbc.Col(html.H2("Dataframe Head: "), width=4),
                dbc.Col([
                    dbc.Button("Download Dataframe", id='catalogue-download-button', color="secondary")
                ], width=4, className="d-grid gap-2")
            ], justify="between"),
            dash_table.DataTable(data_head)
        ])

    @callback(
        Output("download-catalogue-dataframe", "data"),
        Input("catalogue-download-button", 'n_clicks'),
        State("selected-catalogue-filename", 'data'),
        prevent_inital_call=True
    )
    def download_selected_dataframe(self, n_clicks, file_path):
        if n_clicks:
            file_data = self.catalogue_data.get_metadata_by_file(file_path).get_data()
            return dcc.send_data_frame(file_data.to_csv, file_path)
