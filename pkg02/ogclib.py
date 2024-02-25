import requests
import json
import xmltodict

import geopandas as gpd
import matplotlib.pyplot as plt
from datetime import datetime

from pkg02.cadlib import *
from pkg02.geom import *
#from pkg01.url_req import geoDF2ac

from PIL import Image
import io, sys
import mercantile
from tkinter import filedialog as fd

## To compute zoom level for Tile requesting
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

## WFS Class
class WfsProperties:
    def __init__(self, wfs_url, service, version):
        self.wfs_url = wfs_url
        self.service = service
        self.version = version

    def getlayer(self):
        #wfs_request_url = f"{self.wfs_url}?service={self.service}&version={self.version}&request=GetCapabilities"
        wfs_request_params = {'service':self.service, 'version':self.version,'request':'GetCapabilities'}
        # Create a GeoJSON layer using the updated WFS GetCapabilities request
        try:
            #wfs_byte = requests.get(wfs_request_url, timeout=20)
            ## Test for sending params to requests
            wfs_byte = requests.get(self.wfs_url, params=wfs_request_params, timeout=20)
        except requests.exceptions.Timeout:
            print("Request to WFS timed out. Try again later or reduce the data scope.")
            wfs_byte = None
        except requests.exceptions.ConnectionError:
            print('WFS error occurred, no WFS data!!!!')
            wfs_byte = None
        except Exception:
            print('An error occurred, no WFS data!!!!')
            wfs_byte = None

        if wfs_byte:
            wfs_str = wfs_byte.content.decode('utf8')
            #print(type(wfs_str))
            try:
                # Convert XML to dictionary
                xml_dict = xmltodict.parse(wfs_str)

                # Convert dictionary to JSON
                json_string = json.dumps(xml_dict, indent=2)
                json_data = json.loads(json_string)
            except:
                json_data = None

        if json_data:
            #wfs_result = json_data
            layer_list_dict = []
            featureTypes = json_data['wfs:WFS_Capabilities']['FeatureTypeList']['FeatureType']
            for typ in featureTypes:
                layer_list_dict.append(typ)
            layer_list = []
            for layer in layer_list_dict:
                layer_list.append(layer['Name'])

            self.layers = layer_list
        else:
            self.layers = None

    def getdata(self, wfs_layer, max_fea, viewpar, bounds, crs='EPSG:4326', srsname='EPSG:4326'):
        self.srsname = srsname
        self.bounds = bounds
        #self.layer = wfs_layer.rsplit(':')[1]    ## Get layer name
        try:
            layer = f"group_{wfs_layer.rsplit(',')[0]}"
        except:
            layer = wfs_layer.rsplit(':')[1]

        #print(f"temp layer: {layer}")
        try:
            layer = layer.rsplit(':')[1]
        except:
            None

        #print(f"temp2 layer: {layer}")
        if not layer:
            layer = 'WFS_LAYER'
        self.layer = layer

        #print(f"bounds[0][0]: {bounds[0][0]}")
        # Craft your new WFS GetFeature request URL based on the new extent
        #wfs_request_url = f"{self.wfs_url}?service={self.service}&version={self.version}&request=GetFeature&typeName={wfs_layer}&viewparams={viewpar}" \
        #                  f"&count={max_fea}&bbox={bounds[0]},{bounds[1]},{bounds[2]},{bounds[3]},{crs}&outputFormat=json&srsname=urn:x-ogc:def:crs:{srsname}"
        wfs_request_params = {'service':self.service, 'version':self.version, 'request':'GetFeature', 'typeName':wfs_layer, 'viewparams':viewpar,
                              'count':max_fea, 'bbox':f"{bounds[0]},{bounds[1]},{bounds[2]},{bounds[3]},{crs}", 'outputFormat':'json', 'srsname':f"urn:x-ogc:def:crs:{srsname}"}
        #print(f"wfs parama: {wfs_request_params}")
        #print("WFS Request:", wfs_request_url)
        print("WFS Url:", self.wfs_url)
        print("Req. bounds:", self.bounds)
        try:
            #wfs_byte = requests.get(wfs_request_url, timeout=20)
            ## Sending request with params
            wfs_byte = requests.get(self.wfs_url, params=wfs_request_params, timeout=20)
        except requests.exceptions.Timeout:
            print("Request to WFS timed out. Try again later or reduce the data scope.")
            wfs_byte = None
        except requests.exceptions.RequestException:
            print('WFS error occurred, no parcel data!!!!')
            wfs_byte = None
        except Exception:
            print('An error occurred, no parcel data!!!!')
            wfs_byte = None

        if wfs_byte:
            wfs_str = wfs_byte.content.decode('utf8')
            #print(wfs_str)
            try:
                d_json = json.loads(wfs_str)
                #print(d_json['numberReturned'])
                if d_json['numberReturned'] == 0:
                    d_json = None
            except:
                d_json = None

            self.json_data = d_json
            if self.json_data:
                self.geodf = gpd.GeoDataFrame.from_features(self.json_data, crs=srsname)
            else:
                self.geodf = None
        else:
            self.json_data = None
            self.geodf = None

    def to_shp(self, file_out=None):
        if not file_out:
            file_out = fd.asksaveasfilename(title='Define Output File',filetypes=[("Shp file", "*.shp")])
        #selected_columns = ['bldg_id', 'geometry', 'id']
        #self.geodf[selected_columns].to_file(file_out, driver='ESRI Shapefile')
        self.geodf.to_file(file_out, driver='ESRI Shapefile')


