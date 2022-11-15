import dash
from dash import html, dash_table, dcc
from dash import Input, Output, State, ctx, ALL
import dash_bootstrap_components as dbc
import pandas as pd

from discovery.utils.metadata.metadata import NumericColMetadata
from utils.component_decorators import component, callback


@component(name="catalogue_file_overview", required_data=["local_data_catalogue"])
class CatalogueFileOverview:
    def __init__(self, catalogue_data):
        self.catalogue_data = catalogue_data

    @staticmethod
    def build_table_view(file_data, file_metadata):
        """
        Create an overview for a given dataframe
        """
        data_head = file_data.head().to_dict('records')
        numeric_file_metadata = [x for x in file_metadata.columns if isinstance(x, NumericColMetadata)]
        numeric_display_columns = ['name', 'mean', 'maximum', 'minimum']
        numeric_display_records = [{col_name: getattr(metadata, col_name) for col_name in numeric_display_columns} for
                                   metadata in numeric_file_metadata]

        return html.Div([
            html.H2("Metadata Overview: "),
            html.Div(f"File size: {file_metadata.size[0]} {file_metadata.size[1].name}(s)"),
            html.Div(f"Row count: {file_data.shape[0]}"),
            dash_table.DataTable(numeric_display_records),
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
            file_data = next((x for x in self.catalogue_data.discovery_client.dataframe_file_metadata_pairs if
                              x[1].file_path == file_path), (pd.DataFrame, {}))
            return dcc.send_data_frame(file_data[0].to_csv, file_path)
