from dash import html
import dash_bootstrap_components as dbc

from utils.component_decorators import component


@component(name="catalogue_file_column_overview", required_data=["local_data_catalogue"])
class CatalogueColumnOverview:
    def __init__(self, data):
        self.layout = html.Div()

    def build_column_view(self, file_data, file_metadata):
        return html.Div(self.build_column_list(file_metadata))

    def build_column_list(self, file_metadata):
        return dbc.ListGroup(
            [
                dbc.ListGroupItem([
                    html.H5(column.name)
                ])
                for column in file_metadata.columns],
            flush=True
        )
