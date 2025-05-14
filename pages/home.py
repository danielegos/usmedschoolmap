import pandas as pd
import plotly.express as px
from dash import html, dcc, callback, Input, Output, clientside_callback
import dash
# from dash.dependencies import ClientsideFunction
# from dash import clientside_callback


dash.register_page(__name__, path="/")


data = pd.read_csv('data.csv')

# Attempt 1
# Build map
fig = px.scatter_mapbox(
    data,
    lat="Latitude",
    lon="Longitude",
    hover_name="School",
    hover_data={
        "Latitude": False,
        "Longitude": False,
        "State": True,
        "City": True,
        "LCME Accreditation Status": True,
        "Initial Year of LCME Accreditation": True,
        "MD-PhD Program": True,
        "#1 Specialty (2025 Match)": True,
        "#2 Specialty (2025 Match)": True,
        "#3 Specialty (2025 Match)": True,
        },
    custom_data=["School"],
    zoom=3,
    height=600,

    # Attempt to specify colors
    color = "MD-PhD Program",
)


# Group and count schools by state
state_counts = (
    data.groupby("State")
    .size()
    .reset_index(name="num_schools")
)

# Sort by count DESC, then state name ASC
state_counts = state_counts.sort_values(by=["num_schools", "State"], ascending=[False, True])

# Make 'State' a categorical column with the desired order
state_counts["State"] = pd.Categorical(state_counts["State"], categories=state_counts["State"], ordered=True)

# Create the bar chart
bar_fig = px.bar(
    state_counts,
    x="State",
    y="num_schools",
    title="Number of Medical Schools per State (Ordered)",
    labels={"State": "State", "num_schools": "Number of Schools"},
    color_discrete_sequence=["#636EFA"]
)
#
# row_count = len(data)
# print(row_count)

fig.update_layout(
    mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0},
    legend=dict(
        orientation="h",  # horizontal legend
        yanchor="bottom",
        y=0,  # position from bottom (0 = bottom, 1 = top)
        xanchor="center",
        x=0.5  # center horizontally
    )
)

fig.update_traces(marker=dict(size=10))  # Increase or decrease as needed

# fig.update_traces(marker=dict(size=12, color="blue"))

# Include stacked bar chart of residency specialties
# Import residencies.csv as wide_df


wide_df = pd.read_csv('residencies.csv')

stacked_fig = px.bar(
    wide_df, 
    x="Specialty", 
    y=["#1", "#2", "#3"], 
    title="Frequency of Specialty Placement in Top 3 Residencies Per Med School for 2025 Match",
    labels={"Specialty": "Specialty", 
            "value": "Frequency in Top 3 Specialties Per Med School",
            "variable": "Ranking in 2025 Match"},
    )




layout = html.Div([
    html.H2("LCME Accredited MD and MD-PhD Programs in the United States"),
    html.P("Updated 5-14-25"),
    html.P("Click on any of the points in the map below to be directed to that med school's summary page."),
    dcc.Graph(id="map", figure=fig),
    dcc.Location(id="map-url", refresh=True),
    html.Span("*Indicates that the program was accredited prior to the founding of the LCME in 1942.",
              style={"fontSize": "12px"}),
    html.Br(),
    html.Br(),
    html.P("Students interested in applying to MD-PhD programs should also be aware of the NIH Oxford-Cambridge Scholars Program. Learn more at the link below:"),
    html.A(["https://oxcam.gpp.nih.gov/about/mdphd-partnerships-program",
            html.Span("↗", style={"fontSize": "12px"})],
           href="https://oxcam.gpp.nih.gov/about/mdphd-partnerships-program",
           target="_blank"),
    html.Br(),
    html.Br(),
    html.P("For more on Liaison Committee on Medical Education (LCME) accreditation:"),
    html.A(["https://lcme.org/about/",
           html.Span("↗", style={"fontSize": "12px"})],
           href="https://lcme.org/about/",
           target="_blank"),
    # dcc.Graph(id="histogram", figure=hist),
    dcc.Graph(id="bar", figure=bar_fig),
    dcc.Graph(id="stacked_bar", figure=stacked_fig),
    dcc.Store(id="redirect-path"),
    html.Div(id="dummy")  # placeholder output for clientside callback

], style={"backgroundColor": "#FFFFFF", "padding": "20px", "borderRadius": "10px"})

@callback(
    Output("redirect-path", "data"),
    Input("map", "clickData")
)

def go_to_location(clickData):
    if clickData:
        location = clickData["points"][0]["customdata"][0]
        return f"/location/{location.replace(' ', '_')}"
    return dash.no_update

clientside_callback(
    """
    function(path) {
        if (path) {
            window.location.href = path;
        }
        return '';
    }
    """,
    Output("dummy", "children"),
    Input("redirect-path", "data")
)