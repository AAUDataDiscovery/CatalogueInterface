import logging

import pandas as pd
import dash
from dash import Input, Output, State, ALL, ctx
from dash import html, dcc
import dash_bootstrap_components as dbc

from utils.component_decorators import component, page, callback

logger = logging.getLogger(__name__)


@component(name="catalogue_page",
           children=[
               "filesystem_view",
               "catalogue_file_overview",
               "catalogue_file_column_overview",
               "catalogue_dataframe_matcher"
           ],
           required_data=[
               "local_data_catalogue"
           ])
class CataloguePage:
    def __init__(self, filesystem_view, file_overview, column_overview, dataframe_matcher, catalogue_data):
        self.catalogue_data = catalogue_data
        self.tab_reference = {
            "catalogue-overview": file_overview.build_table_view,
            "catalogue-columns": column_overview.build_column_view,
            "dataframe-matcher": dataframe_matcher.build_view
        }

        self.layout = dbc.Row([
            dbc.Col(filesystem_view.layout, width=3, style={"height": "94vh", "overflow": "scroll"}),
            dbc.Col([
                html.H1("No page selected", id="catalogue-file-header", style={"padding": "10px"}),
                html.Hr(),
                dbc.CardHeader(
                    dbc.Tabs([
                        dbc.Tab(label="Overview", tab_id="catalogue-overview"),
                        dbc.Tab(label="Columns", tab_id="catalogue-columns"),
                        dbc.Tab(label="Matcher", tab_id="dataframe-matcher")
                    ],
                        id="catalogue-file-card-tabs",
                        active_tab="catalogue-overview"
                    )
                ),
                dbc.CardBody(id="catalogue-file-card-view")
            ], width=9, style={"height": "94vh", "overflow": "scroll"}),
            dcc.Download(id="download-catalogue-dataframe"),
            dcc.Store(id='selected-catalogue-filename')
        ], className="g-0")

    @page("catalogue", "Catalogue")
    def display_page(self):
        return self.layout

    @callback(
        Output("catalogue-file-card-view", 'children'),
        Output("selected-catalogue-filename", 'data'),
        Output("catalogue-file-header", "children"),
        Input({"type": "catalogue-fileviewer", "index": ALL}, 'n_clicks'),
        Input("catalogue-file-card-tabs", "active_tab"),
        State("selected-catalogue-filename", 'data'),
        prevent_initial_call=True
    )
    def update_display_page(self, file_view, active_tab, selected_file):
        """
        If any of the files are clicked on, or if there is a change of tabs, update the content being shown
        Note: as you can not have duplicate outputs, both pieces of logic must exist here
        """
        if ctx.triggered_id == "catalogue-file-card-tabs":
            # if the component is being updated by a tab change, then we can keep the selected file in memory
            file_path = selected_file
        elif not sum(file_view):
            # Updates to the file structure count as updates to the file_view
            # If all the files in the file_view are at 0, this means that none have been clicked on, ignore
            return dash.no_update
        else:
            # get the file path that was specified
            file_path = ctx.triggered_id['index']

        file_catalogue = self.catalogue_data.get_metadata_by_file(file_path)

        header_text = html.H1(f"Displaying file '{file_catalogue.get_metadata().data_manifest['path']}'")

        card_layout = self.tab_reference.get(active_tab, self._card_stub)(file_catalogue)
        return card_layout, file_path, header_text

    @staticmethod
    def _card_stub(*args):
        """
        Something went wrong, fail elegantly
        """
        logger.error("Tab layout not found, returning empty div")
        return html.Div()
