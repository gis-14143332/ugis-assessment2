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
        
        
# --- NO CODE BELOW HERE ---

# report runtime
print(f"completed in: {perf_counter() - start_time} seconds")
