import dash
import pandas as pd
from dash import html, dcc, dash_table
from dash import Input, Output, State, ALL
import dash_bootstrap_components as dbc

from utils.component_decorators import component, callback


@component(name="catalogue_dataframe_matcher", required_data=["local_data_catalogue"])
class CatalogueDataframeMatcher:
    def __init__(self, catalogue_data):
        self.catalogue_data = catalogue_data

    def build_view(self, file_data, file_metadata):
        """
        Build the main view for the selected file
        """
        data_head = file_data.head().to_dict('records')
        return html.Div([
            dcc.Dropdown([
                file_path for file_path in self.catalogue_data.get_loaded_files()
                if file_path != file_metadata.file_path
            ],
                id="catalogue-file-comparison-choice"
            ),

            html.H2(file_metadata.file_path),
            dash_table.DataTable(
                data_head,
                columns=[{
                    "name": col,
                    "hideable": True,
                    "id": col
                } for col in file_data.columns],
                id="catalogue-origin-comparison-table"
            ),

            html.Div([
                html.H2("Specify a file to compare with"),
                dash_table.DataTable(id="catalogue-target-comparison-table")
            ],
                id="catalogue-file-comparison-view"
            ),

            html.Hr(),
            html.H2("Comparison"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Label(label),
                        dbc.InputGroup([
                            dbc.InputGroupText(dbc.Checkbox(
                                id={
                                    "type": "catalogue-dataframe-comparison-types",
                                    "index": value
                                }
                            )),
                            dbc.Input(
                                type="number",
                                placeholder=1,
                                min=1,
                                id={
                                    "type": "catalogue-dataframe-comparison-weights",
                                    "index": value
                                }
                            )
                        ], class_name="mb-3")
                    ])
                    for label, value in self.catalogue_data.match_types.items()
                ], width=3),
                dbc.Col(html.Div(id="catalogue-comparison-table"), width=9)
            ]),
            dcc.Store("catalogue-comparison-percentages-data")
        ])

    @callback(
        Output("catalogue-file-comparison-view", "children"),
        Input("catalogue-file-comparison-choice", "value")
    )
    def display_compare_file(self, file_path):
        """
        Display the head of file that has been chosen as a target for comparison
        If none is specified (or the field is cleared) ask the user to specify
        """
        file_search = next(
            (x for x in self.catalogue_data.discovery_client.dataframe_file_metadata_pairs if
             x[1].file_path == file_path), None)

        if file_search is None:
            return html.Div(
                html.H2("Specify a file to compare with")
            )

        file_data, file_metadata = file_search
        data_head = file_data.head().to_dict('records')

        return html.Div([
            html.H2(file_metadata.file_path),
            dash_table.DataTable(
                data_head,
                columns=[{
                    "name": col,
                    "hideable": True,
                    "id": col
                } for col in file_data.columns],
                id="catalogue-target-comparison-table"
            )
        ])

    @callback(
        Output("catalogue-comparison-table", "children"),
        Input("catalogue-target-comparison-table", "hidden_columns"),
        Input("catalogue-origin-comparison-table", "hidden_columns"),
        Input("catalogue-comparison-percentages-data", "data"),
        State("catalogue-target-comparison-table", "columns"),
        State("catalogue-origin-comparison-table", "columns")
    )
    def update_result_table(self, target_hidden_columns, origin_hidden_columns, percentage_data, target_columns,
                            origin_columns):
        """
        Change the cells of the result table based on what has been hidden the original columns
        If no target dataframe is selected, do not update
        """
        if target_columns is None:
            return dash.no_update

        origin_hidden_columns = origin_hidden_columns or []
        target_hidden_columns = target_hidden_columns or []

        active_target_columns = [col['name'] for col in target_columns if col['name'] not in target_hidden_columns]
        active_origin_columns = [col['name'] for col in origin_columns if col['name'] not in origin_hidden_columns]

        result_table = pd.DataFrame(percentage_data, columns=[""] + active_origin_columns)[:len(active_target_columns)]
        result_table[""] = active_target_columns
        return dash_table.DataTable(
            result_table.to_dict('records')
        )

    @callback(
        Output("catalogue-comparison-percentages-data", "data"),
        Input({"type": "catalogue-dataframe-comparison-types", "index": ALL}, 'value'),
        Input({"type": "catalogue-dataframe-comparison-weights", "index": ALL}, 'value'),
        State("selected-catalogue-filename", 'data'),
        State("catalogue-file-comparison-choice", "value"),
        State("catalogue-target-comparison-table", "hidden_columns"),
        State("catalogue-origin-comparison-table", "hidden_columns"),
        State("catalogue-target-comparison-table", "columns"),
        State("catalogue-origin-comparison-table", "columns")
    )
    def update_comparison_percentage_data(self, comparison_types, comparison_weights, origin_file_path,
                                          target_file_path,
                                          target_hidden_columns, origin_hidden_columns, target_columns, origin_columns):
        comparison_type_names = [x['id']['index'] for x in dash.ctx.inputs_list[0] if x.get('value', False)]
        comparison_weight_names = [x['id']['index'] for x in dash.ctx.inputs_list[1] if x.get('value', False)]
        origin_file_search = next(
            (x for x in self.catalogue_data.discovery_client.dataframe_file_metadata_pairs if
             x[1].file_path == origin_file_path), None)
        target_file_search = next(
            (x for x in self.catalogue_data.discovery_client.dataframe_file_metadata_pairs if
             x[1].file_path == target_file_path), None)

        if target_file_search is None:
            return dash.no_update

        origin_hidden_columns = origin_hidden_columns or []
        target_hidden_columns = target_hidden_columns or []
        active_target_columns = [col['name'] for col in target_columns if col['name'] not in target_hidden_columns]
        active_origin_columns = [col['name'] for col in origin_columns if col['name'] not in origin_hidden_columns]

        origin_file_data = origin_file_search[0]
        target_file_data = target_file_search[0]
        origin_file_data = origin_file_data.reindex(columns=active_origin_columns)
        target_file_data = target_file_data.reindex(columns=active_target_columns)
        percentages = self.catalogue_data.get_dataframe_comparisons(
            comparison_type_names, comparison_weight_names, origin_file_data, target_file_data
        )

        return percentages
