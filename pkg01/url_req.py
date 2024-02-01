import pywintypes
import requests
import json
import os
import datetime
import time
import osmnx as ox

#from tkinter import *
from tkinter import filedialog as fd

#import os, sys, fiona
import geopandas as gpd
import matplotlib.pyplot as plt
#import pywintypes

from pkg01.global_var import *
from pkg02.cadlib import *
from pkg02.geom import *
from pkg03.utility import *

#global top
#top = set_root_window()
#top.iconify()

## Get last modified date of file
def get_last_modified_date(file_path):
    try:
        # Get the last modified timestamp of the file
        timestamp = os.path.getmtime(file_path)

        # Convert the timestamp to a human-readable date and time
        last_modified_date = datetime.datetime.fromtimestamp(timestamp)

        return last_modified_date
    except FileNotFoundError:
        return None


# Get url request parameter from file ".parx"
def getURLconfig():
    url_reg_dir = "d:/TGA_TEST/datacomp/"
    url_req_file = "url_req_params.parx"
    file_path = url_reg_dir + url_req_file
    #print(f"File : {file_path}")
    last_modified_date = get_last_modified_date(file_path)
    #print(f"Last modified : {last_modified_date}")
    ## Check last modified date of parameter file to current date
    if last_modified_date:
        current_datetime = datetime.datetime.now()
        time_difference = current_datetime - last_modified_date

        # Get the total number of minutes
        minutes_difference = time_difference.total_seconds() / 60

        #days_difference = (minutes_difference / 60 / 24)
        # Get the number of days
        days_difference = time_difference.days
        #print(f"Days : {days_difference}")
        ## Check > 30 Days
        if days_difference > 30:
            return False
    try:
        url_req_params = getProjParams(url_reg_dir, url_req_file)
    except Exception:
        return False

    #print(f"URL Params : {url_req_params}")
    return url_req_params

# Get OSM
def get_osm_data(b_box, network_type='all'):
    #b_box = ipyleaflet_map.bounds
    print(f"Req. bounds: {b_box}")
    # Get the graph (road network) within the bounding box
    #G = ox.graph_from_bbox(north, south, east, west, network_type='all')
    try:
        G = ox.graph_from_bbox(b_box[3], b_box[1], b_box[2], b_box[0], network_type=network_type)
    except requests.exceptions.Timeout:
        print("Request to OSM timed out. Try again later or reduce the data scope.")
        return None
    except Exception:
        return None
    #print(G)
    return G

# Add WFS layer
def getWFSdata(wfs_url, wfs_layer, max_fea, viewpar, bounds, crs='EPSG:4326', srsname='EPSG:4326'):
    #bounds = ipyleaflet_map.bounds
    # Craft your new WFS GetFeature request URL based on the new extent
    wfs_request_url = f"{wfs_url}?service=WFS&version=2.0.0&request=GetFeature&typeName={wfs_layer}&viewparams={viewpar}" \
                      f"&count={max_fea}&bbox={bounds[0]},{bounds[1]},{bounds[2]},{bounds[3]},{crs}&outputFormat=json&srsname=urn:x-ogc:def:crs:{srsname}"

    # Print or process the WFS request URL as needed
    #print("WFS Request URL:", wfs_request_url)
    print("WFS Request URL:", wfs_url)
    print(f"Req. bounds: {bounds}")

    # Create a GeoJSON layer using the updated WFS GetFeature request
    #geojson_layer = GeoJSON(data=wfs_request_url, name='WFS Layer')
    try:
        wfs_byte = requests.get(wfs_request_url, timeout=20)
    except requests.exceptions.Timeout:
        print("Request to WFS timed out. Try again later or reduce the data scope.")
        return None
    except requests.exceptions.RequestException:
        print('WFS error occurred, no parcel data!!!!')
        return None
    except Exception:
        print('An error occurred, no parcel data!!!!')
        return None

    if wfs_byte:
        wfs_str = wfs_byte.content.decode('utf8')
        #print(wfs_str)
        try:
            d_json = json.loads(wfs_str)
            #print(d_json['numberReturned'])
            if d_json['numberReturned'] == 0:
                d_json = None
        except:
            return None
        return d_json
    else:
        return None


