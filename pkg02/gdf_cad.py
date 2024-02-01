from tkinter import filedialog as fd

import tkinter as tk
from tkinter import ttk
import geopandas as gpd
import matplotlib.pyplot as plt
import fiona

from pkg01.global_var import *
from pkg01.url_req import geoDF2ac
#from pkg02.geom import *

## Read Shape file and return GDF
def shp2gdf(file_path, bbox=None, encoding='tis-620'):
    data_gdf = gpd.read_file(file_path, bbox=bbox, encoding=encoding)
    return data_gdf



def create_dropdown_window(column_names, shared_var, real_number_var, encoding_var, callback):
    def on_dropdown_change(*args):
        shared_var.set(dropdown_var.get())

    def on_ok_button_click():
        #callback(shared_var.get(),real_number_var.get())
        callback(shared_var.get(), real_number_var.get(), encoding_var.get())
        # Close the Tkinter window
        dropdown_window.destroy()

    # Create the Toplevel window
    dropdown_window = tk.Toplevel(top)
    dropdown_window.geometry('500x220')
    dropdown_window.geometry('+400+250')
    dropdown_window.title(f"Define Parameters of Features ")
    dropdown_window.lift(top)

    # Create a StringVar to store the selected column from the dropdown
    dropdown_var = tk.StringVar(dropdown_window)

    # Set the default value for the dropdown
    dropdown_var.set(column_names[0])

    #label = ttk.Label(dropdown_window, text="Select a Label :", font=('Helvetica', 10, 'bold'))
    #label.pack(padx=10, pady=10)

    # modify adding label
    label_font = ("Arial", 10)
    aLabel = tk.Label(dropdown_window, text="Please define AutoCAD features", font=label_font)
    aLabel.grid(column=0, row=0,  padx=5,  pady=10)
    # Label before the dropdown
    label = tk.Label(dropdown_window, text="Select a label:", width=25)
    label.grid(column=0, row=3,  padx=5,  pady=10)

    # Create the OptionMenu widget
    dropdown_menu = ttk.Combobox(dropdown_window, textvariable=dropdown_var, values=column_names)
    dropdown_menu.grid(column=1, row=3,  padx=5,  pady=10)
    dropdown_menu.bind("<<ComboboxSelected>>", on_dropdown_change)
    #dropdown_menu.pack(padx=80, pady=10)
    ## Label for font size
    label = tk.Label(dropdown_window, text="Font height:", width=25)
    label.grid(column=0, row=5,  padx=5,  pady=5)

    # text box entry
    #ttk.Label(dropdown_window, text="Enter a name:").grid(column=0, row=0)
    #fontsize = tk.StringVar()
    #real_number_var = tk.DoubleVar()
    enter_real_number = ttk.Entry(dropdown_window, width=12, textvariable=real_number_var)
    enter_real_number.grid(column=1, row=5,  padx=5,  pady=5, sticky=tk.W)


    ## Label for encoding
    label = tk.Label(dropdown_window, text="File Encoding:", width=25)
    label.grid(column=0, row=7,  padx=5,  pady=5)

    # text box entry
    #ttk.Label(dropdown_window, text="Enter a name:").grid(column=0, row=0)
    #fontsize = tk.StringVar()
    #real_number_var = tk.DoubleVar()
    enter_encoding = ttk.Entry(dropdown_window, width=12, textvariable=encoding_var)
    enter_encoding.grid(column=1, row=7,  padx=5,  pady=5, sticky=tk.W)


    # Create the OK button
    ok_button = tk.Button(dropdown_window, text="OK", command=on_ok_button_click)
    ok_button.grid(column=1, row=9,  padx=5,  pady=10, sticky=tk.W)
    #ok_button.pack(pady=10)

    # Return the Toplevel window
    return dropdown_window