## WMS Class
class WmsProperties:
    def __init__(self, wms_url, service, version):
        self.wms_url = wms_url
        self.service = service
        self.version = version

    def getdata(self, wms_layer, viewparams, npixel, bounds, crs='EPSG:4326', srsname='EPSG:4326'):
        self.srsname = srsname
        #self.bounds = bounds
        x_size = bounds[2] - bounds[0]
        y_size = bounds[3] - bounds[1]
        m_size = max(x_size, y_size)    # compute max. size of X&Y
        #print(f"m_size: {m_size}")
        ur = [bounds[0] + m_size, bounds[1] + m_size]
        # Craft your new WMS GetMap request URL based on the new extent
        wms_request_url = f"{self.wms_url}?service={self.service}&version={self.version}&request=GetMap&layers={wms_layer}&viewparams={viewparams}&WIDTH={npixel}&HEIGHT={npixel}" \
                          f"&bbox={bounds[0]},{bounds[1]},{ur[0]},{ur[1]}&crs={crs}&format=image/jpeg&transparent=TRUE&srsname={srsname}&exceptions=application/vnd.ogc.se_inimage"
        self.bounds = [bounds[0],bounds[1], ur[0], ur[1]]
        self.img_size = m_size

        # Define WMS layer
        try:
            layer = f"group_{wms_layer.rsplit(',')[0]}"
        except:
            layer = wms_layer.rsplit(':')[1]

        #print(f"temp layer: {layer}")
        try:
            layer = layer.rsplit(':')[1]
        except:
            layer = None

        #print(f"temp2 layer: {layer}")
        if layer is None:
            layer = 'WMS_LAYER'
        self.layer = layer

        #print(f"self.bounds getdata: {self.bounds}")
        # Print or process the WMS request URL as needed
        print("WMS Request:", wms_request_url)
        try:
            wms_byte = requests.get(wms_request_url, timeout=20)
        except requests.exceptions.Timeout:
            print("Request to WMS timed out. Try again later or reduce the data scope.")
            wms_byte = None
        except requests.exceptions.ConnectionError:
            print('WMS error occurred, no parcel data!!!!')
            wms_byte = None
        except Exception:
            print('An error occurred, no parcel data!!!!')
            wms_byte = None

        if wms_byte:
            wms_img = wms_byte.content

            if wms_img:
                img_data = Image.open(io.BytesIO(wms_img))
                self.img_data = img_data                    # in jpeg format
        else:
            self.img_data = None


    def img_to_acad(self, img_file_location):
        #print(f"self.bounds img_to_acad : {self.bounds}")
        bounds = self.bounds
        #bounds_X = bbox2utm([bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1]])
        #bounds_X = [bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1]]
        bounds_X = bounds
        img_size = bounds_X[2] - bounds_X[0]

        now = datetime.now()                                    # current date and time
        date_time = now.strftime("%m%d%Y%H%M%S")
        #wms_img_path = f"d:/usr/tmp/wms_image_{date_time}.png"  # define temporary file
        wms_img_path = f"{img_file_location}/wms_image_{date_time}.png"  # define temporary file as tile
        self.img_data.save(wms_img_path)
        #print(f"bounds_X : {bounds_X}")
        image_ent = add_image(wms_img_path, [bounds_X[0],bounds_X[1]], img_size, 0, f'WMS_{self.layer}')
        chProp(image_ent, 70, 15)               # set image to transparency
        doc.Regen(1)
        print(f"WMS image has been added to AutoCAD drawing.")
        # End img_to_acad()