def get_api_data_bbox(b_box):
    api_url = f"https://zign.me/tbt/tt_tbt_bbox_api.php?bbox={b_box[0][0]},{b_box[0][1]},{b_box[1][0]},{b_box[1][1]}"
    print(api_url)
    reponse = requests.get(api_url)
    #print(reponse)
    if reponse:
        return reponse.json()
    else:
        return None

#plt.switch_backend('Qt5Agg')  # Replace 'Qt5Agg' with an appropriate backend
plt.switch_backend('TkAgg')  # Replace 'Qt5Agg' with an appropriate backend
"""
Common backends include 'TkAgg', 'Qt5Agg', 'Agg', etc. Choose the one that works best for your system.
"""

# To send GeoData to AutoCAD drawing
def geoDF2ac(geodf, layer_name, fieldname=None, label_height=2.5):
    global top, sta_label
    """
    # Iterating through all features and accessing their geometry
    for index, row in geodf.iterrows():
        feature_geometry = row['geometry']
        print(f'Geometry of feature {index}:')
        print(feature_geometry)
        plt.plot(feature_geometry)
    """
    """
    # Plot each feature separately
    for index, row in geodf.iterrows():
        # Create a GeoDataFrame with only the current feature
        single_feature_gdf = gpd.GeoDataFrame([row], geometry='geometry')
        #print(single_feature_gdf['geometry'])
        # Plot the current feature
        #single_feature_gdf.plot()

        # Customize the plot if needed
        #plt.title(f'Feature {index}')
        #plt.show()
    """
    ### Working
    #doc = is_cadready()      # For testing
    start_datetime = datetime.datetime.now()
    start_time = start_datetime.strftime("%H:%M:%S")
    child_win = Toplevel(top)
    #child_win = Tk()
    child_win.geometry('615x100')
    child_win.geometry('+200+300')
    child_win.title(f"Status of <<< CREATING FEATURES : [{layer_name}] @{start_time} >>>")
    child_win.configure(bg='lightgreen')
    child_win.lift()
    # Specify the font size using the 'size' parameter
    label_font = ("Arial", 14)  # Replace "Arial" with your desired font and 12 with the desired font size
    sta_label = Label(child_win, text=': ', width=50, font=label_font)
    sta_label0 = Label(top, text=': ', width=50)

    rows = geodf.shape[0]
    if (rows==0):
        msg = 'There is no feature to be created.'
        show_message(msg)
        child_win.destroy()
        return 1

    msg = f'Creating [{rows} features] in AutoCAD... @{start_time}\n'
    pycad_prompt(msg)

    ## Define status window
    def status_win(msg):
        sta_label.configure(text=': ' + msg, width=50, fg='#4488CC', bg='lightgreen')
        sta_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        sta_label.master.update()

    ## Check Layer name exist or not
    if not layerexist(layer_name):
        doc.Layers.Add(layer_name)
    if not layerexist('Interior_'+layer_name):
        doc.Layers.Add('Interior_'+layer_name)
    if not layerexist(fieldname):
        doc.Layers.Add(fieldname)

    npt_err = nls_err = npgo_err = npgi_err = nmp_err = 0
    i = 1
    success_features = 0
    #print(f"Number of rows: {rows}")
    ## Set sys.stdout & sys.stderr equal to buffer for Windows 11 running
    #sys.stdout = sys.stderr = buffer
    sys.stdout = buffer

    # Iterate through all features and get coordinates of polygon vertices
    for index, row in geodf.iterrows():
        feature_geometry = row['geometry']
        #feature_properties = row['properties']

        #print(f"Content of row : {row}")
        #print(feature_geometry)
        #print(f'Index : {index}')

        if fieldname:
            label_name = row[fieldname]
        else:
            label_name = 'x'
        #print(feature_geometry)
        #print(feature_properties)
        #print(f"Creating feature: #{i} / {rows}")
        try:
            if (i % 100)==0:
                acprompt(f'Draw feature: #{i} / {rows} : [{fieldname}: {label_name}] \n')
        except pywintypes.com_error:
            print(f'An error occurred at feature: #{i} / {rows}')
        except Exception:
            sys.stdout = sys.__stdout__
            print(f'An Exception occurred at feature: #{i} / {rows}')

        #acprompt('.')
        msg = f'Creating feature: #{i} / {rows}'
        statusbox(sta_label0, msg)
        try:
            status_win(msg)
        except:
            sys.stdout = sys.__stdout__
            print('Terminated by user!!!')
            return -1

        feature_type = feature_geometry.geom_type
        #if feature_type=='Polygon':
        #    raise TypeError(f'Feature type : {feature_type}')
        #feature_type = 'Polygon'
        #match feature_type:
        # Check if the geometry is a Point
        if (feature_type=='Point'):
            #case 'Point':
            # Extract coordinates of point
            x_exterior, y_exterior = feature_geometry.x, feature_geometry.y
            pt = [x_exterior, y_exterior]
            #print(f'Coordinates of feature #{i}: {pt}')
            #acprompt(f'Draw feature: #{i} : [Name: {label_name}] \n')
            try:
                ep = make_point(pt, layer_name, check=False)                   # Create Point
                ptxt(label_name, pt, label_height, fieldname, check=False)  # Create label of point
                success_features += 1
            except pywintypes.com_error:
                # I no longer care to see the errors because I can't do anything about them anyway.
                npt_err += 1
        ###================================

        # Check if the geometry is a LineString
        elif (feature_type=='LineString'):
        #case 'LineString':
            # Extract coordinates of the exterior
            #exterior_coords = feature_geometry.geoms[0].coords.xy
            exterior_coords = feature_geometry.coords.xy
            # print(f'Exterior coord: {exterior_coords}')
            x_exterior, y_exterior = exterior_coords[0], exterior_coords[1]

            # calculate middle point coordinate of linestring
            middle_point = feature_geometry.interpolate(0.5, normalized=True)
            #print(f"middle_point.coords: {list(middle_point.coords)[0]}")
            mid_point = list(middle_point.coords)[0]
            #mid_point = [middle_point.coords.xy[0][0], middle_point.coords.xy[1][0]]
            #print(f"mid_point: {mid_point}")


            #print(f'Coordinates of exterior of feature {index}:')
            #acprompt(f'Draw feature: #{i} : [Name: {label_name}] \n')
            pts = []
            for x, y in zip(x_exterior, y_exterior):
                #print(f'({x}, {y})')
                xy = (x, y)
                pts.append(xy)

            #print(f'LineString coords: {pts}')
            #geometry = row['geometry']

            # Compute centroid of polygon
            #centroid = centroid_polygon(feature_geometry)
            #print(f'Centroid of feature #{label_name}: {centroid}')
            #print('.', end='')
            try:
                ep = make_lwpline(pts, layer_name, check=False)                   # Create Lind String
                ptxt(label_name, mid_point, label_height, fieldname,
                     check=False)  # Create label of linestring
                #ptxt(label_name, pts[int(len(pts)/2)], label_height, fieldname, check=False)  # Create label of linestring
                success_features += 1
            except pywintypes.com_error:
                # I no longer care to see the errors because I can't do anything about them anyway.
                nls_err += 1
                #raise TypeError(f'This COM object [{feature_type}] can not automate!')
            except Exception:
                continue
        ###================================

        # Check if the geometry is a Polygon
        #case 'Polygon':
        elif (feature_type=='Polygon'):
            # Extract coordinates of the exterior (outer ring)
            exterior_coords = feature_geometry.exterior.coords.xy

            #print(f'Exterior coord: {exterior_coords}')
            x_exterior, y_exterior = exterior_coords[0], exterior_coords[1]

            #print(f'Coordinates of exterior of feature {index}:')
            #acprompt(f'Draw feature: #{i} : [Name: {label_name}] \n')
            pts = []
            for x, y in zip(x_exterior, y_exterior):
                #print(f'({x}, {y})')
                xy = (x, y)
                pts.append(xy)

            #print(f'Polygon coords: {pts}')
            #geometry = row['geometry']

            # Compute centroid of polygon
            #centroid = centroid_polygon(feature_geometry)
            feature_centroid = feature_geometry.centroid
            centroid = [feature_centroid.x, feature_centroid.y]
            #centroid = [feature_geometry.centroid.x, feature_geometry.centroid.y]
            #print(f'Centroid of feature #{label_name}: {centroid}')
            #print('.', end='')
            try:
                ep = make_lwpline(pts, layer_name, check=False)    # Create polygon
                chProp(ep, 70, 1)               # Change property of polygon to closed
                ptxt(label_name, centroid, label_height, fieldname, check=False)    # Create label of polygon
                success_features += 1
            except pywintypes.com_error as e:
                # I no longer care to see the errors because I can't do anything about them anyway.
                npgo_err += 1
                #raise TypeError('This COM object [Exterior Polygon] can not automate!')
            except Exception as e:
                print(f"Exception occurred for item {i}: {e}")

            # Extract coordinates of any interior rings (holes)
            for interior in feature_geometry.interiors:
                interior_coords = interior.coords.xy
                x_interior, y_interior = interior_coords[0], interior_coords[1]
                pts_i = []
                print(f'Coordinates of interior of feature {index}: >>>>>>>>')
                for x, y in zip(x_interior, y_interior):
                    #print(f'({x}, {y})')
                    xy = (x, y)
                    pts_i.append(xy)
                if len(pts_i) > 0:
                    try:
                        e_par = make_lwpline(pts_i, 'Interior_'+layer_name, check=False)  # Create polygon (Interior)
                        chProp(e_par, 70, 1)            # Change property of polygon to closed
                    except pywintypes.com_error:
                        # I am checking for COM object of Interior Polygon.
                        npgi_err += 1
                        if (npgi_err > 5):
                            raise TypeError(f'The {npgi_err} COM objects [Interior Polygon] can not automate!')
        ####==========================================================

        # Check if the geometry is a MultiPolygon
        #case 'MultiPolygon':
        elif (feature_type=='MultiPolygon'):
            # Extract coordinates of the exterior (outer ring)
            #exterior_coords = feature_geometry.geoms.exterior.coords.xy
            #print(f'GEOMS :  {feature_geometry.geoms[0]}')

            exterior_coords = feature_geometry.geoms[0].exterior.coords.xy

            #print(f'Exterior coord: {exterior_coords}')
            #print('Result exterior :', exterior_coords[0], exterior_coords[1])
            x_exterior, y_exterior = exterior_coords[0], exterior_coords[1]

            #print(f'Coordinates of exterior of feature {index}:')
            #acprompt(f'Draw feature#: {i}: [Name: {label_name}] \n')
            pts = []
            for x, y in zip(x_exterior, y_exterior):
                #print(f'({x}, {y})')
                xy = (x, y)
                pts.append(xy)

            #print(f'Polygon coords: {pts}')
            #geometry = row['geometry']

            # Compute centroid of polygon
            centroid = centroid_polygon(feature_geometry)
            #print(f'Centroid of feature #{label_name}: {centroid}')
            #print('.', end='')
            #ep = make_lwpline(pts, name, check=False)                   # Create feature
            #chProp(ep, 70, 1)            # Change property of polygon to closed
            ptxt(label_name, centroid, label_height, fieldname, check=False)             # Create label

            # If it has more than one component, convert it to a Polygon
            if len(feature_geometry.geoms) > 0:
                # If it has multiple components,
                for coords in feature_geometry.geoms:
                    #print(f"Sub: {coords}:")
                    sub_coords = coords.exterior.coords.xy
                    x_sub, y_sub = sub_coords[0], sub_coords[1]
                    sub_pts = []
                    for x, y in zip(x_sub, y_sub):
                        #print(f'({x}, {y})')
                        xy = (x, y)
                        sub_pts.append(xy)
                    #print(f"Sub polygon: {sub_pts}")
                    #if label_name=='จ.นครศรีธรรมราช':
                    #    print(f"Sub polygon: {sub_pts}")
                    try:
                        ep = make_lwpline(sub_pts, layer_name, check=False)  # Create feature
                        chProp(ep, 70, 1)                 # Change property of polygon to closed
                        success_features += 1
                    except pywintypes.com_error as e:
                        # I no longer care to see the errors because I can't do anything about them anyway.
                        nmp_err += 1
                        #raise TypeError(f'This COM object [{feature_type}] can not automate!')
                    except Exception as e:
                        print(f"Exception occurred for item {i}: {e}")

        ###========================================
        else:
            print("The feature type doesn't matter, what matters is solving problems.")
        ###========================================

        if (i % 1000) == 0:
            time.sleep(1)  # Sleep for 1 second
        i += 1
        """
            # Extract coordinates of any interior rings (holes)
            for interior in feature_geometry.geoms[0]:
                interior_coords = interior.coords.xy
                x_interior, y_interior = interior_coords[0], interior_coords[1]
                pts_i = []
                print(f'Coordinates of interior of feature {index}: >>>>>>>>')
                for x, y in zip(x_interior, y_interior):
                    #print(f'({x}, {y})')
                    xy = (x, y)
                    pts_i.append(xy)
                if len(pts_i) > 0:
                    e_par = make_lwpline(pts_i, 'Interior_'+name)           # Create Land parcel (Interior)
                    chProp(e_par, 70, 1)            # Change property of polygon to closed
        """


    finish_datetime = datetime.datetime.now()
    time_difference = finish_datetime - start_datetime
    #minutes_difference = time_difference.total_seconds() / 60

    # Clear the content of the buffer
    buffer.truncate(0)
    buffer.seek(0)

    try:
        #doc.Regen(1)
        doc.SendCommand('_regen ')
        acprompt(f'\nImport & Draw {success_features} features Finished.\n')
        doc.SendCommand('_qsave ')
    except pywintypes.com_error:
        print(f'An error occurred at [regen]')
    except Exception:
        print(f'An UNKNOWN error occurred.!!!')

    ## Reset sys.stdout & sys.stderr to NORMAL state
    sys.stdout = sys.__stdout__
    #sys.stderr = sys.__stderr__

    msg = '>>>> Features have been created.'
    #print(msg)
    statusbox(sta_label0, msg)
    child_win.destroy()

    #msg = f"Total {rows} Features : [{layer_name}] : have been created,\n[for {minutes_difference:.1f} minutes]."
    msg = f"[{layer_name}] : [{success_features} / {rows}] Features : have been created.\n" \
           f"[Elapsed time >> {str(time_difference).split('.',1)[0]}]."

    ## Shows some messages
    if (npt_err > 0):
        print(f'{npt_err} Points could not be created!!!')
    if (nls_err > 0):
        print(f'{nls_err} LineStrings could not be created!!!')
    if (npgo_err > 0):
        print(f'{npgo_err} Exterior Polygons could not be created!!!')
    if (npgi_err > 0):
        print(f'{npgi_err} Interior Polygons could not be created!!!')
    if (nmp_err > 0):
        print(f'{nmp_err} MultiPolygons could not be created!!!')

    try:
        acprompt('\n' + msg + '\n')
    except pywintypes.com_error:
        print(f'An error occurred at [acprompt]')
    except:
        print(f'An UNKNOWN error occurred.!!!')

    show_message(msg)
    ### End geoDF2ac

