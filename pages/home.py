import pandas as pd
import plotly.express as px
from dash import html, dcc, callback, Input, Output, clientside_callback, dash_table
import dash
# from dash.dependencies import ClientsideFunction
# from dash import clientside_callback


dash.register_page(__name__, path="/")


data = pd.read_csv('data.csv')

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

clustered_data = pd.read_csv('clustered_schools.csv')

# Build map of clustered schools
cluster_fig = px.scatter_mapbox(
    clustered_data,
    lat="Latitude",
    lon="Longitude",
    hover_name="School",
    hover_data={
        "Latitude": False,
        "Longitude": False,
        "State": False,
        "City": False,
        "LCME Accreditation Status": False,
        "Initial Year of LCME Accreditation": False,
        "MD-PhD Program": False,
        "#1 Specialty (2025 Match)": False,
        "#2 Specialty (2025 Match)": False,
        "#3 Specialty (2025 Match)": False,
        "hierarchical_cluster": True,
        "cluster_summary": True,
        },
    custom_data=["School"],
    zoom=3,
    height=600,

    # Attempt to specify colors
    color = "hierarchical_cluster",
)

cluster_fig.update_layout(
    mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0},
    legend=dict(
        orientation="h",  # horizontal legend
        yanchor="bottom",
        y=0,  # position from bottom (0 = bottom, 1 = top)
        xanchor="center",
        x=0.5  # center horizontally
    )
)

cluster_fig.update_traces(marker=dict(size=10))  # Increase or decrease as needed

table_df = clustered_data[['School', 'hierarchical_cluster', 'cluster_summary']].copy()

# Prep full data table with links
# Create a new column with Markdown-formatted links
clustered_data['Website_Link'] = clustered_data['Website'].apply(
    lambda x: f"[{x}]({x})" if pd.notnull(x) and x.strip() else "N/A"
)

clustered_data['MD-PhD_Website_Link'] = clustered_data['MD-PhD_link'].apply(
    lambda x: f"[{x}]({x})" if pd.notnull(x) and x.strip() else "N/A"
)

# Preview the updated DataFrame
print(clustered_data[['Website', 'Website_Link']].head())
print(clustered_data[['MD-PhD_link', 'MD-PhD_Website_Link']].head())

full_table = clustered_data[['School', 'City', 'State', 'Website_Link', 'MD-PhD_Website_Link']].copy()




layout = html.Div([
    html.H2("LCME Accredited MD and MD-PhD Programs in the United States"),
    html.P("Updated 5-23-25 by Daniel Gallegos"),
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
    html.Br(),
    html.Br(),
    html.Hr(),
    html.Br(),
    html.Br(),
    html.H2("Grouping Similar Medical Schools Using Hierarchical Clustering in Scikit-learn and SciPy"),
    html.P("The methodology for this clustering can be seen in the Jupyter Binder here:"),
    html.A(["https://mybinder.org/v2/gh/danielegos/usmedschoolmap/main?urlpath=%2Fdoc%2Ftree%2Fhierarchical_clustering_task2.ipynb",
            html.Span("↗", style={"fontSize": "12px"})],
           href="https://mybinder.org/v2/gh/danielegos/usmedschoolmap/main?urlpath=%2Fdoc%2Ftree%2Fhierarchical_clustering_task2.ipynb",
           target="_blank"),
    html.Br(),
    html.Br(),
    html.Img(src="assets/dendrogram.png", style={"width": "100%", "height": "auto"}),
    # Add map of clustered schools
    html.Br(),
    html.Br(),
    html.P("The map and table below show the placement of each medical school within the hierarchical cluster represented in the dendrogram above, along with a summary of the top five words which characterize its cluster."),
    dcc.Graph(id="cluster_map", figure=cluster_fig),
    html.Br(),

    dash_table.DataTable(
        data=table_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in table_df.columns],
        sort_action='native',  # Enable sorting
        filter_action='native',  # Enable filtering
        page_size=10,
        style_cell={
            'textAlign': 'left',  # Left align all cell text
            'padding': '5px',
            'whiteSpace': 'normal',  # Allow line wrapping if needed
        },
        style_header={
            'fontWeight': 'bold',  # Bold headers
            'textAlign': 'left',  # Left align header text
            'backgroundColor': '#f9f9f9',  # Optional: light background color for headers
        },


        style_table={'overflowX': 'auto'},
    ),
    html.Br(),
    html.Br(),
    html.Hr(),
    html.Br(),
    html.Br(),

    # Include full list of schools
    html.H2("Full list of LCME Accredited MD and MD-PhD Programs in the United States"),
    html.Br(),

    dash_table.DataTable(
        data=full_table.to_dict('records'),
        columns=[{"name": i, "id": i, "presentation": "markdown"} for i in full_table.columns],
        sort_action='native',  # Enable sorting
        filter_action='native',  # Enable filtering
        page_size=160,
        style_cell={
            'textAlign': 'left',  # Left align all cell text
            'padding': '5px',
            'whiteSpace': 'normal',  # Allow line wrapping if needed
        },
        style_header={
            'fontWeight': 'bold',  # Bold headers
            'textAlign': 'left',  # Left align header text
            'backgroundColor': '#f9f9f9',  # Optional: light background color for headers
        },


        style_table={'overflowX': 'auto'},
    ),



    html.Br(),
    html.Hr(),
    html.Br(),

    html.P("The full dataset is available here:"),
    html.A(
        ["https://github.com/danielegos/usmedschoolmap/blob/main/clustered_schools.csv",
         html.Span("↗", style={"fontSize": "12px"})],
        href="https://github.com/danielegos/usmedschoolmap/blob/main/clustered_schools.csv",
        target="_blank"),

    html.Br(),
    html.Hr(),
    html.P("© Daniel Gallegos 2025. All rights reserved. Feedback is encouraged."),

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
