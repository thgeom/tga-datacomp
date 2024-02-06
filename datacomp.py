#from tkinter import filedialog as fd
#from tkinter import ttk


from pkg01.datainput import *
#from pkg01.url_req import *
#from pkg02.cadlib import *
from pkg02.cad_mani import *

#import matplotlib.pyplot as plt
#import os, sys
import subprocess

from pkg01.wms_test import *
from pkg01.osm_test import *
from pkg01.ggs_test import *
from pkg01.wfs_test import *
#from pkg02.ogclib import *
from pkg01.tiles_test import *
from pkg02.gdf_cad import *
from pkg02.cad_test import *

from PIL import Image, ImageTk
import requests
from io import BytesIO
"""
workdir = "d:/TGA_TEST/datacomp/"
csvfile = "RTK_X-sec.csv"
csvcolumns = ["Code", "Name", "E", "N", "Z"]
csvencoding = "TIS-620"
xscode_layer = "XS_Code"
xsname_layer = "XS_Name"
xspoint_layer = "XS_Point"
xlsfile = "ac_out.xlsx"
"""
global top, sta_label
#top = Tk()

#top = set_root_window()

def status_window(msg):
    sta_label = Label(top, text=': ', width=40)
    statusbox(sta_label, msg)


"""
top.config(menu=menubar)
top.geometry('605x400')
top.geometry('+150+100')                 # Position ('+Left+Top')
top.title('THGeom Academy (Field data & CAD manipulation & Export file)')
sta_label = Label(top, text=': ', width=40)
sta_label.pack()
sta_label.place(relx=-0.1, rely=1.0, anchor=SW)
"""
#sta_label.pack()
#top.withdraw()  # Hide the main window

# Set up parameters
# :project parameter shall be utilized for data manipulation
def setparams():
    global doc, cadapp
    global workdir, csvfile, csvcolumns, csvencoding, dwgfile
    global xsline_layer, chn_layer
    global xscode_layer, xsname_layer, xspoint_layer
    global xsline_completed_layer
    global completed_color, Buffer
    global filter_code, filter_content
    global xlsfile

    workdir = proj_params['WorkDirectory']
    csvfile = proj_params['CSVDataFile']
    csvcolumns = proj_params['CSVColumns']
    csvencoding = proj_params['CSVEncoding']
    dwgfile = proj_params['DrawingFile']
    #outfile = proj_params['OutputCsvFile']
    xlsfile = proj_params['OutputXlsFile']
    cadapp = proj_params['CadApp']
    xsline_layer = proj_params['XSLineLayer']
    chn_layer = proj_params['ChainageLayer']
    xscode_layer = proj_params['XSCodeLayer']
    xsname_layer = proj_params['XSNameLayer']
    xspoint_layer = proj_params['XSPointLayer']

    completed_color = proj_params['CompletedColor']
    xsline_completed_layer = proj_params['XSLineCompletedLayer']
    Buffer = proj_params['Buffer']
    filter_code = proj_params['FilterCode']
    filter_content = proj_params['FilterContent']

    doc = is_autocad_running()                          # Checking AutoCAD is opened or not?
    #return doc

    if doc:
        return doc
    else:
        return False

# Select parameter file
def selectfile():
    global proj_params, doc

    statusbox(sta_label, 'Open parameter file.')
    parfile = fd.askopenfilename(title='Select Parameter File',filetypes=[("Par file", "*.par")])
    if parfile == '':
        return
    proj_params = getProjParams('', parfile)
    #print(proj_params)
    if proj_params == {}:
        msg = 'Incorrect Parameter File format!!!'
        for i in range(3):
            cad.entryconfig(i, state=DISABLED)
        warn_message(msg)
        return
    conn_ok = setparams()               # Check parameters & CAD connection
    #print(f"Connection to AutoCAD is : {conn_ok}")
    if csvfile != '' and workdir != '' and conn_ok:
        cad.entryconfig(0, state=NORMAL)
    if cadapp != '' and workdir != '' and conn_ok:
        cad.entryconfig(1, state=NORMAL)
        #cad.entryconfig(2, state=NORMAL)
        #cad.entryconfig(3, state=NORMAL)
        #select.entryconfig(0, state=NORMAL)
        for i in range(4):
            select.entryconfig(i, state=NORMAL)
        statusbox(sta_label, doc.Name + ' is connected.')
        if doc.Name != dwgfile:
            msg = 'Parameter of DrawFile is not the same as AutoCAD drawing!!!\n'
            msg += '=====================\n'
            msg += f"DrawFile = {dwgfile}\n"
            msg += f"AutoCAD drawing = {doc.Name}"
            warn_message(msg)

# To connect to AutoCAD
def cad_connected_check():
    if is_cadopen():
        msg = 'AutoCAD has been connected.\n'
        show_message(msg)