# Write GeoDataFrame to file
def geoDF2file(gdf, filename, driver='GeoJSON'):
    #gdf.to_file('D:/TGA_TEST/datacomp/wfs_dol-2.json', driver='GeoJSON')
    #shpfile = 'D:/TGA_TEST/datacomp/wfs_dol-4.shp'
    #gdf.to_file(shpfile, driver='ESRI Shapefile')
    print(f"Writing data to file : {filename} ...")
    gdf.to_file(filename, driver)
    show_message(f"File : {filename} : has been created.")

# LandMaps to AutoCAD
def parcel_wfs2device(to='to_dwg'):
    # Start of LandMaps to AutoCAD
    global acad, doc, cadready

    # Check AutoCAD ready or not
    doc = is_cadready()
    if not doc:
        return False

    #print(doc)
    #acad = win32com.client.Dispatch("AutoCAD.Application")
    #acprompt = doc.Utility.Prompt
    #ms = doc.ModelSpace

    ### These 3 parameters should be defined in a parmeter file later.
    #dol_wfs_url = "https://landsmaps.dol.go.th/geoserver/LANDSMAPS/wfs"
    #dol_layer_name = 'V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO'
    #dol_layer_name = 'V_PARCEL47_LANDNO'
    #dol_view_params = 'utmmap:51363,utmmap:51364,utmmap:50362,utmmap:50361'
    ### ------------

    #dol_data = getWFSdata(dol_wfs_url, dol_layer_name, 200, dol_view_params, [(100.425,13.877), (100.445,13.905)])   #OK
    #dol_data = getWFSdata(dol_wfs_url, dol_layer_name, 20, dol_view_params, [(13.877,100.425), (13.905,100.445)])
    #dol_data = getWFSdata(dol_wfs_url, dol_layer_name, 500, dol_view_params, [(633085.7299236332, 1526987.26557123), (676689.059034325, 1545173.218927742)], srsname='EPSG:32647')
    dwg_bounds = get_active_document_bounds()
    dwg_bounds = bbox2geo(dwg_bounds)                                  # Convert 32647 to 4326

    ## if getting boundary boox from AutoCAD is True
    if dwg_bounds:
        #dol_data = get_api_data_bbox([dwg_bounds[0:2], dwg_bounds[2:4]])   # Send request via TBT
        #dol_data = getWFSdata(dol_wfs_url, dol_layer_name, dol_feature_count, dol_view_params, [dwg_bounds[0:2], dwg_bounds[2:4]], srsname='EPSG:4326')
        dol_data = getWFSdata(dol_wfs_url, dol_layer_name, dol_feature_count, dol_view_params,
                              dwg_bounds, srsname='EPSG:4326')

    # Draw land parcels to AutoCAD
    if dol_data:
        dol_gdf = gpd.GeoDataFrame.from_features(dol_data, crs='EPSG:4326')
        #dol_gdf.head()
        #print(dol_gdf)
        #plt.figure(figsize=(8,6))
        #plt.title('Land Parcels Preview')
        plt.close()
        dol_gdf.plot(figsize=(8,5.5), color='lightgreen')
        plt.title(f'[{dol_gdf.shape[0]} Land Parcels] Preview')
        plt.show()
        dol_gdf_32647 = dol_gdf.to_crs(32647)  # Convert data frame to 32647
        #dol_gdf_32647.set_crs('EPSG:32647')
        dol_gdf_32647['area'] = dol_gdf_32647['geometry'].area
        #dol_gdf_32647.head(20)
        #dol_gdf_32647.sindex
        #print(dol_gdf_32647.columns)

        if to == 'to_file':
            # Define conditions
            #condition1 = (dol_gdf_32647['area'] > 32000)
            condition1 = (dol_gdf_32647['area'] > 1)
            condition2 = (dol_gdf_32647['area'] < 700000)
            desired_geometry_types = ['Polygon', 'MultiPolygon']

            # Create a condition based on geometry types
            condition3 = dol_gdf_32647.geometry.geom_type.isin(desired_geometry_types)

            # Combine conditions using logical operators
            combined_condition = condition1 & condition2 & condition3 # Use '&' for 'and', '|' for 'or'

            # Filter the GeoDataFrame based on the combined condition
            filtered_gdf = dol_gdf_32647[combined_condition]
            print(filtered_gdf)
            #selected_columns = ['parcel_seq', 'land_no', 'geometry', 'area']
            selected_columns = ['land_no', 'geometry', 'area']
            file_out = fd.asksaveasfilename(title='Define Output File',filetypes=[("Shp file", "*.shp")])
            if file_out == '':
                return False
            else:
                geoDF2file(filtered_gdf[selected_columns],file_out,driver='ESRI Shapefile')
                #geoDF2file(filtered_gdf[selected_columns],'D:/TGA_TEST/datacomp/kamalasai-new.json')

        else:
            geoDF2ac(dol_gdf_32647, 'Parcels', 'land_no')       # Draw features to AutoCAD
    else:
        print('No parcel data!, Please try again later.')


    #dwg_bounds = get_active_document_bounds()
    #print(f"The value of Drawing boundary box is: {dwg_bounds}")
    ### End def parcel_wfs2ac()

