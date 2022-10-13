from dash import html
from utils.component_decorators import component, page


@component(name="catalogue_page", required_data=["local_data_catalogue"])
class CataloguePage:
    def __init__(self, local_data):
        self.local_data = local_data
        self.layout = html.Div("Catalogue page")

    @page("catalogue", "Catalogue")
    def display_page(self):
        return self.layout
