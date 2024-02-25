from pyproj import CRS,Transformer,Proj
from shapely.geometry import shape, Polygon
from pkg01.global_var import *

#Define coordinate transformation parameters
UTMz = ACAD_CRS.rsplit(':')[1]
crs_UTM = CRS.from_epsg(UTMz)    # WGS84 UTM zoneXX
crs_WGS84 = CRS.from_epsg(4326)     # WGS84
crs_3857 = CRS.from_epsg(3857)      # World Mercator

proj2utm = Transformer.from_crs(crs_WGS84, crs_UTM, always_xy=True, accuracy=0.001)
proj2geo = Transformer.from_crs(crs_UTM, crs_WGS84, always_xy=True, accuracy=0.001)
proj3857toUTM = Transformer.from_crs(crs_3857, crs_UTM, always_xy=True, accuracy=0.001)

utm = Proj(crs_UTM)
mer = Proj(crs_3857)

# Compute scale factor of bbox diagonal (b_box in LonLat)
def calMidScale(crs, bbox_ll):
    proj = Proj(crs)
    sf1 = proj.get_factors(bbox_ll[0],bbox_ll[1]).meridional_scale
    sf2 = proj.get_factors(bbox_ll[2],bbox_ll[3]).meridional_scale
    return (sf1 + sf2) / 2


# To convert bbox from lonlat to UTM Zone 47
def bbox2utm(b_box):
    from pkg01.global_var import ACAD_CRS

    UTMz = ACAD_CRS.rsplit(':')[1]
    crs_UTM = CRS.from_epsg(UTMz)  # WGS84 UTM zoneXX
    proj2utm = Transformer.from_crs(crs_WGS84, crs_UTM, always_xy=True, accuracy=0.01)

    ll = proj2utm.transform(b_box[0], b_box[1])
    ur = proj2utm.transform(b_box[2], b_box[3])
    return ll + ur
#-----------------

# To convert bbox from EPSG:32647 to WGS84
def bbox2geo(b_box):
    from pkg01.global_var import ACAD_CRS

    UTMz = ACAD_CRS.rsplit(':')[1]
    crs_UTM = CRS.from_epsg(UTMz)  # WGS84 UTM zoneXX
    proj2geo = Transformer.from_crs(crs_UTM, crs_WGS84, always_xy=True, accuracy=0.001)

    ll = proj2geo.transform(b_box[0], b_box[1])
    ur = proj2geo.transform(b_box[2], b_box[3])
    return ll + ur
#-----------------

# To convert bbox from 3857 to UTM Zone 47
def bbox_mer2utm(b_box):
    from pkg01.global_var import ACAD_CRS

    UTMz = ACAD_CRS.rsplit(':')[1]
    crs_UTM = CRS.from_epsg(UTMz)  # WGS84 UTM zoneXX
    proj3857toUTM = Transformer.from_crs(crs_3857, crs_UTM, always_xy=True, accuracy=0.001)

    ll = proj3857toUTM.transform(b_box[0], b_box[1])
    ur = proj3857toUTM.transform(b_box[2], b_box[3])
    return ll + ur
#-----------------

"""
def bounds2bbox(bounds):
    bbox = (bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1])
    return bbox
#-----------------
"""

# To compute centroid of Polygon Geometry
def centroid_polygon(geometry):
    # Use the centroid of the geometry directly
    polygon = shape(geometry)
    centroid = list(polygon.centroid.coords[0])
    return centroid
#-----------------
