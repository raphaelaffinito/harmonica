"""
Layer of prisms
===============
"""
import pyproj
import numpy as np
import verde as vd
import harmonica as hm
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


# Read South Africa topography
south_africa_topo = hm.datasets.fetch_south_africa_topography()

# Project the grid
projection = pyproj.Proj(proj="merc", lat_ts=south_africa_topo.latitude.values.mean())
south_africa_topo = vd.project_grid(south_africa_topo.topography, projection=projection)

# Create a 2d array with the desntiy of the prisms Points above the geoid will
# have a density of 2670 kg/m^3 Points below the geoid will have a density
# contrast equal to the difference between the density of the ocean and the
# density of the upper crust: # 1000 kg/m^3 - 2900 kg/m^3
density = south_africa_topo.copy()  # copy topography to a new xr.DataArray
density.values[:] = 2670.0  # replace every value for the density of the topography
# Change density values of ocean points
density.where(south_africa_topo >= 0, 1000 - 2900)

# Create layer of prisms
prisms = hm.prisms_layer(
    (south_africa_topo.easting, south_africa_topo.northing),
    surface=south_africa_topo.values,
    reference=0,
    properties={"density": density},
)

prisms.top.plot()
plt.gca().set_aspect("equal")
plt.show()

prisms.bottom.plot()
plt.gca().set_aspect("equal")
plt.show()

# Compute gravity field on a regular grid located at 2000m above the ellipsoid
coordinates = vd.grid_coordinates(
    region=(12, 33, -35, -18), spacing=0.2, extra_coords=2000
)
easting, northing = projection(*coordinates[:2])
coordinates_projected = (easting, northing, coordinates[-1])
prisms_gravity = hm.prism_gravity(
    coordinates_projected, prisms.prisms_layer.get_prisms(), prisms.density, field="g_z"
)

# Make a plot of the computed gravity
plt.figure(figsize=(7, 6))
ax = plt.axes()
#  ax = plt.axes(projection=ccrs.Mercator())
tmp = ax.pcolormesh(*coordinates[:2], prisms_gravity)
ax.set_title("Terrain gravity effect")
plt.colorbar(tmp, label="mGal")
ax.set_aspect("equal")
plt.tight_layout()
plt.show()