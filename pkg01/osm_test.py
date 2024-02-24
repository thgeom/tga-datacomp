import win32com.client
import matplotlib.pyplot as plt
import requests

import math
from pkg01.global_var import *
from pkg02.cadlib import *
#from pkg02.cadlib import get_active_document_bounds, get_autocad_variable
from pkg02.geom import *

from PIL import Image
import io
import mercantile
from datetime import datetime
import numpy as np
#from pyproj import Proj, transform

def get_tile_image(tile_url):
    """
    #headers = {'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}
    headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"}
    response = requests.get(tile_url, headers=headers)
    #session = requests.Session()
    #response = session.get(tile_url)
    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"tile url: {tile_url}")
    print(f"response code: {response.status_code}")
    if response.status_code == 418:
        image_data = io.BytesIO(response.content)
        print(image_data.__dir__())
        #image = np.asarray(image_data, dtype=np.float32)
        image = Image.open(image_data)
        print(type(image))
        return image

    else:
        print(f"Failed to fetch tile. Status code: {response.status_code}")
        return None
    """
    # make the request
    #print(f"tile url: {tile_url}")
    with requests.get(tile_url) as resp:
        resp.raise_for_status() # just in case
        img = Image.open(io.BytesIO(resp.content))
    return img


def get_osm_tile_image(lon, lat, zoom):
    #tile_x = int((lon + 180) / 360 * 2 ** zoom)
    #tile_y = int((1 - (lat + 90) / 180) * 2 ** zoom)
    #TILE_SIZE = 256
    lat_rad = math.radians(lat)
    n = (2.0 ** zoom)
    tile_x = int((lon + 180.0) / 360.0 * n)
    tile_y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    #tile_url = f"https://b.tile.openstreetmap.org/{zoom}/{tile_x}/{tile_y}.png"

    tile_url = f"{osm_url}/{zoom}/{tile_x}/{tile_y}.png"
    img = get_tile_image(tile_url)
    img_bbox0 = mercantile.bounds(tile_x, tile_y, zoom)
    #print(f"Tile bbox: {img_bbox0}")
    img_bbox = []
    for i in img_bbox0:
        img_bbox.append(i)
    #print(f"Tile bounds: {img_bbox}")
    return img, img_bbox, f"{zoom}_{tile_x}_{tile_y}"


## To compute zoom level for OSM requesting
def compute_zoom_level(min_lon, min_lat, max_lon, max_lat, screen_width, screen_height):
    # Convert bounding box coordinates to meters
    (min_x, min_y) = proj2utm.transform(min_lon, min_lat)
    (max_x, max_y) = proj2utm.transform(max_lon, max_lat)

    # Calculate the width and height of the bounding box in meters
    bbox_width = max_x - min_x
    bbox_height = max_y - min_y
    #area = (bbox_width * bbox_height) / (screen_width * screen_height)
    #print(f"bbox_width: {bbox_width}")
    #print(f"bbox_height: {bbox_height}")
    # Choose the larger dimension to determine the appropriate zoom level
    bbox_dimension = max(bbox_width, bbox_height)

    ## Define traget zoom constant for testing
    target_zoom_level = 16
    # Calculate the zoom level based on the bounding box dimension and screen width
    zoom_level = target_zoom_level + math.log2((360 / bbox_dimension) * (screen_width / 256))
    #zoom_level = math.floor(8 - math.log(1.6446 * bbox_dimension / math.sqrt(2 * (screen_width * screen_height))) / math.log (2))
    """
    zoom_level = np.interp(x=area,
                     xp=[0, 5**-10, 4**-10, 3**-10, 2**-10, 1**-10, 1**-5],
                     fp=[20, 15,    14,     13,     12,     7,      5])
    """
    return int(zoom_level)

## OSM to AutoCAD
def img_osm2ac():
    global doc

    doc = is_cadready()

    #acprompt = doc.Utility.Prompt
    ms = doc.ModelSpace
    dwg_bounds = get_active_document_bounds()
    dwg_bounds = bbox2geo(dwg_bounds)
    #bbox = dwg_bounds[0:2] + dwg_bounds[2:4]
    bbox = dwg_bounds

    print(f"Dwg. bounds : {bbox}")
    #zoom_level = 14

    min_lon, min_lat, max_lon, max_lat = bbox
    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2

    # Specify the screen dimensions (width and height)
    #screen_width = 800
    #screen_height = 600
    screen_width,screen_height = get_autocad_variable('SCREENSIZE')
    zoom_level = compute_zoom_level(min_lon, min_lat, max_lon, max_lat, screen_width, screen_height)
    print(f"Computed Zoom Level: {zoom_level}")

    ## Requesting for OSM image with its boundaary
    osm_img, bounds, img_name = get_osm_tile_image(center_lon, center_lat, zoom_level)
    bounds_X = bbox2utm(bounds)
    img_size = bounds_X[2] - bounds_X[0]
    #K_img = 1.00254              ### To define factor of EPSG:32647 & 3857  ###
    ## at Zoom level < 15
    ## at Zoom >= 15, K_img = 1.0065
    if zoom_level < 12:
        K_img = 1.00454
    elif zoom_level < 15:
        K_img = 1.0055
    elif zoom_level < 17:
        K_img = 1.0062
    elif zoom_level < 19:
        K_img = 1.0065
    else:
        K_img = 1.0066
    img_size = img_size * K_img

    if osm_img:
        plt.imshow(osm_img)
        plt.title('OpenStreetMaps Tile Preview')
        plt.show()  # Display the image using the default image viewer
        # You can also save the image to a file using image.save('output.png')

    now = datetime.now()                                    # current date and time
    date_time = now.strftime("%m%d%Y%H%M%S")
    #osm_img_path = f"d:/usr/tmp/osm_image_{date_time}.png"  # define temporary file
    osm_img_path = f"{IMAGE_PATHNAME}/osm_{img_name}.png"  # define temporary file as tile
    osm_img.save(osm_img_path)
    #print(f"bounds_X : {bounds_X}")
    image_ent = add_image(osm_img_path, bounds_X[0:2], img_size, 0, 'OSM')
    chProp(image_ent, 70, 15)               # set image to transparency
    doc.Regen(1)
    msg = f"OSM image has been added to AutoCAD drawing.\n" \
          f"{osm_img_path}"
    pycad_prompt(msg)
    # End osm2ac()

## Test OSM
osm_url = "https://tile.openstreetmap.de"
#osm_url = "https://c.tile.openstreetmap.fr/osmfr"
#img_osm2ac()
