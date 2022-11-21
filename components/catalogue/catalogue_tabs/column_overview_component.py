from dash import html
import dash_bootstrap_components as dbc

from utils.component_decorators import component


@component(name="catalogue_file_column_overview", required_data=["local_data_catalogue"])
class CatalogueColumnOverview:
    def __init__(self, data):
        self.data_catalogue = data
        self.layout = html.Div()
        # Set colour thresholds for the certainty
        # 0 - 50 (danger) ; 50 - 75 (warning) ; 75 - 100 (success)
        self.colour_thresholds = lambda x: "success" if x >= 75 else ("warning" if x >= 50 else "danger")

    def build_column_view(self, file_metadata):
        return html.Div(self.build_column_list(file_metadata))

    def build_column_list(self, file_metadata):
        return dbc.Accordion(
            [
                dbc.AccordionItem([
                    html.H5("Relationships:"),
                    dbc.ListGroup([
                        dbc.ListGroupItem(
                            f"Column: {relationship.target_column_name} "
                            f"-- from \
                            {self.data_catalogue.get_metadata_by_hash(relationship.target_file_hash).file_path}"
                            f" (Certainty: {relationship.certainty}%)",
                            color=self.colour_thresholds(relationship.certainty)
                        )
                        for relationship in file_metadata.columns.get(column).relationships
                    ], flush=True)
                ],
                    title=column
                )
                for column in file_metadata.columns
            ],
            flush=True
        )
