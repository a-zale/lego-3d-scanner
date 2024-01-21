#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np
import pyvista as pv
import argparse

def denoise(Z):
    """
    Z is a 2D array.
    Simple outlier correction by comparing each interior point with its 4 neighbors.
    In-place.
    """
    nx, ny = Z.shape
    sub = Z[1:-1,1:-1]
    nbrs = np.array([ Z[1+i:nx-1+i, 1+j:ny-1+j] for i,j in [(-1,0), (1,0), (0,-1), (0,1)] ])
    is_outlier = (sub > nbrs.max(0) + 10) | (sub < nbrs.min(0) - 10)
    sub[is_outlier] = nbrs.mean(0)[is_outlier]
    return Z

def grid(x, y, z):
    """
    1D x, y, z -> 2D X, Y, Z defined on grid
    """
    xvals, yvals = np.sort(np.unique(x)), np.sort(np.unique(y))
    nx, ny = len(xvals), len(yvals)
    x2i = { v:i for i,v in enumerate(xvals)  }
    y2i = { v:i for i,v in enumerate(yvals)  }
    X, Y, Z = ( np.full((nx, ny), np.nan) for _ in range(3) )
    # scanner loops over x (outer) and y (inner), and y may stop early if the calibration sensor triggers the carriage return
    # to-do: vectorize
    for i in range(len(x)):
        xval, yval, zval = ( vec[i] for vec in (x,y,z) )
        idx = (x2i[xval], y2i[yval])
        X[idx], Y[idx], Z[idx] = xval, yval, zval
    return X, Y, Z

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE.csv', help='path to semicolon-delimited file: i;x;y;z')
    parser.add_argument('--color', default='orange', help='color of the mesh')
    parser.add_argument('--denoise', dest='denoise', action='store_true', help='apply simple outlier correction to z values')
    parser.add_argument('--points', dest='points', action='store_true', help='plot as points instead of mesh')
    parser.add_argument('--save-orbit', dest='orbit', metavar='FILE.gif', help='save an animation of the object rotating')
    args = parser.parse_args()

    pts = pd.read_csv(args.file, sep=';', names=['i', 'x', 'y', 'z'], header=0, index_col='i').to_numpy()
    x, y, z = pts[:,0], pts[:,1], pts[:,2]
    X, Y, Z = grid(x, y, z)
    if args.denoise:
        denoise(Z)

    p = pv.Plotter()
    if args.points:
        p.add_points(np.column_stack([X.flatten(), -Y.flatten(), Z.flatten()]), color=args.color)
    else:
        p.add_mesh(pv.StructuredGrid(X, -Y, Z), color=args.color)
    p.enable_terrain_style(mouse_wheel_zooms=True)

    if args.orbit:
        viewup = [.1, .1, 1] # normal to orbital plane
        centroid = [x.mean(), -y.mean(), z.mean()]
        orbit_time = 2.5 # in seconds

        path = p.generate_orbital_path(factor=2.0, n_points=60, viewup=viewup, shift=centroid[2]*20.0)
        p.open_gif(args.orbit)
        print("Please wait until progress is 100% to close the plot.")
        p.orbit_on_path(path, write_frames=True, focus=centroid, step=(orbit_time/60.), progress_bar=True)
        p.show()
        p.close()
        print(f"Created {args.orbit}")
    else:
        p.show()

if __name__ == "__main__":
    main()
