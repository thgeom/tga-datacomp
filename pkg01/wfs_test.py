from pkg01.url_req import *
import xmltodict



## ==========================
## WFS for DOL parcels testing

#center = (13.7253, 100.6099) # PKM Vill.
#center = (13.8891, 100.4336)  # BBT
#data = get_api_data(13.625, 100.609)
#data = get_api_data(center[0], center[1])
#data = get_api_data_bbox([(100.601,13.705), (100.618,13.735)])
"""
data = get_api_data_bbox([(100.425,13.877), (100.445,13.905)])
if data:
    data_gdf = gpd.GeoDataFrame.from_features(data, crs='EPSG:4326')
    #data_gdf = gpd.GeoDataFrame.from_features(data)
    print(data_gdf)
    data_gdf.plot()
    plt.show()
    data_gdf.to_file('D:/TGA_TEST/datacomp/wfs_dol.json', driver='GeoJSON')
else:
    print('An error occurred.')
"""

# Test parcel_wfs2ac
#parcel_wfs2device(to='to_file')
#parcel_wfs2device(to='to_dwg')

# Test bldg_wfs2ac
#bldg_wfs2ac()

# Test osm2ac
#osm2ac()


"""
# Getting url parameter from file 
url_params = getURLconfig()
dol_wfs_urlx = url_params['DOL_WFS_url']
dol_layer_namex = url_params['DOL_layer_name']
dol_view_paramsx = url_params['DOL_view_params']
dol_feature_countx = url_params['DOL_feature_count']
print(f'dol_view_paramsx : {dol_view_paramsx}')
"""


def getWFScapabilities(wfs_url):
    #bounds = ipyleaflet_map.bounds
    # Craft your new WFS GetFeature request URL based on the new extent
    wfs_request_url = f"{wfs_url}?service=WFS&version=1.1.0&request=GetCapabilities"

    # Print or process the WFS request URL as needed
    #print("WFS Request URL:", wfs_request_url)
    print("OWS Request URL:", wfs_url)

    # Create a GeoJSON layer using the updated WFS GetCapabilities request
    try:
        wfs_byte = requests.get(wfs_request_url, timeout=20)
    except requests.exceptions.Timeout:
        print("Request to WFS timed out. Try again later or reduce the data scope.")
        return None
    except requests.exceptions.ConnectionError:
        print('WFS error occurred, no WFS data!!!!')
        return None
    except Exception:
        print('An error occurred, no WFS data!!!!')
        return None

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
            return None
        return json_data
    else:
        return None




## Get list of WFS layers
def getWFSlayers(wfs_url):
    try:
        wfs_result = getWFScapabilities(wfs_url)
    except:
        return None

    if wfs_result:
        layer_list = []
        featureTypes = wfs_result['wfs:WFS_Capabilities']['FeatureTypeList']['FeatureType']
        for layer in featureTypes:
            layer_list.append(layer)

        return layer_list
    else:
        return None


# Get list of layers
def getLayers():
    #ows_url = "https://geoserver.thgeom-academy.com/geoserver/thgeom/ows"
    #lay_list = getWFSlayers(wfs_url)

    ## Usingg WfsProperties class
    wfsObj = WfsProperties(wfs_url, 'wfs', '2.0.0')
    wfsObj.getlayer()
    lay_list = wfsObj.layers
    #print(f"Layer list: {lay_list}")
    #print(f'GetCapabilities : {ows_url}')
    print('List of WMS/WFS layers >>>>')
    i = 1
    for layer in lay_list:
        print(f"{i} : {layer}")
        i += 1

## Get WFS to AutoCAD
def wfs2ac():
    pass


# Test GetLayers
#getLayers()