# Province to AutoCAD
def prov_wfs2ac():
    global acad, doc, cadready

    # Check AutoCAD ready or not
    doc = is_cadready()
    if not doc:
        return False

    #acad = win32com.client.Dispatch("AutoCAD.Application")
    #acprompt = doc.Utility.Prompt
    #ms = doc.ModelSpace
    wfs_url = "https://geoserver.thgeom-academy.com/geoserver/thgeom/wfs"
    wfs_layer = "thgeom:province"
    b_box = (98.5, 5.5, 105.5, 21.5)

    prov_data = getWFSdata(wfs_url,wfs_layer,200,viewpar='',bounds=b_box,srsname='EPSG:4326')
    prov_gdf = gpd.GeoDataFrame.from_features(prov_data, crs='EPSG:4326')
    prov_gdf_32647 = prov_gdf.to_crs(32647)  # Convert data frame to 32647
    print(prov_gdf_32647)
    prov_gdf_32647.plot()
    plt.show()
    geoDF2ac(prov_gdf_32647, 'Provinces', 'PROV_NAM_T', 5000)
    # End prov_wfs2ac()

# WFS to AutoCAD
def get_wfs2ac():
    global acad, doc, cadready

    # Check AutoCAD ready or not
    doc = is_cadready()
    if not doc:
        return False

    #acad = win32com.client.Dispatch("AutoCAD.Application")
    #acprompt = doc.Utility.Prompt
    #ms = doc.ModelSpace
    #wfs_url = "https://geoserver.thgeom-academy.com/geoserver/thgeom/wfs"
    #wfs_layer = "thgeom:BLDG_new_region"
    #b_box = (98.5, 5.5, 105.5, 21.5)
    dwg_bounds = get_active_document_bounds()
    dwg_bounds = bbox2geo(dwg_bounds)                                  # Convert 32647 to 4326
    layer = wfs_layer.rsplit(':')[1]    ## Get layer name
    print('Requesting & Processing...')
    wfs_data = getWFSdata(wfs_url,wfs_layer,wfs_feature_count,viewpar='',bounds=dwg_bounds,srsname='EPSG:4326')
    if wfs_data:
        wfs_gdf = gpd.GeoDataFrame.from_features(wfs_data, crs='EPSG:4326')
        wfs_gdf_32647 = wfs_gdf.to_crs(32647)  # Convert data frame to 32647


        print(f"[{layer}] : Total {wfs_gdf_32647.shape[0]} features selected.")
        print(f"List of feature columns")
        print(list(wfs_gdf_32647.columns))

        wfs_gdf_32647.plot(figsize=(8,5.5), color='darkgreen')
        plt.title(f'[{layer} : {wfs_gdf_32647.shape[0]} Features] Preview')
        plt.ylabel('Northing')
        plt.xlabel('Easting')
        plt.show()
        geoDF2ac(wfs_gdf_32647, f"WFS_{layer}", wfs_label)
    else:
        print('No WFS data!!!')
    # End get_wfs2ac()

