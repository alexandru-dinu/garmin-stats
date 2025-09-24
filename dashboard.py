import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dash_table, dcc, html

from client import Client

g = Client()
res = pd.DataFrame(g.get_activities(start=0, limit=1000))
mask = res["activityType"].apply(lambda d: "running" in d["typeKey"])

run = res.loc[mask]

# TODO: separate data from presentation
df = run[["activityId", "startTimeLocal", "distance", "elapsedDuration"]].reset_index(drop=True)
df["distance_km"] = (df["distance"] / 1000).round(2)
df["duration_min"] = (df["elapsedDuration"] / 60).round(2)
df["pace"] = (df["duration_min"] / df["distance_km"]).round(2)
df["pace_str"] = df["pace"].apply(lambda x: f"{int(x)}:{round(60 * (x % 1)):02d} min/km")
df = df.drop(["distance", "elapsedDuration"], axis=1)

TEXT_STYLE = {"font-family": "sans-serif", "font-size": "14px"}

app = Dash(__name__)

# TODO: smarter layout
app.layout = html.Div(
    [
        # Inputs
        html.Label("Number of activities: ", style=TEXT_STYLE),
        dcc.Input(
            id="n_selector",
            type="number",
            debounce=True,
            value=100,
        ),
        html.Label("Min distance: ", style=TEXT_STYLE),
        dcc.Input(id="n_min_distance", type="number", debounce=True, value=0),
        html.Div(id="err_msg", style=TEXT_STYLE | {"color": "red", "font-weight": "bold"}),
        # Main activities
        dcc.Graph(id="plot_running"),
        # Activity info
        html.Div(id="activity_info", style=TEXT_STYLE),
        dcc.Graph(id="hr_info"),
    ]
)


@app.callback(
    [Output("plot_running", "figure"), Output("err_msg", "children")],
    [Input("n_selector", "value"), Input("n_min_distance", "value")],
)
def _(n, md):
    n = int(n)
    msg = "" if n <= len(df) else f"Too many activities! (max = {len(df)})"
    fig = px.scatter(
        df.head(n).query(f"distance_km >= {md}"),
        x="startTimeLocal",
        y="duration_min",
        size="distance_km",
        color="pace",
        color_continuous_scale=px.colors.sequential.Turbo_r,
        custom_data=["pace_str", "distance_km"],
        title="Distance and Duration",
    )
    fig.update_traces(
        hovertemplate="Distance: %{customdata[1]}<br>Pace: %{customdata[0]}<br>Time: %{x}"
    )
    fig.update_traces(
        marker={"symbol": "circle", "line": {"width": 2, "color": "Black"}},
        selector={"mode": "markers"},
    )
    return fig, msg


@app.callback(
    Output("activity_info", "children"),
    Input("plot_running", "clickData"),
)
def _(clickData):
    if not clickData:
        return "Click a point"

    idx = clickData["points"][0]["pointIndex"]
    pt = df.iloc[[idx]]

    link = f'https://connect.garmin.com/modern/activity/{pt["activityId"].iloc[0]}'

    return html.Div(
        [
            dash_table.DataTable(
                data=pt.to_dict("records"),
                columns=[{"name": c, "id": c} for c in pt.columns],
                style_table={"overflowX": "auto", "margin": "auto", "width": "50%"},
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
    Output("hr_info", "figure"),
    Input("plot_running", "clickData"),
)
def _(clickData):
    if not clickData:
        return px.scatter()

    idx = clickData["points"][0]["pointIndex"]
    hr = g.get_hr(df.iloc[idx]["activityId"])

    if not hr:
        return px.scatter()

    # smooth
    w = 10
    hr = np.convolve(hr, np.ones(w) / w, mode="valid")
    fig = px.line(hr, title="Heart Rate")
    fig.update_yaxes(range=[80, 210])
    return fig


if __name__ == "__main__":
    app.run(debug=True)