def shp2ac():

    shpfile = fd.askopenfilename(title='Select Shape File', filetypes=[("SHP file", "*.shp")])
    if shpfile == '':
        return None

    #file_path = 'D:/TGA_TEST/datacomp/samutprakarn.shp'
    file_path = shpfile
    file_name = file_path.split('/')

    file_name = file_name[len(file_name) - 1]
    layer = file_name.split('.')[0]
    #print(layer)
    # Open the shapefile using Fiona
    with fiona.open(file_path) as src:
        # Get the first feature to access its properties
        first_feature = next(iter(src))

        # Get the column names from the properties of the first feature
        column_names = list(first_feature['properties'].keys())
    #bbox = [684000, 1513000, 684500, 1513500]
    dwg_bounds = get_active_document_bounds()       ## Get boundary box from AutoCAD Dwg.
    #print(f'dwg_bounds: {dwg_bounds}')
    bbox = dwg_bounds
    print(f'Bbox: {bbox}')

    #column_names = list(shape_gdf.columns)
    try:
        column_names.remove('geometry')
    except:
        pass
    #print(f'columns : {columns}')
    #label_name =''

    # Create a StringVar to store the selected column
    #selected_column_var = tk.StringVar()

    # Create a StringVar to store the selected column with the default value (first column)
    selected_column_var = tk.StringVar(value=column_names[0])
    # Create default fontsize
    fontsize_var = tk.DoubleVar(value=2.5)
    # Create default encoding
    encoding_var = tk.StringVar(value='tis-620')
    # Callback function to handle the selected column
    def callback(selected_column_value, fontsize_var, encoding_var):
        #print(f"Callback function received selected column: {selected_column_value}")
        # Use 'selected_column_value' in 'main_function'
        value = [selected_column_value, fontsize_var, encoding_var]

    # Call the function to create and display the dropdown window
    dropdown_window = create_dropdown_window(column_names, selected_column_var, fontsize_var, encoding_var,  callback)
    #dropdown_window = create_dropdown_window(column_names, selected_column_var, fontsize_var, callback)

    # Wait for the dropdown window to be destroyed
    dropdown_window.wait_window(dropdown_window)

    # Wait for the StringVar to be set
    #selected_column_var.get()
    #print(f"Selected column in main_function: {selected_column_var.get()}")

    label_name = selected_column_var.get()
    fontsize = fontsize_var.get()
    encoding = encoding_var.get()
    #print(f'Label name : {label_name}')

    shape_gdf = shp2gdf(file_path, bbox=bbox, encoding=encoding)    ## Read data from Shape file to GeoDF
    #print(shape_gdf['AMPHOE_T'])

    rows = shape_gdf.shape[0]
    ## if No feature in the specified arae
    if (rows==0):
        msg = '>>> There is no feature in the specified area. <<<'
        show_message(msg)
        return 1

    # Convert the column to strings
    shape_gdf[label_name] = shape_gdf[label_name].astype(str)
    print(shape_gdf[label_name])
    shape_gdf.plot(figsize=(7.5, 5.5), color='green')
    plt.title(f'[ {layer} {rows} features] : Data Preview')
    plt.show()

    # Print the data type of the column
    #print(shape_gdf[label_name].dtype)

    # Change the encoding of a specific column
    #label_name_2 = f"{label_name}_2"
    #shape_gdf[label_name_2] = shape_gdf[label_name].str.decode('tis-620', errors='ignore').str.encode('utf-8', errors='ignore')

    # Decode dataframe in Python
    #shape_gdf[label_name] = map(lambda x: x.decode('tis-620', 'strict'), shape_gdf[label_name])
    #print(shape_gdf['AMP_decoded'])

    geoDF2ac(shape_gdf, layer_name=layer.upper(), fieldname=label_name, label_height=fontsize)
    #geoDF2ac(shape_gdf, 'Shp_Parcels', fieldname=label_name)
    #geoDF2ac(shape_gdf, 'Shp_Parcels', fieldname='land_no')
    #geoDF2ac(shape_gdf, layer_name=layer, fieldname='land_no')
    ## End shp2ac()

## Test
#shp2ac()