# OSM to AutoCAD
def osm2ac():
    global acad, doc, cadready

    # Check AutoCAD ready or not
    doc = is_cadready()
    if not doc:
        return False

    #acad = win32com.client.Dispatch("AutoCAD.Application")
    #acprompt = doc.Utility.Prompt
    #ms = doc.ModelSpace

    dwg_bounds = get_active_document_bounds()                    # Get LL & UR from AutoCAD
    dwg_bounds = bbox2geo(dwg_bounds)                            # Convert 32647 to 4326
    #print(f'Bounds: {dwg_bounds}')
    ## if getting boundary boox from AutoCAD is True
    if dwg_bounds:
        osm_data = get_osm_data(dwg_bounds, network_type)  # By specified network type
    #print(osm_data)
    if osm_data:
        osm_gdf_nodes, osm_gdf_edges = ox.utils_graph.graph_to_gdfs(osm_data)
        #osm_gdf_edges.to_crs(4326)
        osm_gdf_edges_32647 = osm_gdf_edges.to_crs(32647)  # Convert data frame to 32647
        osm_gdf_nodes_32647 = osm_gdf_nodes.to_crs(32647)  # Convert data frame to 32647
        #print(osm_gdf_edges_32647)
        #osm_gdf_edges_32647.sindex
        osm_gdf_edges_32647.plot(figsize=(7,5), color='orange')
        #osm_gdf_nodes_32647.plot()
        plt.title(f'[{osm_gdf_edges_32647.shape[0]} OpenStreetMap Edges] Preview')
        plt.ylabel('Northing')
        plt.xlabel('Easting')
        plt.show()
        #print(osm_gdf_nodes_32647)

        # Create a GeoDataFrame for polylines
        #polylines_gdf = gpd.GeoDataFrame()

        # Add the LineString geometries to the GeoDataFrame
        #polylines_gdf['geometry'] = osm_gdf_32647['geometry']
        #print(polylines_gdf)
        """
        # Extract coordinates for each LineString
        coordinates_list = []

        for index, row in polylines_gdf.iterrows():
            line_coords = list(row['geometry'].coords)
            print(f"Row : {row['geometry'].geom_type}")
            coordinates_list.append(line_coords)

        # Create a new column with the coordinates
        polylines_gdf['coordinates'] = coordinates_list

        # Print the GeoDataFrame with coordinates
        print(polylines_gdf[['geometry', 'coordinates']])
        """

        #geoDF2ac(polylines_gdf, 'OpenStreetMaps')

        #geoDF2ac(osm_gdf_nodes_32647, 'OpenStreetMaps_Nodes')
        geoDF2ac(osm_gdf_edges_32647, 'OpenStreetMaps', 'highway')
    else:
        print('No OSM data.')
    # End osm2ac()
    ## ============================================================

