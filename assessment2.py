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

# --- NO CODE BELOW HERE ---

# report runtime
print(f"completed in: {perf_counter() - start_time} seconds")
