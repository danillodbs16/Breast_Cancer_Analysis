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
    cmap="tab10"
):
    """
    Plots a 3D scatter plot using plotly.graph_objects.
    """

    X = np.array(X)
    y = np.array(y)

    # Unique labels
    labels = np.unique(y)

    # FIXED: proper matplotlib → plotly color conversion
    if color_map is None:
        cmap_obj = plt.get_cmap(cmap)
        color_map = {}
        for i, label in enumerate(labels):
            r, g, b, a = cmap_obj(i / max(len(labels)-1, 1))
            color_map[label] = f"rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {a})"

    # Create a trace for each label
    traces = []
    for label in labels:
        mask = y == label

        # Keep original label unless mapping is provided
        display_name = label_map[label] if label_map else str(label)

        traces.append(
            go.Scatter3d(
                x=X[mask, 0],
                y=X[mask, 1],
                z=X[mask, 2],
                mode='markers',
                name=display_name,
                marker=dict(
                    size=5,
                    opacity=0.8,
                    color=color_map.get(label, "gray"),
                    line=dict(width=0)
                )
            )
        )

    # Create the figure
    fig = go.Figure(data=traces)

    # Update layout
    fig.update_layout(
        scene=dict(
            xaxis_title="X-axis",
            yaxis_title="Y-axis",
            zaxis_title="Z-axis"
        ),
        title=title,
        legend_title=legend_title
    )

    fig.show()
