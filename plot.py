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

def grid(series, nx, ny):
    """
    Shapes a 1D series of length <= nx*ny to (nx,ny)
    """
    g = np.full(nx*ny, np.nan)
    g[:len(series)] = series
    return g.reshape(nx,ny)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='csv file: i;x;y;z')
    parser.add_argument('--color', default='orange')
    parser.add_argument('--denoise', dest='denoise', action='store_true')
    args = parser.parse_args()

    pts = pd.read_csv(args.file, sep=';', names=['i', 'x', 'y', 'z'], header=0, index_col='i').to_numpy()
    x, y, z = pts[:,0], pts[:,1], pts[:,2]
    nx, ny = len(np.unique(x)), len(np.unique(y))
    X, Y, Z = grid(x, nx, ny), grid(y, nx, ny), grid(z, nx, ny)
    if args.denoise:
        denoise(Z)

    p = pv.Plotter()

    g = pv.StructuredGrid(X, -Y, Z)
    p.add_mesh(g, color=args.color)
    p.enable_terrain_style(mouse_wheel_zooms=True)
    p.show()

if __name__ == "__main__":
    main()
