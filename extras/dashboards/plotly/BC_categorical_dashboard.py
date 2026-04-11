import glob
import pandas as pd
import numpy as np

import dash
from dash import dcc, html, dash_table, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import umap

# =========================
# LOAD DATA
# =========================
import kagglehub
path = kagglehub.dataset_download("mariolisboa/breast-cancer-wisconsin-original-data-set")
df = pd.read_csv(glob.glob(path + "/*")[0])

# =========================
# CLEANING
# =========================
df = df.drop(columns="Sample code number")

def fix(val):
    try:
        return int(val)
    except:
        return -1

df["Bare Nuclei"] = df["Bare Nuclei"].apply(fix)

features = df.columns[:-1]

# =========================
# PCA PRECOMPUTE
# =========================
X = df[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=3)
X_pca = pca.fit_transform(X_scaled)

df_pca = pd.DataFrame(X_pca, columns=["PC1", "PC2", "PC3"])
df_pca["Class"] = df["Class"]

# =========================
# DISPARATE IMPACT
# =========================
b = df[df.Class == 2].shape[0]
m = df[df.Class == 4].shape[0]

di = m / b if b != 0 else 0

if di > 1:
    di_value = 1 / di
    privileged = "Malignant"
    protected = "Benign"
else:
    di_value = di
    privileged = "Benign"
    protected = "Malignant"

# =========================
# PROBABILITY FUNCTION
# =========================
def prob(data, filters):
    mask = pd.Series(True, index=data.index)
    for col, val in filters.items():
        if val is None:
            continue
        vmin, vmax = val
        mask &= data[col].between(vmin, vmax)
    S = data[mask]
    if len(S) == 0:
        return 0, 0
    B = len(S[S.Class == 2]) / len(S)
    M = len(S[S.Class == 4]) / len(S)
    return B, M

# =========================
# DASH APP
# =========================
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Breast Cancer Analysis Dashboard"),

    # =========================
    # DATA EXPLORER
    # =========================
    html.H2("Dataset Explorer"),
    html.Div([
        html.Label("Select Columns"),
        dcc.Dropdown(
            id="column-selector",
            options=[{"label": c, "value": c} for c in df.columns],
            value=list(df.columns),
            multi=True
        ),
        html.Br(),
        html.Label("Filter by Class"),
        dcc.Checklist(
            id="class-filter",
            options=[
                {"label": "Benign", "value": 2},
                {"label": "Malignant", "value": 4}
            ],
            value=[2, 4],
            inline=True
        ),
    ]),

    dash_table.DataTable(
        id="data-table",
        page_size=10,
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": "#1f2c56",
            "color": "white",
            "fontWeight": "bold",
            "textAlign": "center"
        },
        style_cell={
            "textAlign": "center",
            "padding": "8px",
            "fontFamily": "Arial"
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#f9f9f9"},
            {"if": {"filter_query": "{Class} = 4"}, "backgroundColor": "#ffe6e6"},  # Malignant
            {"if": {"filter_query": "{Class} = 2"}, "backgroundColor": "#e6f2ff"}   # Benign
        ]
    ),

    html.Button("Download CSV", id="download-btn"),
    dcc.Download(id="download-data"),

    # =========================
    # HISTOGRAM
    # =========================
    html.H2("Feature Distribution"),
    dcc.Dropdown(
        id="feature-dropdown",
        options=[{"label": c, "value": c} for c in features],
        value=features[0]
    ),
    dcc.Graph(id="histogram"),

    # =========================
    # DISPARATE IMPACT
    # =========================
    html.H2("Disparate Impact"),
    html.Div(id="di-output"),

    # =========================
    # PROBABILITY CALCULATOR
    # =========================
    html.H2("Tumor Probability Calculator"),
    html.Div([
        html.Div([
            dcc.Checklist(
                id=f"check-{col}",
                options=[{"label": f"Use {col}", "value": "on"}],
                value=["on"]
            ),
            html.Label(col),
            dcc.RangeSlider(
                id=f"slider-{col}",
                min=df[col].min(),
                max=df[col].max(),
                step=1,
                value=[df[col].min(), df[col].max()],
                marks=None
            )
        ]) for col in features
    ], style={"columns": 2}),
    html.Button("Compute Probability", id="compute-btn"),
    dcc.Graph(id="prob-output"),

    # =========================
    # 3D VISUALIZATION
    # =========================
    html.H2("3D Visualization"),
    dcc.RadioItems(
        id="view-mode",
        options=[
            {"label": "Raw Features", "value": "raw"},
            {"label": "PCA (3D)", "value": "pca"},
            {"label": "UMAP (3D)", "value": "umap"},
        ],
        value="raw",
        inline=True
    ),

    html.Div([
        dcc.Dropdown(id="x-axis-3d", options=[{"label": c, "value": c} for c in features], value=features[0]),
        dcc.Dropdown(id="y-axis-3d", options=[{"label": c, "value": c} for c in features], value=features[1]),
        dcc.Dropdown(id="z-axis-3d", options=[{"label": c, "value": c} for c in features], value=features[2]),
    ], style={"columns": 3}),

    html.Div([
        html.Label("UMAP n_neighbors"),
        dcc.Slider(id="umap-neighbors", min=5, max=50, step=1, value=15,
                   marks={5: "5", 15: "15", 30: "30", 50: "50"}),
        html.Br(),
        html.Label("UMAP Metric"),
        dcc.Dropdown(
            id="umap-metric",
            options=[{"label": m, "value": m} for m in ["euclidean", "manhattan", "cosine", "chebyshev"]],
            value="euclidean"
        )
    ], style={"marginTop": "20px"}),
    dcc.Graph(id="scatter-3d")
])

