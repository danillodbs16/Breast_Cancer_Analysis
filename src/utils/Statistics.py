import numpy as np
# --- Cohen's d function ---
def cohens_d(x, y):
    """Computes the average divergence between sets"""
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return np.nan
    pooled_std = np.sqrt(
        ((nx - 1)*np.var(x, ddof=1) + (ny - 1)*np.var(y, ddof=1)) / (nx + ny - 2)
    )
    if pooled_std == 0:
        return np.nan
    return abs(np.mean(x) - np.mean(y)) / pooled_std
# Centroid distance
def centroid_dist(X,Y):
    """Computes the centroid distance between sets"""
    V=X.mean(axis=0)-Y.mean(axis=0)
    #print(V)
    return (V**2).sum()


def norm_centroid_dist(X, Y):
    """Computes the normalized centroid distance between sets X and Y."""
    # Normalize each set to [0, 1]
    X0 = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-8)
    Y0 = (Y - Y.min(axis=0)) / (Y.max(axis=0) - Y.min(axis=0) + 1e-8)
    
    # Compute centroid difference
    V = X0.mean(axis=0) - Y0.mean(axis=0)
    
    # Return squared Euclidean distance (optional: use np.linalg.norm(V) for actual distance)
    return 10*(V**2).sum()