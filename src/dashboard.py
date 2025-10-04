import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, dash_table, dcc, html
from loguru import logger

from client import Client

# TODO: separate data from presentation
g = Client()
df = pd.DataFrame(g.get_activities(start=0, limit=1000)).set_index("activityId")
df["activityId"] = df.index
logger.info(f"{df.shape=}")

df = df[
    ["activityId", "activityType", "activityName", "startTimeLocal", "distance", "elapsedDuration"]
]
df["startTimeLocal"] = pd.to_datetime(df["startTimeLocal"])
df["activityType"] = df["activityType"].apply(lambda d: d["typeKey"])
df["distance_km"] = (df["distance"] / 1000).round(2)
df["duration_min"] = (df["elapsedDuration"] / 60).round(2)
df = df.drop(["distance", "elapsedDuration"], axis=1)


TEXT_STYLE = {"font-family": "sans-serif", "font-size": "14pt"}
ERR_TEXT_STYLE = TEXT_STYLE | {"color": "red", "font-weight": "bold"}

app = Dash(__name__)
app.layout = html.Div(
    [
        html.Div(
            [
                # Text input
                dcc.Textarea(
                    id="df_query",
                    placeholder="Enter Pandas query...",
                    style={
                        "width": "50%",
                        "height": "120px",
                        "fontFamily": "monospace",
                        "fontSize": "16px",
                        "whiteSpace": "pre",
                    },
                ),
                html.Button("Run query", id="run_query", n_clicks=0, style={"marginLeft": "10px"}),
            ],
            style={"display": "flex", "alignItems": "center"},
        ),
        # Main activities
        dcc.Graph(id="plot_activities"),
        # Activity info
        html.Div(id="activity_info", style=TEXT_STYLE),
        dcc.Loading(
            id="hr_loading",
            type="circle",
            style={"marginTop": "40px"},
            children=html.Div(id="hr_info"),
        ),
    ]
)


@app.callback(
    Output("plot_activities", "figure"),
    Input("run_query", "n_clicks"),
    State("df_query", "value"),
)
def _(n_clicks, query):
    if not n_clicks or not query:
        tmp = df
    else:
        tmp = df.query(query.replace("\n", " "))

    fig = px.scatter(
        tmp,
        x="startTimeLocal",
        y="duration_min",
        color="activityType",
        symbol="activityType",
        custom_data=["activityId"],
        title=f"Activities: {len(tmp):,d}",
    )
    fig.update_traces(
        marker={"size": 10, "line": {"width": 1, "color": "Black"}},
        selector={"mode": "markers"},
    )
    return fig


@app.callback(
    Output("activity_info", "children"),
    Input("plot_activities", "clickData"),
)
def _(clickData):
    if not clickData:
        return "Select an activity to see detailed info..."

    activity_id = clickData["points"][0]["customdata"][0]
    pt = df.loc[[activity_id]]

    link = f"https://connect.garmin.com/modern/activity/{activity_id}"

    return html.Div(
        [
            dash_table.DataTable(
                data=pt.to_dict(orient="records"),
                columns=[{"name": c, "id": c} for c in pt.columns],
                style_table={"overflowX": "auto", "margin": "auto", "width": "80%"},
                style_cell={"padding": "5px"},
            ),
            html.Div(
                html.A("Open Activity (Garmin Connect)", href=link, target="_blank"),
                style=(
                    TEXT_STYLE | {"marginTop": "10px", "textAlign": "center", "font-weight": "bold"}
                ),
            ),
        ]
    )


@app.callback(
    Output("hr_info", "children"),
    Input("plot_activities", "clickData"),
)
def _(clickData):
    if not clickData:
        # return html.Div("Select an activity to see Heart Rate data...", style=TEXT_STYLE)
        return

    hr = g.get_hr(activity_id=clickData["points"][0]["customdata"][0])

    if not hr:
        return html.Div("No HR data available for selected activity!", style=ERR_TEXT_STYLE)

    # smooth
    w = 50
    hr = np.convolve(hr, np.ones(w) / w, mode="valid")
    fig = px.line(hr, title="Heart Rate")
    fig.update_yaxes(range=[50, 210])
    return dcc.Graph(figure=fig)


if __name__ == "__main__":
    app.run(debug=True)