## Tile Class
class TileProperties:
    def __init__(self, name):
        #self.tile_url = tile_url
        self.name = name
        self.osm_url = "https://tile.openstreetmap.de"
        self.ggs_url = "https://mt1.google.com/vt/lyrs=s@189&hl=en"
        self.ggm_url = "https://mt1.google.com/vt/lyrs=m@113&hl=en"
        #self.version = version

    ## Get tile image
    def get_tile_image(self, tile_req_url, echo_msg=False):
        # make the request
        if echo_msg:
            print(f"tile req url: {tile_req_url}")
        with requests.get(tile_req_url) as resp:
            resp.raise_for_status() # just in case
            img = Image.open(io.BytesIO(resp.content))
        self.img = img

    ## Get lonlat tile image
    def get_tile_lonlat_zoom(self, lon, lat, zoom):
        #tile_x = int((lon + 180) / 360 * 2 ** zoom)
        #tile_y = int((1 - (lat + 90) / 180) * 2 ** zoom)
        #TILE_SIZE = 256
        lat_rad = math.radians(lat)
        n = (2.0 ** zoom)
        tile_x = int((lon + 180.0) / 360.0 * n)
        tile_y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        # Ensure tile_y is within valid range [0, 2^zoom - 1]
        tile_y = max(0, min(tile_y, n - 1))
        #tile_url = f"https://b.tile.openstreetmap.org/{zoom}/{tile_x}/{tile_y}.png"

        #lonlatzoom_tile = f"&&x={tile_x}&y={tile_y}&z={zoom}"
        #img = self.get_tile_image(tile_url)
        #img_bbox0 = mercantile.bounds(tile_x, tile_y, zoom)   # 4326
        #img_bbox0 = tile_boundary_coordinates(tile_x, tile_y, zoom)
        img_bbox0 = mercantile.xy_bounds(tile_x, tile_y, zoom) #3857
        #print(f"Tile bbox: {img_bbox0}")
        img_bbox = []
        for i in img_bbox0:
            img_bbox.append(i)
        #print(f"Tile bounds: {img_bbox}")
        self.bounds = img_bbox
        self.z = zoom
        self.x = tile_x
        self.y = tile_y
        self.name = f"{zoom}_{tile_x}_{tile_y}"


    ## getdata by given bbox
    def getdata(self, bbox):
        min_lon, min_lat, max_lon, max_lat = bbox[0][0],bbox[0][1],bbox[1][0],bbox[1][1]
        center_lon = (min_lon + max_lon) / 2
        center_lat = (min_lat + max_lat) / 2

        # Specify the screen dimensions (width and height)
        #screen_width = 800
        #screen_height = 600
        screen_width,screen_height = get_autocad_variable('SCREENSIZE')
        z = compute_zoom_level(min_lon, min_lat, max_lon, max_lat, screen_width, screen_height)
        print(f"Computed Zoom Level: {z}")

        ## Requesting for image with its boundaary
        self.get_tile_lonlat_zoom(center_lon, center_lat, z)
        self.get_tile_image(f"{self.ggs_url}&&x={self.x}&y={self.y}&z={self.z}")
        self.ggs_img = self.img
        #self.get_tile_image(f"{self.ggm_url}&&x={self.x}&y={self.y}&z={self.z}")
        #self.ggm_img = self.img
        #self.get_tile_image(f"{self.osm_url}/{self.z}/{self.x}/{self.y}.png")
        #self.osm_img = self.img

    ## getdata by given z, x, y
    def getdata_zxy(self, layer, z, x, y):
        self.z = z
        self.x = x
        self.y = y
        self.tile_name = f"{layer}_{z}_{x}_{y}"
        img_bbox0 = mercantile.xy_bounds(x, y, z) #3857
        #print(f"Tile bbox: {img_bbox0}")
        img_bbox = []
        for i in img_bbox0:
            img_bbox.append(i)
        #print(f"Tile bounds: {img_bbox}")
        self.bounds = img_bbox

        ## Requesting for image with its boundaary
        if layer == 'GGS':
            self.get_tile_image(f"{self.ggs_url}&&x={self.x}&y={self.y}&z={self.z}")
            self.ggs_img = self.img
        elif layer == 'GGM':
            self.get_tile_image(f"{self.ggm_url}&&x={self.x}&y={self.y}&z={self.z}")
            self.ggm_img = self.img
        elif layer == 'OSM':
            self.get_tile_image(f"{self.osm_url}/{self.z}/{self.x}/{self.y}.png")
            self.osm_img = self.img

    def img_to_acad(self, img_file_location, img_type, img_layer):
        bounds_X = bbox_mer2utm(self.bounds)
        dx = bounds_X[2] - bounds_X[0]              # Meters for CRS
        dy = bounds_X[3] - bounds_X[1]
        #print(f"dX, dY : ({dx}, {dy})")
        #img_size = (dx + dy) / 2.0
        img_size = max(dx, dy)
        #img_path = f"{img_file_location}/{img_layer}_{self.z}_{self.x}_{self.y}.gif"  # [gif,tga,bmp,tif] define temporary file as tile
        img_path = f"{img_file_location}/{self.tile_name}.gif"  # [gif,tga,bmp,tif] define temporary file as tile
        try:
            img_type.save(img_path)
        except PermissionError as e:
            print(f"[{img_path}] already exist with: {e}.")

        #print(f"bounds_X : {bounds_X}")
        ### Factor for Tiled Images to AutoCAD.
        ### To be adjusted
        K_img = 1.000                 ## Factor for image size to AutoCAD !!!
        image_ent = add_image(img_path, bounds_X[0:2], K_img * img_size, 0, img_layer, check=False)

        # Check if image entity creation is complete
        while image_ent and not is_entity_creation_complete(doc, image_ent):
            print("Image entity creation is still in progress. Waiting...")
            time.sleep(1)

        if image_ent:
            chProp(image_ent, 70, 15)               # set image to off & transparency
            #doc.Regen(1)
            #print(f"[{img_layer}] Tile Image has been added to AutoCAD drawing.")
            #matrix = image_ent.GetTransform()
            #print(f"matrix: {matrix}")
            #print(f"image_ent: {image_ent.__dir__()}")
            #print(f"Width: {image_ent.ImageWidth}")
            #print(f"Height: {image_ent.ImageHeight}")
            #print(f"ScaleEntity: {image_ent.ScaleEntity.__dir__()}")
            # u_vector = (dx / 256, 0, 0)  # Example U-vector, change as needed
            # v_vector = (0, dy / 256, 0)  # Example V-vector, change as needed

            image_ent.ScaleFactor = max(dx, dy)
            #image_ent.ImageWidth = dx
            #print(f"Image Height: {image_ent.ImageHeight}")
            ## Check Image size (dx & dy)
            ## **** To be TESTED ****
            if dx < dy:
                image_ent.ImageHeight = (dx + dy) / 2
                if (dy-dx)>(dx/256):
                    adj_x = 0
                    adj_y = (dy - dx) / 4
                else:
                    adj_x = (dy - dx) / 2
                    adj_y = 0
                #image_ent.ImageWidth = image_ent.ImageWidth + (dx / 256)  ## Added by 1 pixel
                image_ent.ImageHeight = image_ent.ImageHeight - adj_y + (dy / 512)
                #print(f"Corr. Image Height: {image_ent.ImageHeight}")
                image_ent.ImageWidth = image_ent.ImageWidth + adj_x + (dx / 512)  ## Adjusted by dx&dy

            else:
                if (dx-dy)>(dx/256):
                    adj_x = 0
                    adj_y = (dx - dy) / 4
                else:
                    adj_x = (dx - dy) / 2
                    adj_y = 0
                image_ent.ImageHeight = image_ent.ImageHeight - adj_y + (dy / 512)
                #print(f"Corr. Image Height: {image_ent.ImageHeight}")
                image_ent.ImageWidth = image_ent.ImageWidth + adj_x + (dx / 512)  ## Deduced by dx&dy


            return image_ent
        else:
            print(f"Any error occurred, the image is not in drawing!!!")
            return -1
            #sys.exit(-1)
        # End img_to_acad()


