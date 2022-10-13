import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import html

from utils.component_decorators import component, callback


@component(name="navigation_bar", required_data=["app_context"])
class NavBar:
    """
    The navbar is the default component which allows navigation between pages in the app
    """

    def __init__(self, app_context):
        self.components = app_context.components
        self.base_path = app_context.base_path
        self.pages = app_context.page_data

        navitems = []
        for page_url, page_items in self.pages.items():
            page_name = page_items[0]
            navitems.append(dbc.NavItem(dbc.NavLink(page_name, href=f"{self.base_path}{page_url}", active='partial')))

        self.layout = html.Div([
            dbc.Navbar(
                dbc.Nav(
                    id="main-page-navbar",
                    children=navitems,
                    navbar=True
                ),
                color="#2d2d2d",
                dark=True,
                expand="sm"
            )
        ])

    @callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(self, pathname):
        """
        choose which page to display
        """
        pathname = pathname.removeprefix(self.base_path)
        if not pathname or pathname not in self.pages:
            pathname = ""

        return self.pages[pathname][1]()