# =========================
# CALLBACKS
# =========================
@app.callback(
    Output("data-table", "data"),
    Output("data-table", "columns"),
    Input("column-selector", "value"),
    Input("class-filter", "value")
)
def update_table(selected_cols, selected_classes):
    dff = df.copy()
    if selected_classes:
        dff = dff[dff["Class"].isin(selected_classes)]
    if selected_cols:
        dff = dff[selected_cols]
    return dff.to_dict("records"), [{"name": c, "id": c} for c in dff.columns]

@app.callback(
    Output("download-data", "data"),
    Input("download-btn", "n_clicks"),
    State("column-selector", "value"),
    State("class-filter", "value"),
    prevent_initial_call=True
)
def download_csv(n, selected_cols, selected_classes):
    dff = df.copy()
    if selected_classes:
        dff = dff[dff["Class"].isin(selected_classes)]
    if selected_cols:
        dff = dff[selected_cols]
    return dcc.send_data_frame(dff.to_csv, "data.csv", index=False)

@app.callback(
    Output("histogram", "figure"),
    Input("feature-dropdown", "value")
)
def update_histogram(feature):
    return px.histogram(df, x=feature, color=df["Class"].map({2: "Benign", 4: "Malignant"}))

@app.callback(
    Output("di-output", "children"),
    Input("feature-dropdown", "value")
)
def update_di(_):
    return html.Div([
        html.P(f"Privileged group: {privileged}"),
        html.P(f"Protected group: {protected}"),
        html.P(f"Disparate Impact: {di_value:.2f}")
    ])

@app.callback(
    Output("prob-output", "figure"),
    Input("compute-btn", "n_clicks"),
    [Input(f"slider-{col}", "value") for col in features] +
    [Input(f"check-{col}", "value") for col in features]
)
def update_probability(n, *inputs):
    if n is None:
        return go.Figure()

    slider_values = inputs[:len(features)]
    check_values = inputs[len(features):]

    filters = {}
    for col, slider, check in zip(features, slider_values, check_values):
        if check and "on" in check:
            filters[col] = slider

    B, M = prob(df, filters)

    fig = go.Figure()

    # Explicit names to fix legend
    fig.add_trace(go.Bar(
        x=[B*100],
        y=["Tumor"],
        name="Benign",
        orientation='h',
        marker_color='blue',
        text=f"{B*100:.1f}%",
        textposition='inside'
    ))
    fig.add_trace(go.Bar(
        x=[M*100],
        y=["Tumor"],
        name="Malignant",
        orientation='h',
        marker_color='crimson',
        text=f"{M*100:.1f}%",
        textposition='inside'
    ))

    fig.update_layout(
        barmode='stack',
        xaxis=dict(range=[0,100], title="Probability (%)"),
        yaxis=dict(title=""),
        height=200,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True,
        legend=dict(title="Class")
    )

    return fig

@app.callback(
    Output("scatter-3d", "figure"),
    Input("view-mode", "value"),
    Input("x-axis-3d", "value"),
    Input("y-axis-3d", "value"),
    Input("z-axis-3d", "value"),
    Input("umap-neighbors", "value"),
    Input("umap-metric", "value"),
)
def update_3d(mode, x, y, z, n_neighbors, metric):
    fig = go.Figure()
    if mode == "raw":
        for cls, color, name in [(2, "blue", "Benign"), (4, "crimson", "Malignant")]:
            d = df[df["Class"] == cls]
            fig.add_trace(go.Scatter3d(x=d[x], y=d[y], z=d[z],
                                       mode="markers", name=name,
                                       marker=dict(size=4, color=color, opacity=0.7)))
        fig.update_layout(scene=dict(xaxis_title=x, yaxis_title=y, zaxis_title=z))
    elif mode == "pca":
        for cls, color, name in [(2, "blue", "Benign"), (4, "crimson", "Malignant")]:
            d = df_pca[df_pca["Class"] == cls]
            fig.add_trace(go.Scatter3d(x=d["PC1"], y=d["PC2"], z=d["PC3"],
                                       mode="markers", name=name,
                                       marker=dict(size=4, color=color, opacity=0.7)))
        fig.update_layout(scene=dict(xaxis_title="PC1", yaxis_title="PC2", zaxis_title="PC3"))
    else:  # UMAP
        X_scaled = StandardScaler().fit_transform(df[features])
        reducer = umap.UMAP(n_components=3, n_neighbors=n_neighbors, metric=metric, random_state=42)
        embedding = reducer.fit_transform(X_scaled)
        df_umap = pd.DataFrame(embedding, columns=["U1","U2","U3"])
        df_umap["Class"] = df["Class"]
        for cls, color, name in [(2, "blue", "Benign"), (4, "crimson", "Malignant")]:
            d = df_umap[df_umap["Class"] == cls]
            fig.add_trace(go.Scatter3d(x=d["U1"], y=d["U2"], z=d["U3"],
                                       mode="markers", name=name,
                                       marker=dict(size=4, color=color, opacity=0.7)))
        fig.update_layout(scene=dict(xaxis_title="U1", yaxis_title="U2", zaxis_title="U3"))
    fig.update_layout(height=650, margin=dict(l=0,r=0,t=40,b=0))
    return fig

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)