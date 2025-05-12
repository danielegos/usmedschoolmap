import pandas as pd
from dash import html, dcc, callback, Input, Output
import dash
from urllib.parse import unquote

dash.register_page(__name__, path_template="/location/<location_name>")

# layout = html.Div(id="location-page-content")


layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="location-page-content")
])

test_var = "Test Variable Text-Woohoo!"

# Load the CSV once at the top (assumes it doesn't change often)
data = pd.read_csv("data.csv")  # Adjust path as needed


@callback(
    Output("location-page-content", "children"),
    Input("url", "pathname")
)
def render_location(pathname):
    # Extract the location name
    location_name = unquote(pathname.split("/location/")[1]).replace("_", " ")

    # Find the row matching the location
    row = data[data["School"] == location_name]

    # Default image URL in case of no match
    image_url = None
    if not row.empty:
        image_url = row.iloc[0]["image_url"]

    description = None
    if not row.empty:
        description = row.iloc[0]["Description"]

    school_link = None
    if not row.empty:
        school_link = row.iloc[0]["Website"]      

    city = None
    if not row.empty:
        city = row.iloc[0]["City"] 

    state = None
    if not row.empty:
        state = row.iloc[0]["State"]

    mdphd = None
    if not row.empty:
        mdphd = row.iloc[0]["MD-PhD Program"]

    # Get top 3 residency match placements
    top1 = None
    if not row.empty:
        top1 = row.iloc[0]["#1 Specialty (2025 Match)"]

    top2 = None
    if not row.empty:
        top2 = row.iloc[0]["#2 Specialty (2025 Match)"]

    top3 = None
    if not row.empty:
        top3 = row.iloc[0]["#3 Specialty (2025 Match)"]

    mdphd_message = None
    if mdphd == "Yes":
        mdphd_message = "has an MD-PhD program"
    else:
        mdphd_message = "does not have an MD-PhD program"

    mdphd_link = None
    if not row.empty:
        mdphd_link = row.iloc[0]["MD-PhD_link"]

    lcme_status = None
    if not row.empty:
        lcme_status = row.iloc[0]["LCME Accreditation Status"]

    initial_acc_year = None
    if not row.empty:
        initial_acc_year = row.iloc[0]["Initial Year of LCME Accreditation"]


    return html.Div([
        html.H2(f"{location_name}"),
        html.Br(),
        html.Img(src=image_url, style={"width": "700px", "height": "auto"}) if image_url else html.P("Image not found."),
        html.Br(),
        html.P(f"Location: {city}, {state}"),
        html.Br(),
        html.P(f"Description from {location_name}:"),
        html.P(f"{description}"),

        # Top 3 match placements
        html.P("Top 3 specialties based on 2025 Match results:"),
        html.Ol([html.Li(f"{top1}"), html.Li(f"{top2}"), html.Li(f"{top3}")]),
        html.Br(),

        # LCME Accreditation
        html.P(f"LCME Accreditation Status: {lcme_status}"),
        html.P(f"Initial Year of LCME Accreditation: {initial_acc_year}"),
        html.Br(),

        # MD-PhD
        html.P(f"{location_name} {mdphd_message}."),
        html.P(f"MD-PhD program site:"),
        html.A([f"{mdphd_link}", html.Span("↗", style={"fontSize": "12px"})], href=mdphd_link, target="_blank") if mdphd_link is not None else "",
        html.Br(),

        # School link
        html.Br(),
        html.P(f"Learn more about {location_name}: "),
        html.A([f"{school_link}", html.Span("↗", style={"fontSize": "12px"})], href=school_link, target="_blank"),
        
        html.Br(),
        html.Br(),
        dcc.Link("Back to Map", href="/")
    ], style={"backgroundColor": "#FFFFFF", "padding": "20px", "borderRadius": "10px"})
