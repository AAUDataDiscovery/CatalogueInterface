from dash import html
from utils.component_decorators import page


@page("", "Landing")
def display_page():
    return html.Div("This is the landing page")