# Test WfsProperties
#global doc

#ows_url = "https://landsmaps.dol.go.th/geoserver/LANDSMAPS/ows"
#ows_url = "https://geoserver.thgeom-academy.com/geoserver/thgeom/ows"
#dol_layers = "V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL48_LANDNO,V_PARCEL48_LANDNO,V_PARCEL48_LANDNO,V_PARCEL48_LANDNO"
#dol_viewparams = "utmmap:51363,utmmap:51364,utmmap:50362,utmmap:50361,utmmap:52373,utmmap:52372,utmmap:51361,utmmap:51362,utmmap:52363,utmmap:52364,utmmap:56411,utmmap:56412,utmmap:57413,utmmap:57414"


#wfsObj = WfsProperties(ows_url, 'wfs', '2.0.0')
#wfsObj.getlayer()
#print(wfsObj.layers)


#doc = is_cadready()
#dwg_bounds = get_active_document_bounds()
#print(f"dwg_bounds from AC: {dwg_bounds}")
#dwg_bounds_deg = bbox2geo(dwg_bounds)
#print(f"deg_bounds: {dwg_bounds}")



def test_wfs():
    wfsObj = WfsProperties(ows_url, 'wfs', '2.0.0')
    wfsObj.getdata("thgeom:BLDG_new_region", 10000, '', dwg_bounds, crs=ACAD_CRS, srsname=ACAD_CRS)
    #print(wfsObj.json_data)
    wfsObj.geodf.plot()
    plt.title(f"[{wfsObj.geodf.shape[0]} features] : Web Feature Service Preview")
    plt.show()
    #geoDF2ac(wfsObj.geodf, wfsObj.layer, 'id')
    #wfsObj.to_shp()

