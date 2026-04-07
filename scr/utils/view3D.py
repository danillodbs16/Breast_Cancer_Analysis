import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt

def plot_3d_plotly(
    X,
    y,
    title="3D Scatter Plot",
    label_map=None,
    legend_title="Legend",
    color_map=None,
    cmap="tab10",
    width=800,
    height=600,
    save_path=None
):
    X = np.array(X)
    y = np.array(y)
    labels = np.unique(y)

    if color_map is None:
        cmap_obj = plt.get_cmap(cmap)
        color_map = {}
        for i, label in enumerate(labels):
            r, g, b, a = cmap_obj(i / max(len(labels)-1, 1))
            color_map[label] = f"rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {a})"

    traces = []
    for label in labels:
        mask = y == label
        display_name = label_map[label] if label_map else str(label)

        traces.append(
            go.Scatter3d(
                x=X[mask, 0],
                y=X[mask, 1],
                z=X[mask, 2],
                mode='markers',
                name=display_name,
                marker=dict(size=5, opacity=0.8, color=color_map.get(label, "gray"), line=dict(width=0))
            )
        )

    fig = go.Figure(data=traces)
    fig.update_layout(
        width=width,
        height=height,
        scene=dict(
            xaxis_title="X-axis",
            yaxis_title="Y-axis",
            zaxis_title="Z-axis"
        ),
        title=title,
        legend_title=legend_title
    )

    # Save HTML if path is provided
    if save_path:
        fig.write_html(save_path)
        print(f"Plot saved as {save_path}")

    fig.show()
    return fig  # <- now you can store it