from app import app
from dash import html, dcc
import dash

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dash.page_container
])

if __name__ == "__main__":
    app.run(debug=True)