#test_wfs()

def test_wms():
    wmsObj = WmsProperties(ows_url, 'wms', '1.3.0')

    #wmsObj.getdata("thgeom:BLDG_new_region", '', 512, [dwg_bounds[0:2], dwg_bounds[2:4]], crs='EPSG:32647', srsname='EPSG:32647')
    #wmsObj.getdata(dol_layers, dol_viewparams, 512, [dwg_bounds[0:2], dwg_bounds[2:4]], crs='EPSG:32647', srsname='EPSG:32647')

    #print(f"dwg_bounds: {dwg_bounds}")
    wmsObj.getdata("thgeom:province", '', 512, dwg_bounds, crs=ACAD_CRS, srsname=ACAD_CRS)

    plt.imshow(wmsObj.img_data)
    plt.title('Web Map Service Preview')
    plt.show()
    wmsObj.img_to_acad(TEMP_DIRECTORY)


# Test TileProperties
def test_get_tile():
    global tileObj

    #ggm_url = "https://mt1.google.com/vt/lyrs=m@113&hl=en"
    #doc = is_cadready()
    dwg_bounds = get_active_document_bounds()
    dwg_bounds = bbox2geo(dwg_bounds)
    print(f"deg_bounds: {dwg_bounds}")
    tileObj = TileProperties('Tile Map')
    tileObj.getdata([dwg_bounds[0:2], dwg_bounds[2:4]])
    print(f"bbox : {tileObj.bounds}")

def test_ggs():
    plt.imshow(tileObj.ggs_img)
    plt.title('Google Satellite Preview')
    plt.show()
    tileObj.img_to_acad(f"{TEMP_DIRECTORY}", tileObj.ggs_img, 'GGS')

def test_osm():
    plt.imshow(tileObj.osm_img)
    plt.title('OSM Preview')
    plt.show()
    tileObj.img_to_acad(f"{TEMP_DIRECTORY}", tileObj.osm_img, 'OSM')

def test_ggm():
    plt.imshow(tileObj.ggm_img)
    plt.title('Google Map Preview')
    plt.show()
    tileObj.img_to_acad(f"{TEMP_DIRECTORY}", tileObj.ggm_img, 'GGM')

#doc = is_cadready()
#test_wms()
#test_get_tile()
#test_ggs()
