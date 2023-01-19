from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import plotly.express as px

from utils.component_decorators import component
from discovery.metadata import NumericColMetadata


@component(name="catalogue_file_column_overview", required_data=["local_data_catalogue"])
class CatalogueColumnOverview:
    def __init__(self, data):
        self.data_catalogue = data
        self.layout = html.Div()
        # Set colour thresholds for the certainty
        # 0 - 50 (danger) ; 50 - 75 (warning) ; 75 - 100 (success)
        self.colour_thresholds = lambda x: "success" if x >= 75 else ("warning" if x >= 50 else "danger")

    def build_column_view(self, file_catalogue):
        return html.Div(self.build_column_list(file_catalogue))

    def build_column_list(self, file_catalogue):
        catalogue_data = file_catalogue.get_data()
        file_metadata = file_catalogue.get_metadata()
        return dbc.Accordion(
            [
                dbc.AccordionItem([
                    html.H5(f"Inferred Column Type: {column.get_attributes(stringify=True)['type']}"),
                    html.H5("Relationships:"),
                    dbc.ListGroup([
                        dbc.ListGroupItem(
                            f"Column: {relationship.target_column_name} "
                            f"-- from \
                            {self.data_catalogue.get_metadata_by_hash(relationship.target_hash).get_metadata().data_manifest['path']}"
                            f" (Certainty: {relationship.certainty}%)",
                            color=self.colour_thresholds(relationship.certainty)
                        )
                        for relationship in column.relationships
                    ], flush=True),
                    html.H5("Visualisation:"),
                    html.Div(self.build_visual(catalogue_data, column_name, column))
                ],
                    title=column_name
                )
                for column_name, column in file_metadata.columns.items()
            ],
            flush=True
        )

    def build_visual(self, catalogue_data, column_name, column):
        """ Create a graph if the column is numeric """
        if isinstance(column, NumericColMetadata):
            catalogue_data_mask = catalogue_data[column_name]
            return dcc.Graph(figure=px.line(catalogue_data_mask))
        return html.Div("No visuals currently supported for this column type")
