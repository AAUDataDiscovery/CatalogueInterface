import dash
import pandas as pd
from dash import html, dcc, dash_table
from dash import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.express as px

from utils.component_decorators import component, callback


@component(name="catalogue_dataframe_matcher", required_data=["local_data_catalogue"])
class CatalogueDataframeMatcher:
    def __init__(self, catalogue_data):
        self.catalogue_data = catalogue_data
        # List of colours that form a gradient
        self.table_colours = px.colors.diverging.RdYlGn[:9]
        # As there are a set amount of colours, a conversion must be made from a percentage to the required gradient
        self.colour_step = 100 / len(self.table_colours)

    def build_view(self, file_catalogue):
        """
        Build the main view for the selected file
        """
        file_data = file_catalogue.get_data()
        file_metadata = file_catalogue.get_metadata()
        data_head = file_data.head().to_dict('records')
        return html.Div([
            dcc.Dropdown([
                file_path for file_path in self.catalogue_data.file_catalogue_ref
                if file_path != file_metadata.data_manifest['path']
            ],
                id="catalogue-file-comparison-choice"
            ),

            html.H2(file_metadata.data_manifest['path']),
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
                                    "index": label
                                }
                            )),
                            dbc.Input(
                                type="number",
                                placeholder=1,
                                min=1,
                                id={
                                    "type": "catalogue-dataframe-comparison-weights",
                                    "index": label
                                }
                            )
                        ], class_name="mb-3")
                    ])
                    for label in self.catalogue_data.match_types
                ], width=3),
                dbc.Col([
                    html.Div(id="catalogue-comparison-table-wrapper"),
                    html.Hr(),
                    dbc.Card([
                        dbc.CardHeader("Selected relationships to update"),
                        dbc.CardBody(id="catalogue-selected-column-relationships"),
                        dbc.Button("Approve", id="catalogue-approve-comparisons-button"),
                        dbc.Alert(
                            "Column relationships updated!",
                            id="catalogue-approve-alert",
                            is_open=False,
                            duration=3000
                        )
                    ]),
                ], width=9)
            ]),
            dcc.Store("catalogue-comparison-percentages-data"),
            dcc.Store("catalogue-active-relationship-columns")
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
        if file_path is None:
            return dash.no_update

        file_catalogue = self.catalogue_data.get_metadata_by_file(file_path)
        file_meta = file_catalogue.get_metadata()
        file_data = file_catalogue.get_data()

        if file_meta is None:
            return html.Div(
                html.H2("Specify a file to compare with")
            )

        data_head = file_data.head().to_dict('records')

        return html.Div([
            html.H2(file_meta.data_manifest['path']),
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
        Output("catalogue-comparison-table-wrapper", "children"),
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
            result_table.to_dict('records'),
            style_data_conditional=[
                {
                    'if': {
                        'filter_query': f'{{{col_name}}} >= {self.colour_step * index} '
                                        f'&& {{{col_name}}} < {self.colour_step * (index + 1)}',
                        'column_id': col_name
                    },
                    'backgroundColor': colour
                }
                for col_name in active_origin_columns
                for index, colour in enumerate(self.table_colours)
            ],
            id='catalogue-comparison-table'
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
        if not target_file_path:
            return dash.no_update
        comparison_type_names = [x['id']['index'] for x in dash.ctx.inputs_list[0] if x.get('value', False)]
        comparison_weight_names = [x['id']['index'] for x in dash.ctx.inputs_list[1] if x.get('value', False)]

        origin_file_meta = self.catalogue_data.get_metadata_by_file(origin_file_path)
        target_file_meta = self.catalogue_data.get_metadata_by_file(target_file_path)

        if target_file_meta is None:
            return dash.no_update

        origin_hidden_columns = origin_hidden_columns or []
        target_hidden_columns = target_hidden_columns or []
        active_target_columns = [col['name'] for col in target_columns if col['name'] not in target_hidden_columns]
        active_origin_columns = [col['name'] for col in origin_columns if col['name'] not in origin_hidden_columns]

        if not any(comparison_types):
            # if no comparison types are given, reset all percentage cells to nothing (preventing updating columns)
            return [{col_name: None for col_name in active_origin_columns} for _ in range(len(active_target_columns))]

        percentage_data = self.catalogue_data.get_dataframe_comparisons(
            comparison_type_names,
            comparison_weight_names,
            origin_file_meta,
            target_file_meta,
            active_origin_columns,
            active_target_columns
        )

        # data table format is as follows: [{col_name: row_val0}, {col_name: row_val1}]
        percentage_table = [
            {origin_key: percentage_data[origin_key][target_key] for origin_key in percentage_data.keys()}
            for target_key in active_target_columns
        ]

        return percentage_table

    @callback(
        Output("catalogue-selected-column-relationships", 'children'),
        Output("catalogue-active-relationship-columns", 'data'),
        Input("catalogue-comparison-table", 'active_cell'),
        State("catalogue-comparison-table", 'data'),
        State("catalogue-active-relationship-columns", 'data'),
        State("catalogue-target-comparison-table", "hidden_columns"),
        State("catalogue-origin-comparison-table", "columns"),
    )
    def select_comparison_cells(self, last_selection, table_data, active_selections, hidden_columns, columns):
        """
        Allows the user to choose which relationships should be updated
        """
        active_selections = self._flatten_dict(active_selections) if active_selections else {}
        if not last_selection:
            # component is being initialised
            return html.Div([
                html.H2("Choose a relationship to update")
            ]), []

        hidden_columns = hidden_columns or []
        active_columns = [col['name'] for col in columns if col['name'] not in hidden_columns]
        selection = (last_selection['column_id'], active_columns[last_selection['row']])

        # if the selection is already in the active selections, remove it
        # NOTE: since we can't use immutable types such as tuples for keys, we have to use nested dicts instead
        if selection in active_selections:
            active_selections.pop(selection)
        else:
            selection_value = table_data[last_selection['row']][last_selection['column_id']]
            active_selections[selection] = selection_value

        return html.Div([
            dbc.ListGroup([
                dbc.ListGroupItem(
                    f"{origin} -> {target}"
                )
                for origin, target in active_selections
            ])
        ]), self._explode_dict(active_selections)

    @callback(
        Output("catalogue-approve-alert", "is_open"),
        Input("catalogue-approve-comparisons-button", "n_clicks"),
        State("catalogue-active-relationship-columns", "data"),
        State("selected-catalogue-filename", 'data'),
        State("catalogue-file-comparison-choice", "value")
    )
    def update_relationships(self, n_clicks, active_relations, origin_file_path, target_file_path):
        """
        If the button has been pressed, update the column relationships
        """
        if not n_clicks:
            return dash.no_update

        for col_pair, certainty in self._flatten_dict(active_relations).items():
            origin_col, target_col = col_pair
            self.catalogue_data.update_relationships(
                origin_file_path, target_file_path, origin_col, target_col, certainty
            )

        return True

    @staticmethod
    def _flatten_dict(input_dict):
        """
        Flattens a structure such as:
        {
            key: {
                key: value
            }
        }
        into:
        {
            (key, key) : value
        }

        This makes operations a little more intuitive to work with, and avoids nesting loops
        """
        return {(key, nested_key): value for key in input_dict for nested_key, value in input_dict[key].items()}

    @staticmethod
    def _explode_dict(input_dict):
        """
        Explodes an abstract structure such as:
        {
            (key, key) : value
        }
        into:
        {
            key: {
                key: value
            }
        }

        This allows tuple keys to be turned into json compatible nested dicts
        """
        return_dict = {}
        for key, nested_key in input_dict.keys():
            return_dict.setdefault(key, {}).update({nested_key:input_dict[(key, nested_key)]})
        return return_dict
