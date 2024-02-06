import win32com.client
from pkg02.cadlib import *
from pkg02.cad_mani import *

import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
import matplotlib.pyplot as plt
import fiona

fiona.supported_drivers['KML'] = 'rw'

# Check AutoCAD running
#print(f'Cad running : {is_autocad_running()}')
#print(f'Cad open : {is_cadopen()}')
#print(f'Cad ready : {is_cadready()}')
#acad = win32com.client.Dispatch("AutoCAD.Application")

"""
# Connect to AutoCAD
acad = win32com.client.Dispatch("AutoCAD.Application")
doc = acad.ActiveDocument
print(acad)
#print(doc.__dir__())
#print(doc.WindowState)
try:
    #doc
    doc_act = doc.Active
    cadready = True
except AttributeError:
    cadready = False
print(f"AutoCAD ready is : [{cadready}]")
"""
# Verify AutoCAD connection [modified on Dec 24, 2023]
def is_cadreadyX():
    global doc, acprompt, ms, cadready

    try:
        doc.Active
    except AttributeError:
        #print('Connect to AutoCAD failed!!!')
        #print('Press Esc on AutoCAD window then try again.')
        msg = 'AutoCAD currently in use!!!\n'
        msg += 'Press Esc on AutoCAD window then try again.'
        warn_message(msg)
        return False
    else:
        #acprompt = doc.Utility.Prompt                                   # ACAD prompt
        ms = doc.ModelSpace
        #print(doc)
        print('File {} connected.'.format(doc.Name))
        #doc.Utility.Prompt("Execute from python\n")
        acprompt('Hi, from Python : [TGA datacomp].\n')
        cadready = True
        return doc

    #return doc

#print(f"Test again AutoCAD ready is : [{is_cadreadyX()}]")

#objSel = doc.Utility.GetEntity()                  # Get entity by pick
#chProp(objSel[0], 70, 1)
"""
# Get the Editor object
editor = doc.Application.GetInterfaceObject("ObjectDBX.AxDbDocument").Editor

def get_active_command():
    return editor.GetCurrentCommandName()

active_command = get_active_command()
print(f"The active command is: {active_command}")
"""

"""
import win32com.client

def create_autocad_drawing(geojson_file):
    # Create AutoCAD application
    acad = win32com.client.Dispatch("AutoCAD.Application")

    # Set visibility (optional)
    acad.Visible = True

    # Create a new drawing
    doc = acad.Documents.Add()

    # Get the modelspace
    mspace = doc.ModelSpace

    # Read GeoJSON data
    with open(geojson_file, 'r') as f:
        geojson_data = json.load(f)

    # Iterate through GeoJSON features
    for feature in geojson_data['features']:
        if feature['geometry']['type'] == 'Polygon':
            # Extract coordinates from GeoJSON
            coordinates = feature['geometry']['coordinates'][0]  # Assuming there's only one exterior ring

            # Add polygon to AutoCAD
            polyline = mspace.AddPolyline(coordinates)

            # Add attributes to the polygon
            for key, value in feature['properties'].items():
                attribute = polyline.AddAttribute(key, value)
                attribute.Invisible = True  # Hide the attribute

    # Save the drawing
    doc.SaveAs("C:\\Path\\To\\Your\\Drawing.dwg")
    doc.Close()

# Example usage
geojson_file = 'your_geojson_file.geojson'
create_autocad_drawing(geojson_file)

"""
"""
import win32com.client
import geopandas as gpd
from shapely.geometry import Point

# Connect to AutoCAD
acad = win32com.client.Dispatch("AutoCAD.Application")

# Get the active document
doc = acad.ActiveDocument

# Get the selection set
selection_set = doc.SelectionSets.Add("MySelectionSet")
selection_set.SelectOnScreen()  # You can modify this to select entities in a different way

# Create a GeoDataFrame to store the data
columns = ["Entity", "Geometry"]
data = []

# Iterate through the selected entities
for i in range(1, selection_set.Count + 1):
    entity = selection_set.Item(i)

    # Extract relevant information (you may need to customize this based on your entity types)
    entity_type = entity.EntityName
    geometry = Point(entity.InsertionPoint[0], entity.InsertionPoint[1])

    data.append([entity_type, geometry])

# Create GeoDataFrame
gdf = gpd.GeoDataFrame(data, columns=columns, geometry="Geometry")

# Print or do further processing with the GeoDataFrame
print(gdf)

# Release the selection set
selection_set.Delete()

"""
## Select AutoCAD entities using pywin32 as acSelectionSet defined in CADLIB
## then convert to GeoDataFrame
## GeoDataFrame manipulation such as .sjoin, sjoin.nearest to combine to GDF accordint to their geometry
def ac2gdf():
    acss = select_by_window()
    # Create a GeoDataFrame to store the data
    columns = ['Entity_Type', 'geometry', 'Layer', '_Name']
    data = []
    points = []
    polylines = []

    # Iterate through the selected entities
    for entity in acss.slset:
        # Extract relevant information (you may need to customize this based on your entity types)
        entity_type = entity.EntityName
        #print(f"entity_type : {entity_type}")
        #geometry = Point(entity.InsertionPoint[0], entity.InsertionPoint[1])
        if entity_type == 'AcDbText':
            point = Point(list(entity.InsertionPoint))
            layer = entity.Layer
            name = entity.TextString
            geometry = point
            #points.append([entity_type, point, name])
        elif entity_type == 'AcDbPoint':
            point = Point(list(entity.Coordinates))
            layer = entity.Layer
            name = None
            geometry = point
            #points.append([entity_type, point, name])
        elif entity.EntityName == "AcDbPolyline":
            # Create a list to store LineString geometries

            #print(f"entity.Coord: {entity.Coordinates}")
            points = [(entity.Coordinates[i], entity.Coordinates[i + 1]) for i in range(0, len(entity.Coordinates), 2)]
            #print(f"points: {points}")
            polyline = LineString(points)
            layer = entity.Layer
            name = None
            geometry = polyline
            #polylines.append([entity_type, polylines, name])
        else:
            # Handle other entity types or skip them
            continue

        # Create a GeoDataFrame
        data.append([entity_type, geometry, layer, name])
        #data = {'geometry': points + polylines, 'type': ['Point'] * len(points) + ['LineString'] * len(polylines)}

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(data, columns=columns, geometry='geometry')
    return gdf