## Define some parmeters for url requesting
## For OSM
network_type = 'drive_service'
"""
You can also specify several different network types:
'drive' - get drivable public streets (but not service roads)
'drive_service' - get drivable streets, including service roads
'walk' - get all streets and paths that pedestrians can use (this network type ignores one-way directionality)
'bike' - get all streets and paths that cyclists can use
'all' - download all non-private OSM streets and paths (this is the default network type unless you specify a different one)
'all_private' - download all OSM streets and paths, including private-access one
"""
"""
## For DOL parcels
dol_wfs_url = "https://landsmaps.dol.go.th/geoserver/LANDSMAPS/wfs"
dol_layer_name = 'V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO'
#dol_layer_name = 'V_PARCEL47_LANDNO'
dol_view_params = 'utmmap:51363,utmmap:51364,utmmap:50362,utmmap:50361'
### dol_layer_name & dol_view_params have to modified according to the project area
dol_feature_count = 8000
"""

## Get url paramater especially for DOL configuration
global url_params
url_params = getURLconfig()
if url_params:
    dol_wfs_url = url_params['DOL_OWS_url']
    dol_layer_name = url_params['DOL_layer_name']
    dol_view_params = url_params['DOL_view_params']
    dol_feature_count = url_params['DOL_feature_count']
    ### For Testing version
    if dol_feature_count > 20000:
        dol_feature_count = 20000
    ### For Testing
    dol_ows_url = url_params['DOL_OWS_url']
    wms_url = url_params['WMS_url']
    wfs_url = url_params['WFS_url']
    wms_layer = url_params['WMS_layer']
    wfs_layer = url_params['WFS_layer']
    wfs_label = url_params['WFS_label']
    wfs_feature_count = url_params['WFS_feature_count']
    #print(f'dol_view_paramsx : {dol_view_paramsx}')

def parcel2dwg():
    parcel_wfs2device(to='to_dwg')

def parcel2shp():
    parcel_wfs2device(to='to_file')

