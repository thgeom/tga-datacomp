"""
import fiona

# Specify the shapefile path
shapefile_path = 'D:/TGA_TEST/datacomp/samutprakarn.shp'

# Open the shapefile using Fiona
with fiona.open(shapefile_path) as src:
    # Get the column names
    column_names = [prop['name'] for prop in src.schema['properties']]

# Display the list of column names
print(column_names)
"""
import fiona

# Specify the shapefile path
#shapefile_path = 'path/to/your/shapefile.shp'
shapefile_path = 'D:/TGA_TEST/datacomp/samutprakarn.shp'

# Open the shapefile using Fiona
with fiona.open(shapefile_path) as src:
    # Get the first feature to access its properties
    first_feature = next(iter(src))

    # Get the column names from the properties of the first feature
    column_names = list(first_feature['properties'].keys())

# Display the list of column names
print(column_names)