def ac2shp():
    ## Test ac2gdf
    acss_gdf = ac2gdf()
    # Print or do further processing with the GeoDataFrame
    #print(acss_gdf)
    rows = acss_gdf.shape[0]
    if rows == 0:
        msg = "*** No Entity selected. ***"
        show_message(msg)
        return

    acss_gdf.plot()
    plt.title(f'[{rows} ACAD selected features] : Data Preview')
    plt.show()

    # Get the unique categories in the 'Layer' column
    unique_layers = acss_gdf['Layer'].unique()

    # Convert the result to a Python list if needed
    unique_layers_list = list(unique_layers)

    # Print or use the unique layer names
    print(f"List of Selected Layers: {unique_layers_list}")

    """
    condition1 = (acss_gdf['Entity_Type'] == 'AcDbText')
    condition2 = (acss_gdf['Layer'] == 'NAME')
    desired_geometry_types = ['Point']
    """

    ## To select Linestring gdf
    condition1 = (acss_gdf['Entity_Type'] == 'AcDbPolyline')
    condition2 = (acss_gdf['Layer'].isin(unique_layers_list))
    desired_geometry_types = ['LineString']
    # Create a condition based on geometry types
    condition3 = acss_gdf.geometry.geom_type.isin(desired_geometry_types)

    # Combine conditions using logical operators
    combined_condition = condition1 & condition2 & condition3  # Use '&' for 'and', '|' for 'or'

    # Filter the GeoDataFrame based on the combined condition
    linestring_gdf = acss_gdf[combined_condition]
    linestring_gdf.set_crs('EPSG:32647', allow_override=True)
    selected_columns = ['Layer', 'geometry', '_Name']
    print('Total Linestrings')
    print(linestring_gdf[selected_columns])

    # Function to check if LineString is closed
    def is_closed(line):
        return line.is_closed

    # Filter the GeoDataFrame to get LineStrings that are not closed
    linestr_gdf = linestring_gdf[linestring_gdf['geometry'].apply(lambda x: not is_closed(x))]
    #print('Extracted LineStrings')
    #print(linestr_gdf[selected_columns])

    # Function to convert closed LineString to Polygon
    def line_to_polygon(line):
        if line.is_closed:
            return Polygon(line)
        else:
            return line

    #polygon_gdf = filtered_gdf
    # Apply the function to the 'geometry' column using .loc
    #gdf.loc[:, 'geometry'] = gdf['geometry'].apply(line_to_polygon)


    # Apply the function to the 'geometry' column
    linestring_gdf.loc[:, 'geometry'] = linestring_gdf['geometry'].apply(line_to_polygon)
    desired_geometry_types = ['Polygon']
    # Create a condition based on geometry types
    combined_condition = linestring_gdf.geometry.geom_type.isin(desired_geometry_types)
    polygon_gdf = linestring_gdf[combined_condition]
    #selected_columns = ['Layer', 'geometry', '_Name']
    #print('After converted to Polygon')
    #print(polygon_gdf[selected_columns])

    ## To select label_gdf
    condition10 = (acss_gdf['Entity_Type'] == 'AcDbText')
    condition11 = (acss_gdf['Entity_Type'] == 'AcDbPoint')
    condition2 = (acss_gdf['Layer'].isin(unique_layers_list))
    desired_geometry_types = ['Point']
    # Create a condition based on geometry types
    condition3 = acss_gdf.geometry.geom_type.isin(desired_geometry_types)

    # Combine conditions using logical operators
    combined_condition = condition10 & condition2 & condition3  # Use '&' for 'and', '|' for 'or'

    # Filter the GeoDataFrame based on the combined condition
    label_gdf = acss_gdf[combined_condition]
    label_gdf.set_crs('EPSG:32647', allow_override=True)
    #label_gdf.loc[:,'land_no'] = label_gdf['_Name']
    #label_gdf.loc[:, 'land_no'] = label_gdf['_Name']

    # Rename the 'old_name' column to 'new_name'
    #label_gdf = label_gdf.rename(columns={'_Name': 'land_no'})
    #selected_columns = ['Layer', 'geometry', '_Name']
    print('Selected Labels')
    print(label_gdf[selected_columns])


    ## To select point_gdf
    # Combine conditions using logical operators
    combined_condition = condition11 & condition2 & condition3  # Use '&' for 'and', '|' for 'or'

    # Filter the GeoDataFrame based on the combined condition
    point_gdf = acss_gdf[combined_condition]
    point_gdf.set_crs('EPSG:32647', allow_override=True)
    print('Total Selected Points')
    print(point_gdf[selected_columns])


    """
    # Spatial join to get points inside polygons
    joined_gdf = point_gdf.sjoin(polygon_gdf, how="right", predicate='intersects')
    #joined_gdf = gpd.sjoin(point_gdf, polygon_gdf, how="right", predicate="within")
    print('joined_gdf')
    selected_columns = ['Layer_right', 'geometry', 'land_no']
    print(joined_gdf.columns)
    print(joined_gdf[selected_columns])
    #print(joined_gdf.head())
    """

    # Display some information about the 'land_no' column in joined_gdf
    #print(joined_gdf['land_no'].dtype)
    #print(joined_gdf['land_no'].isnull().sum())

    # Convert 'land_no' column to numeric
    #joined_gdf['land_no'] = pd.to_numeric(joined_gdf['land_no'], errors='coerce')

    # The 'index_right' column will contain the index of the matching polygon in polygon_gdf
    # Now you can merge the information you want from point_gdf to polygon_gdf based on this index
    #result_gdf = polygon_gdf.merge(joined_gdf[['land_no']], left_index=True, right_index=True, how='left')
    #result_gdf = polygon_gdf.merge(joined_gdf[['land_no']], left_index=True, right_index=True, how='right')
    #result_gdf = joined_gdf

    gdflist = []
    # Spatial join to get labels inside polygons
    #pg_result_gdf = label_gdf.sjoin(polygon_gdf, how="right", predicate='intersects')
    if len(polygon_gdf) > 0:
        pg_result_gdf = label_gdf.sjoin(polygon_gdf, how="right", predicate='covered_by')
        ## For Result Polygons
        # Use .loc to avoid the warning when setting values
        # result_gdf.loc[:, 'land_no'] = joined_gdf['land_no']
        # result_gdf.set_crs(crs='EPSG:32647', allow_override=True)
        pg_result_gdf.crs = 'EPSG:32647'  ## Have to set for .prj file
        pg_result_gdf = pg_result_gdf.rename(columns={'Layer_right': 'Layer'})
        pg_result_gdf = pg_result_gdf.rename(columns={'_Name_left': '_Name'})
        selected_columns = ['Layer', 'geometry', '_Name']
        print('Result of Polygons with their attribute')
        print(pg_result_gdf[selected_columns])
        # print(pg_result_gdf)
        if pg_result_gdf.shape[0] > 0:
            gdflist.append([pg_result_gdf, 'Polygons'])

    # Spatial join to get labels over linestrings
    if len(linestr_gdf) > 0:
        ls_result_gdf = label_gdf.sjoin_nearest(linestr_gdf, how="right", max_distance=0.5)
        ## For Result LineStrings
        ls_result_gdf.crs = 'EPSG:32647'  ## Have to set for .prj file
        ls_result_gdf = ls_result_gdf.rename(columns={'Layer_right': 'Layer'})
        ls_result_gdf = ls_result_gdf.rename(columns={'_Name_left': '_Name'})
        selected_columns = ['Layer', 'geometry', '_Name']
        print('Result of LineStrings with their attribute')
        print(ls_result_gdf[selected_columns])
        if ls_result_gdf.shape[0] > 0:
            gdflist.append([ls_result_gdf, 'LineStrings'])

    # Spatial join to get labels over points
    if len(point_gdf) > 0:
        pt_result_gdf = label_gdf.sjoin_nearest(point_gdf, how="right", max_distance=0.25)
        ## For Result Points
        pt_result_gdf.crs = 'EPSG:32647'  ## Have to set for .prj file
        pt_result_gdf = pt_result_gdf.rename(columns={'Layer_right': 'Layer'})
        pt_result_gdf = pt_result_gdf.rename(columns={'_Name_left': '_Name'})
        selected_columns = ['Layer', 'geometry', '_Name']
        print('Result of Points with their attribute')
        print(pt_result_gdf[selected_columns])
        if pt_result_gdf.shape[0] > 0:
            gdflist.append([pt_result_gdf, 'Points'])

    # Update 'land_no' values in polygon_gdf using joined_gdf
    #result_gdf['land_no'] = joined_gdf['land_no']
    # Update 'land_no' values in polygon_gdf based on common index values
    #result_gdf['land_no'] = result_gdf['land_no'].combine_first(joined_gdf.set_index('index_right')['land_no'])

    """
    # Check if 'index_right' exists in the result_gdf before dropping it
    if 'index_right' in result_gdf.columns:
        result_gdf = result_gdf.drop(columns=['index_right'])
    """

    ## Export to Shape file
    def gdf_to_shp(gdf, filepath, encoding='tis-620'):
        gdf.to_file(filepath, driver="ESRI Shapefile", encoding=encoding)
        msg = f"Folder : {filepath} : has been created."
        print(msg)

    ## Export to Kml file
    def gdf_to_kml(gdf, filename, encoding='tis-620'):
        gdf.to_file(filename, driver="KML", encoding=encoding)
        msg = f"File : {filename} : has been created."
        print(msg)

    pathname = "D:/TGA_TEST/datacomp"
    selected_columns = ['Layer', 'geometry', '_Name']
    if len(gdflist)>0:
        for gdfi in gdflist:
            gdfi[0].plot()
            plt.title(f"{gdfi[0].shape[0]} {gdfi[1]} : Data Preview")
            plt.show()
            filepath = f"{pathname}/{gdfi[1]}"
            gdf_to_shp(gdfi[0][selected_columns], filepath)
            gdf_to_kml(gdfi[0][selected_columns], f"{filepath}/{gdfi[1]}.kml")
        msg = f"Output Shape/KML files were stored in folder\n" \
              f"{pathname}/[Polygons/LineStrings/Points]"
        show_message(msg)
    else:
        label_gdf.plot()
        label_gdf.crs = 'EPSG:32647'  ## Have to set for .prj file
        plt.title(f"{label_gdf.shape[0]} Labels : Data Preview")
        plt.show()
        filepath = f"{pathname}/Labels"
        gdf_to_shp(label_gdf[selected_columns], filepath)
        gdf_to_kml(label_gdf[selected_columns], f"{filepath}/Labels.kml")
        msg = f"Output Shape/KML file were stored in folder\n" \
              f"{pathname}/[Labels]"
        show_message(msg)
    ## End ac2shp


"""
# Export GeoDataFrame to a shapefile
output_shapefile = "D:/TGA_TEST/datacomp/result2file"
pg_result_gdf[selected_columns].to_file(output_shapefile, driver="ESRI Shapefile")
show_message(f"File : {output_shapefile} : has been created.")


# Export GeoDataFrame [ls_result_gdf] to a shapefile
output_shapefile = "D:/TGA_TEST/datacomp/ls_result"
ls_result_gdf[selected_columns].to_file(output_shapefile, driver="ESRI Shapefile")
show_message(f"File : {output_shapefile} : has been created.")
"""

## Test ac2shp()
#ac2shp()
