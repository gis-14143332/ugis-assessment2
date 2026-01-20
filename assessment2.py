"""
Understanding GIS: Assessment 2
@author [14143332]
"""
from time import perf_counter

# set start time
start_time = perf_counter()	

# --- NO CODE ABOVE HERE ---


''' --- ALL CODE MUST BE INSIDE HERE --- '''
#import
import os
import geopandas as gpd
import rasterio
import random
from shapely.geometry import Point, Polygon, MultiPolygon
from matplotlib.path import Path
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import contextily as cx
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import PathPatch
import seaborn as sns
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.lines import Line2D


#basic rule
map_standard = "EPSG:3857"


#find data
my_data_folder = os.path.dirname(os.path.abspath(__file__)) #find which file this code in
def find_my_file(name): 
    return os.path.join(my_data_folder, 'data', 'wr', name) 

#random point in study area
def make_random_dot(area_shape): 
    left, bottom, right, top = area_shape.bounds # find boundary
    while True: # try until in shape
        p = Point(random.uniform(left, right), random.uniform(bottom, top)) # random position in square
        if area_shape.contains(p): return p # if in study area,choose
        
#check this point's population data
def look_at_population(p, raster_file, raster_data): 
    try:
        row, col = raster_file.index(p.x, p.y) # transfer longtitude&lattitude to xy
        # check number
        if 0 <= row < raster_file.height and 0 <= col < raster_file.width:
            return max(0, float(raster_data[row, col])) 
        return 0.0
    except: return 0.0 #if wrong
    
# convert map shape to drawing path,make rigion of interest
def shape_to_drawing_path(area_shape): 
    # multipul blocks
    all_parts = [area_shape] if isinstance(area_shape, Polygon) else area_shape.geoms 
    points_list, move_codes = [], [] # put coordination and drawing instruction
    for part in all_parts:
        points_list.extend(list(zip(*part.exterior.coords.xy))) #record outside frame' coordination
        move_codes.extend([Path.MOVETO] + [Path.LINETO] * (len(part.exterior.coords.xy[0]) - 1))
    return Path(points_list, move_codes) 

# load roi and tweet data ,standardize coordinates
city_districts = gpd.read_file(find_my_file("gm-districts.shp")).to_crs(map_standard) 
twitter_data = gpd.read_file(find_my_file("level3-tweets-subset.shp")).to_crs(map_standard) 
# spatial joint, find which district every tweet belongs to
combined_data = gpd.sjoin(twitter_data, city_districts, how="inner", predicate="within") 
final_new_dots = []

# open population density file
how_many_dots = 20 # every tweet generate radom points
with rasterio.open(find_my_file("100m_pop_2019.tif")) as pop_img: 
    pop_values = pop_img.read(1) # read picture first layer's data
    for _, each_row in combined_data.iterrows():
        this_area = city_districts.loc[each_row['index_right']].geometry # find the rigion this tweet in
        # generate points for each tweet, choose the one with highest population density
        best_candidates = [(p, look_at_population(p, pop_img, pop_values)) for p in [make_random_dot(this_area) for _ in range(how_many_dots)]]
        final_new_dots.append(max(best_candidates, key=lambda x: x[1])[0]) # choose the point with highest weight
        
redistributed_result = combined_data.copy().set_geometry(final_new_dots)#update new coordination       

#output
#big map to compare
fig, (left_map, right_map) = plt.subplots(1, 2, figsize=(24, 12), subplot_kw={'projection': ccrs.Mercator()}) 
map_view_limit = city_districts.total_bounds #extension

# beautify
def make_map_pretty(ax, main_title): 
    #make buffer
    ax.set_extent([map_view_limit[0]-2000, map_view_limit[2]+2000, map_view_limit[1]-2000, map_view_limit[3]+2000], crs=ccrs.Mercator())
    # add light city background
    cx.add_basemap(ax, crs=map_standard, source=cx.providers.CartoDB.Positron) 
    #add roi line & titiel
    city_districts.plot(ax=ax, facecolor='none', edgecolor='#444444', lw=1, zorder=3) # draw roi line
    ax.set_title(main_title, fontsize=16, fontweight='bold', pad=15)  
    
    # draw gird
    gl = ax.gridlines(draw_labels=True, linewidth=0, alpha=0) 
    gl.top_labels = gl.right_labels = False 
    gl.ylabel_style = {'rotation': 90} # Y grid number vertical
    gl.xformatter, gl.yformatter = LONGITUDE_FORMATTER, LATITUDE_FORMATTER #set auto coordinate unit
    
# false hotspot left
make_map_pretty(left_map, "A. Original Data: False Hotspots")
twitter_data.plot(ax=left_map, color='#00008B', markersize=40, marker='x', alpha=0.8, zorder=6) 
        
# right map: redistribute
make_map_pretty(right_map, "B.Redistributed Surface(Weighted Aalysis)")

red_color_map = LinearSegmentedColormap.from_list("MyReds", ["#ffffff", "#ffcccc", "#ff4d4d"]) 
#mask clip
clipping_mask = PathPatch(shape_to_drawing_path(city_districts.geometry.unary_union), transform=right_map.transData, fc='none', ec='none')
right_map.add_patch(clipping_mask) 

# Filled thermal surface,30 levels
kde_surface = sns.kdeplot(x=redistributed_result.geometry.x, y=redistributed_result.geometry.y, ax=right_map, fill=True, levels=30, cmap=red_color_map, alpha=0.9, zorder=2)
# contour lines
sns.kdeplot(x=redistributed_result.geometry.x, y=redistributed_result.geometry.y, ax=right_map, fill=False, levels=30, color='#DE6954', lw=0.5, alpha=0.6, zorder=2.5)

# strech bar
color_axis = make_axes_locatable(right_map).append_axes("right", size="3%", pad=0.1, axes_class=plt.Axes)
plt.colorbar(plt.cm.ScalarMappable(cmap=red_color_map), cax=color_axis, label='Estimated Interes Density') 

# restrain to roi
for collection in kde_surface.collections + right_map.collections: 
    collection.set_clip_path(clipping_mask) 
# add redistributed plots on hotspot
redistributed_result.plot(ax=right_map, color='#2c2c2c', markersize=1.5, alpha=0.4, zorder=5) 

# add north arrow & 10 km scla bar
right_map.annotate('N', xy=(0.95, 0.93), xytext=(0.95, 0.85), arrowprops=dict(facecolor='black', width=4), ha='center', va='center', fontsize=12, fontweight='bold', xycoords=right_map.transAxes)
right_map.plot([map_view_limit[0]+2000, map_view_limit[0]+12000], [map_view_limit[1], map_view_limit[1]], color='k', lw=3, transform=ccrs.Mercator()) 
right_map.text(map_view_limit[0]+7000, map_view_limit[1]+500, "10 km", ha='center', fontweight='bold', transform=ccrs.Mercator())

# legend
legend_items = [Line2D([0], [0], marker='x', color='#00008B', linestyle='None', ms=10, label='False Hotspot'),
                Line2D([0], [0], marker='o', color='#2c2c2c', linestyle='None', ms=5, alpha=0.5, label='Restributed Points'),
                Line2D([0], [0], color='#ff4d4d', lw=8, label='Intrerest Density Surface')]
right_map.legend(handles=legend_items, loc='upper left', frameon=True) # left up corner






# --- NO CODE BELOW HERE ---

# report runtime
print(f"completed in: {perf_counter() - start_time} seconds")
