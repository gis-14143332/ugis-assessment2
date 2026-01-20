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
    left, bottom, right, top = area_shape.bounds # 找到这个形状的最外圈边界
    while True: # 不断尝试，直到点掉进形状里
        p = Point(random.uniform(left, right), random.uniform(bottom, top)) # 在方框里随机选坐标
        if area_shape.contains(p): return p # 如果点在行政区内，就选定它



# --- NO CODE BELOW HERE ---

# report runtime
print(f"completed in: {perf_counter() - start_time} seconds")
