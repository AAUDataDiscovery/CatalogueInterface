import base64

from dash import dcc, html
from dash import Input, Output, State
from utils.component_decorators import component, page, callback
import dash_bootstrap_components as dbc


@component(name="data_uploader")
class DataUploaderTab:
    def __init__(self):
        self.layout = dbc.Card([
            html.Header("Add files to the local catalogue"),
            dcc.Upload(
                id='data-upload-component',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=True
            ),
            html.Div(id='data-upload-output-component')
        ])

    @callback(
        Output('data-upload-output-component', 'children'),
        Input('data-upload-component', 'contents'),
        State('data-upload-component', 'filename'),
        State('data-upload-component', 'last_modified'),
        prevent_initial_call=True
    )
    def update_output(self, list_of_contents, list_of_names, list_of_dates):
        for index, filename in enumerate(list_of_names):
            with open(f'local_data/user_content/{filename}', 'wb') as newfile:
                contents = list_of_contents[index]
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                newfile.write(decoded)

        return html.Div('\n'.join(list_of_names))
