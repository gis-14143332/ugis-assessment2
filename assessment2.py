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
import geopandas
import rasterio
import random
from shapely.geometry import Point, Polygon, MultiPolygon

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

# --- NO CODE BELOW HERE ---

# report runtime
print(f"completed in: {perf_counter() - start_time} seconds")
