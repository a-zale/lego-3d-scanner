#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np

import matplotlib
#matplotlib.use('Qt5Agg') # see https://stackoverflow.com/questions/23227129/matplotlib-doesnt-rotate-3d-plots
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LightSource

import pyvista as pv
from pyvista import examples

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file', help='csv file: i;x;y;z')
parser.add_argument('--color', default='orange')
args = parser.parse_args()

###
def denoise(Z):
    # could vectorize this, but that's overkill for now
    for i in range(1,Z.shape[0]-1):
        for j in range(1, Z.shape[1]-1):
            z = Z[i,j]
            nbrs = np.array([ Z[i-1,j], Z[i+1,j], Z[i,j-1], Z[i,j+1]])
            if z > nbrs.max() + 10 or z < nbrs.min() - 10:
                Z[i,j] = nbrs.mean()
    return Z
###
pts = pd.read_csv(args.file, sep=';', names=['i', 'x', 'y', 'z'], header=0, index_col='i').to_numpy()
x, y, z = pts[:,0], pts[:,1], pts[:,2]
nx, ny = len(np.unique(x)), len(np.unique(y))

def grid(series):
    g = np.full(nx*ny, np.nan)
    g[:len(series)] = series
    return g.reshape(nx,ny)

X, Y, Z = grid(x), grid(y), grid(z)
Z = denoise(Z)

#grid = pv.StructuredGrid(-X, -Y, Z)
#grid.plot()

#x = np.arange(-10, 10, 0.25)
#y = np.arange(-10, 10, 0.25)
#x, y = np.meshgrid(x, y)
#r = np.sqrt(x**2 + y**2)
#z = np.sin(r)

#cubemap = examples.download_sky_box_cube_map()
plotter = pv.Plotter()
grid = pv.StructuredGrid(X, -Y, Z)
#plotter.add_actor(cubemap.to_skybox())
light = pv.Light(position=(-960,-1100,400), intensity=3, show_actor=True, positional=False, shadow_attenuation=.5)
#plotter.set_environment_texture(cubemap)  # For reflecting the environment off the mesh
#plotter.add_mesh(grid, color='blue', pbr=True, metallic=0.0, roughness=.6, diffuse=1, split_sharp_edges=True)
#plotter.add_light(light)
#plotter.enable_shadows()
#plotter.set_background('grey')

plotter.add_mesh(grid, color=args.color)

plotter.enable_terrain_style(mouse_wheel_zooms=True)
plotter.show()

#fig = plt.figure()
#ax = plt.axes(projection='3d')

#ls = LightSource(azdeg=0, altdeg=70)
#rgb = ls.shade(Z, plt.cm.BuPu)

#ax.plot_trisurf(-y, -x, z, facecolors=rgb) #color=args.color)
#ax.plot_surface(-Y,X,Z, facecolors=rgb, rstride=1, cstride=1, linewidth=0, antialiased=False)
#plt.axis('equal')
#plt.show()
