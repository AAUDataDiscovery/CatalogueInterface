import dash
import pandas as pd
from dash import html, MATCH, ALL
from dash import dash_table
from dash import Input, Output, State, ctx
from dash import dcc
import dash_bootstrap_components as dbc

from discovery.utils.metadata.metadata import NumericColMetadata
from utils.component_decorators import component, page, callback


@component(name="catalogue_page", children=["filesystem_view"], required_data=["local_data_catalogue"])
class CataloguePage:
    def __init__(self, filesystem_view, catalogue_data):
        self.catalogue_data = catalogue_data
        self.layout = dbc.Row([
            dbc.Col(filesystem_view.layout, width=3, style={"height": "94vh", "overflow": "scroll"}),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div('No page selected', id='catalogue-page-viewer')
                    ])
                ])
            ], width=9, style={"height": "94vh", "overflow": "scroll"}),
            dcc.Download(id="download-catalogue-dataframe"),
            dcc.Store(id='selected-catalogue-filename')
        ], className="g-0")

    @page("catalogue", "Catalogue")
    def display_page(self):
        return self.layout

    def _build_table_view(self, file_data, file_metadata):
        """
        Create an overview for a given dataframe
        """
        data_head = file_data.head().to_dict('records')
        numeric_file_metadata = [x for x in file_metadata.columns if isinstance(x, NumericColMetadata)]
        numeric_display_columns = ['name', 'mean', 'maximum', 'minimum']
        numeric_display_records = [{col_name: getattr(metadata, col_name) for col_name in numeric_display_columns} for
                                   metadata in numeric_file_metadata]

        return html.Div([
            html.H1(f"Displaying file '{file_metadata.file_path}'"),
            html.Hr(),
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
        Output("catalogue-page-viewer", 'children'),
        Output("selected-catalogue-filename", 'data'),
        Input({"type": "catalogue-fileviewer", "index": ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def update_display_page(self, file_view):
        """
        If any of the files are clicked on, display their metadata view
        If all the files in the file_view are at 0, this means that none have been clicked on
        """
        if not sum(file_view):
            return dash.no_update

        file_path = ctx.triggered_id['index']
        file_data = next((x for x in self.catalogue_data.discovery_client.dataframe_file_metadata_pairs if
                          x[1].file_path == file_path), (pd.DataFrame, {}))
        return self._build_table_view(*file_data), file_path

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