# Import CSV & Plot
def plotCSV():
    global csvdata

    csvdata = getCSV(workdir, csvfile, csvcolumns, csvencoding)
    #csvdata.show_data()
    plt.figure(figsize=(8,6))
    for pt in csvdata.restab.values:
        plt.plot(pt[2], pt[3], 'r+')
    plt.ylabel('Northing')
    plt.xlabel('Easting')
    plt.title('Location of CSV Points')
    plt.gca().set_aspect('equal')
    plt.show()
    cad.entryconfig(2, state=NORMAL)

# Create points from CSV data
def cr_cadpoints():
    csv2ac(csvdata, xscode_layer, xsname_layer, xspoint_layer)




# Call tga_traverse.exe
def traverse():
    print('Traverse...')
    #os.system('d:/TGA_TEST/datacomp/tga_traverse.exe')
    subprocess.call('d:/TGA_TEST/datacomp/tga_traverse.exe')

def main():
    global acad, doc, cad, select, top, sta_label

    #top = set_root_window()
    #doc = None
    #print(f'AutoCAD running : {is_autocad_running()}')
    menubar = Menu(top)
    # Add File menu
    file = Menu(menubar, tearoff=0)
    #file.add_command(label="New")
    file.add_command(label="Open", command=selectfile)
    #file.add_command(label="Save")
    #file.add_command(label="Save as...")
    #file.add_command(label="Close")
    file.add_separator()
    file.add_command(label="Exit", command=top.quit)
    menubar.add_cascade(label="File", menu=file)

    # Add CAD menu
    cad = Menu(menubar, tearoff=0)
    cad.add_command(label="Import points", state=DISABLED, command=plotCSV)
    cad.add_command(label="CAD connection checking", state=DISABLED, command=cad_connected_check)
    cad.add_command(label="Create CAD points", state=DISABLED, command=cr_cadpoints)

    # Add Draw submenu
    draw = Menu(menubar, tearoff=0)
    cad.add_cascade(label="Draw", state=DISABLED, menu=draw)
    draw.add_command(label='Circle', command=cr_circle)
    draw.add_command(label='Line', state=DISABLED, command=cr_line)
    draw.add_command(label='Polyline', command=cr_pl)
    menubar.add_cascade(label="CAD", menu=cad)

    """
    # Add Draw submenu
    edit = Menu(menubar, tearoff=0)
    edit.add_command(label="Cut")
    edit.add_command(label="Copy")
    edit.add_command(label="Paste")
    edit.add_command(label="Delete")
    menubar.add_cascade(label="Edit", menu=edit)
    """

    # Add Select menu
    select = Menu(menubar, tearoff=0)
    select.add_command(label="Select LWPolyline", state=DISABLED, command=select_by_clicklw)
    select.add_command(label="Select Entities", state=DISABLED, command=select_by_entities)
    select.add_command(label="Select by Polygon", state=DISABLED, command=select_by_polygon)
    #cad.add_command(label="Select by Polygon", command=select_by_polygon)
    select.add_command(label="Define Criteria >>", state=DISABLED, command=sel_criteria)
    select.add_command(label="Select by Criteria", state=DISABLED, command=select_by_criteria)
    select.add_separator()
    select.add_command(label="LWPolyline->Txt", state=DISABLED, command=dt2txt)
    select.add_command(label="Data->Excel", state=DISABLED, command=dt2file)
    select.add_separator()
    select.add_command(label="Select All", state=DISABLED)
    menubar.add_cascade(label="Select", menu=select)

    # Add Calc menu
    calculate = Menu(menubar, tearoff=0)
    calculate.add_command(label="Traverse", command=traverse)
    calculate.add_command(label="Volume", state=DISABLED)
    menubar.add_cascade(label="Calc", menu=calculate)

    # Add Tools menu
    tools = Menu(menubar, tearoff=0)
    tools.add_command(label="OSM Edges->Dwg", command=osm2ac)
    tools.add_command(label="OSM Image->Dwg", command=img_osm2ac)
    tools.add_command(label="Google Map->Dwg", command=img_ggm2ac)
    tools.add_command(label="Google Satellite->Dwg", command=img_ggs2ac)
    tools.add_command(label="Z-19 OpenStreetMaps->Dwg", command=group_img_osm2ac)
    tools.add_command(label="Z-19 Google Maps->Dwg", command=group_img_ggm2ac)
    tools.add_command(label="Z-20 Google Satellites->Dwg", command=group_img_ggs2ac)

    tools.add_separator()
    tools.add_command(label="Parcels->Dwg", state=DISABLED, command=parcel2dwg)
    tools.add_command(label="Parcels->Shp", state=DISABLED, command=parcel2shp)
    tools.add_command(label="Parcels Image->Dwg", state=DISABLED, command=dol_wms2ac)

    tools.add_separator()
    tools.add_command(label="OWS GetLayers", state=DISABLED,command=getLayers)
    tools.add_command(label="WMS->Dwg", state=DISABLED,command=get_wms2ac)
    tools.add_command(label="WFS->Dwg", state=DISABLED,command=get_wfs2ac)
    tools.add_separator()
    tools.add_command(label="Import Shape File", command=shp2ac)
    tools.add_command(label="Export Shape/KML File", command=ac2shp)
    menubar.add_cascade(label="Tools", menu=tools)

    # Add Setting menu
    setting = Menu(menubar, tearoff=0)
    setting.add_command(label="Prevent Sleep", command=prevent_sleep)
    setting.add_command(label="Allow Sleep", command=allow_sleep)
    menubar.add_cascade(label="Setting", menu=setting)

    # Add Help menu
    help = Menu(menubar, tearoff=0)
    help.add_command(label="About", state=DISABLED)
    menubar.add_cascade(label="Help", menu=help)



    top.geometry('795x440')
    top.geometry('+250+100')                 # Position ('+Left+Top')
    top.resizable(0, 0)  # Don't allow resizing in the x or y direction
    top.title('THGeom Academy (Import Field, Web services data & CAD manipulation & Export): [Trial Version.]')

    # Create a photoimage object of the image in the path
    #thgeom_img = Image.open("D:/TGA_TEST/datacomp/THGA_Logo5_200x200-nobg.png")
    #thgeom_img = Image.open("D:/TGA_TEST/datacomp/TGA_CoverPage-L9.png")

    #thgeom_img = Image.open("D:/TGA_TEST/datacomp/thga_logo5-r.jpg")
    """
    # Provide the URL as a string
    image_url = "https://thgeomacademy.files.wordpress.com/2024/01/thga_logo5_200x200-nobg.png"

    # Download the image from the URL
    response = requests.get(image_url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        try:
            # Try to open the image using PIL
            thgeom_img = Image.open(BytesIO(response.content))

            # Now you can use the thgeom_img object as needed
            # For example, you can display the image:
            thgeom_img.show()
        except Exception as e:
            # Print the error for further investigation
            print(f"Error: {e}")
    else:
        print(f"Error: Unable to fetch the image. Status Code: {response.status_code}")
    """
    # Get image by given url
    def get_url_image(url):
        # make the request
        #print(f"url: {url}")
        with requests.get(url) as resp:
            resp.raise_for_status()  # just in case
            img = Image.open(io.BytesIO(resp.content))
        return img

    # Create background image
    #img_url = "https://raw.githubusercontent.com/thgeom/tga-datacomp/master/TGA_CoverPage-L9.png"
    img_url = "https://raw.githubusercontent.com/thgeom/tga-datacomp/master/TGA_CoverPage-2.png"
    thgeom_img = get_url_image(img_url)

    #thgeom_img = thgeom_img.resize((150, 150), 0)  # For Logo
    #thgeom_img = thgeom_img.resize((515, 278), 0)  # For BG _L9.png
    thgeom_img = thgeom_img.resize((684, 260), 0)  # For BG -2.png
    photo = ImageTk.PhotoImage(thgeom_img)

    thgeom_label = Label(top, image=photo)
    #thgeom_label = Label(top, image=thgeom_img)
    #label.image = photo
    # Position image
    #thgeom_label.place(x=325, y=100)   # For Logo
    #thgeom_label.place(x=140, y=50)    # For BG _L9.png
    thgeom_label.place(x=55, y=75)  # For BG -2.png

    # Create Icon for top window
    ico_url = "https://raw.githubusercontent.com/thgeom/tga-datacomp/master/THGA_Logo5_200x200-nobg.png"
    thgeom_ico = get_url_image(ico_url)
    ico = ImageTk.PhotoImage(thgeom_ico)
    top.wm_iconphoto(False, ico)

    top.config(menu=menubar)
    top.lift()

    sta_label = Label(top, text=': ', width=60)
    #sta_label.place(x=-1.0, rely=1.0, anchor='sw')
    sta_label.pack()
    sta_label.place(relx=-0.1, rely=1.0, anchor=SW)
    #top.update()

    ## Check url request parameter file exist or not
    ## if not "Parcel-->Dwg" will not active
    if url_params:
        [tools.entryconfig(i, state=NORMAL) for i in range(8,11)]
        [tools.entryconfig(i, state=NORMAL) for i in range(12,15)]
        #tools.entryconfig(10, state=NORMAL)
        """
        tools.entryconfig(2, state=NORMAL)
        tools.entryconfig(3, state=NORMAL)
        tools.entryconfig(4, state=NORMAL)
        """
    else:
        print('INCORRECT URL PARAMETERS : SOME FUNCTIONS WILL BE DISABLED!!!')

    top.mainloop()


if __name__ == '__main__':
    main()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
