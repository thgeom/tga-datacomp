#import requests
#import math
#import matplotlib.pyplot as plt


from pkg01.global_var import *
from pkg02.ogclib import *
from pkg02.cadlib import *
from pkg02.geom import *

import datetime
import time
#from PIL import Image
#import io

#global top
#top = set_root_window()

def latlon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x_tile = int((lon + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return x_tile, y_tile

## Get image tiiles by given boundary ll&ur
def get_img_tiles(img_layer, zoom, min_lat, min_lon, max_lat, max_lon):
    min_x, min_y = latlon_to_tile(min_lat, min_lon, zoom)
    max_x, max_y = latlon_to_tile(max_lat, max_lon, zoom)
    print(f"min_x, min_y : {min_x} , {min_y}")
    print(f"max_x, max_y : {max_x} , {max_y}")
    ## For Google Satellite
    #img_layer = 'GGS'
    start_datetime = datetime.datetime.now()
    start_time = start_datetime.strftime("%H:%M:%S")
    pycad_prompt('Processing.')
    child_win = Toplevel(top)

    #child_win = Tk()
    child_win.geometry('695x120')
    child_win.geometry('+200+250')
    child_win.title(f"Status of <<< CREATING TILES : [{img_layer}] [Column={max_x - min_x + 1}, Row={min_y - max_y + 1}] @{start_time} >>>")
    child_win.configure(bg='lightgreen')
    child_win.lift()
    # Specify the font size using the 'size' parameter
    label_font = ("Arial", 12)  # Replace "Arial" with your desired font and 12 with the desired font size
    sta_label = Label(child_win, text=': ', width=75, font=label_font)
    msg = f'Creating {img_layer} Tiles [Column={max_x - min_x + 1}, Row={min_y - max_y + 1}] in AutoCAD... @{start_time}\n'
    pycad_prompt(msg)
    prevent_sleep()     ## to prevent sleep mode of windows

    ## Define status window
    def status_win(msg):
        sta_label.configure(text=': ' + msg, width=75, fg='#4488CC', bg='lightgreen')
        sta_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        sta_label.master.update()

    ## Check layer for imgages exist or notp
    if not layerexist(img_layer):
        doc.Layers.Add(img_layer)

    ## Set sys.stdout & sys.stderr equal to buffer for Windows 11 running
    #sys.stdout = sys.stderr = buffer
    #sys.stdout = buffer

    col = 0
    for x in range(min_x, max_x + 1):
        #acprompt('.')
        for y in range(max_y, min_y + 1):
            msg = f"Tile z,x,y : {zoom}, {x}, {y}  of  [{min_x}->{max_x}, {max_y}->{min_y}]"
            #print(msg)
            #if (i % 100) == 0:
            if (y==max_y) and ((col % 2)==0):
                pycad_prompt(msg)       ## Shows only the 1st of y

            try:
                status_win(msg)
            except:
                sys.stdout = sys.__stdout__
                print('Terminated by user!!!')
                return -1

            """
            tile_url = f'https://tile.openstreetmap.de/{zoom}/{x}/{y}.png'
            # Download or process the tile using the URL
            print(f"tile req url: {tile_url}")
            with requests.get(tile_url) as resp:
                resp.raise_for_status() # just in case
                img = Image.open(io.BytesIO(resp.content))
                plt.imshow(img)
                plt.title('OSM Preview')
                plt.show()
            """
            tileObj = TileProperties('Tile Map')
            tileObj.getdata_zxy(img_layer, zoom, x, y)
            #plt.imshow(tileObj.ggm_img)
            #plt.title('Google Map Preview')
            #plt.show()

            """
            # Wait for AutoCAD to become quiescent (optional)
            while not is_quiescent():
                time.sleep(1)
            """

            # tileObj.img_to_acad("d:/usr/tmp/ggm", tileObj.ggm_img, 'GGM')
            if img_layer == 'GGS':
                code = tileObj.img_to_acad(f"d:/usr/tmp", tileObj.ggs_img, img_layer)
            elif img_layer == 'GGM':
                code = tileObj.img_to_acad(f"d:/usr/tmp", tileObj.ggm_img, img_layer)
            elif img_layer == 'OSM':
                code = tileObj.img_to_acad(f"d:/usr/tmp", tileObj.osm_img, img_layer)

            if code == -1:
                #child_win.destroy()
                msg = f'Any error occurred, the image [{img_layer}_{zoom}_{x}_{y}] is not in drawing.\n'
                msg += 'Please save, close and reopen AutoCAD drawing!!!'
                acprompt('Terminated.\n')
                warn_message(msg)
                return -1
            ## End for y
        col += 1
        time.sleep(5)  # Sleep for 5 second
        ## Checking buffer size then clear if > 1M
        ## This checking after Python 3.12,
        buffer_size = buffer.tell()
        #buffer_size = sys.stdout.tell()
        #msg = f"buffer_size : {buffer_size}"
        #show_message(msg)

        if buffer_size > 512000000:
            msg = f"buffer_size : {buffer_size}"
            show_message(msg)
            # Clear the content of z w the buffer
            buffer.truncate(0)
            buffer.seek(0)

        if (col % 10)==0:
            #doc.SendCommand('qsave ')
            msg = f"[{col} columns] have been processed and SAVING..."
            status_win(msg)
            time.sleep(5)  # Sleep for 5 second
            doc.Save()
        ## End for x

    finish_datetime = datetime.datetime.now()
    time_difference = finish_datetime - start_datetime
    #minutes_difference = time_difference.total_seconds() / 60

    # Clear the content of the buffer
    buffer.truncate(0)
    buffer.seek(0)

    try:
        doc.SendCommand('_regen ')
        doc.SendCommand('_qsave ')
        #doc.Regen(1)
    except pywintypes.com_error as e:
        print(f'An error occurred as: {e}')
    except Exception:
        print(f'An UNKNOWN error occurred.!!!')

    ## Reset sys.stdout & sys.stderr to NORMAL state
    sys.stdout = sys.__stdout__
    # sys.stderr = sys.__stderr__

    child_win.destroy()

    #msg = f'[{img_layer}] : [Column={max_x-min_x+1}, Row={min_y-max_y+1}] for {minutes_difference:.1f} minutes, Completed.'
    msg = f"[{img_layer}] : [Column={max_x - min_x + 1}, Row={min_y - max_y + 1}] Completed.\n" \
          f"[Elapsed time >> {str(time_difference).split('.', 1)[0]}]."

    try:
        acprompt('\n' + msg + '\n')
    except pywintypes.com_error:
        print(f'An error occurred at [acprompt]')
    except:
        print(f'An UNKNOWN error occurred.!!!')

    allow_sleep()  ## enable sleep mode of windows
    show_message(msg)
    ## End get_image_tiles

## Example usage
## Google satellite images
def group_img_ggs2ac():
    msg = 'Please define the area required in AutoCAD drawing,\n'
    msg += 'then press OK.'
    show_message(msg)
    dwg_bounds = get_active_document_bounds()
    dwg_bounds = bbox2geo(dwg_bounds)
    print(f"DWG. bounds: {dwg_bounds}")
    img_layer = 'GGS'
    get_img_tiles(img_layer, zoom=20, min_lat=dwg_bounds[1], min_lon=dwg_bounds[0], max_lat=dwg_bounds[3], max_lon=dwg_bounds[2])
    #get_osm_tiles(zoom=14, min_lat=12.5, min_lon=99.5, max_lat=12.7, max_lon=99.7)

## Google map images
def group_img_ggm2ac():
    msg = 'Please define the area required in AutoCAD drawing,\n'
    msg += 'then press OK.'
    show_message(msg)
    dwg_bounds = get_active_document_bounds()
    dwg_bounds = bbox2geo(dwg_bounds)
    print(f"DWG. bounds: {dwg_bounds}")
    img_layer = 'GGM'
    get_img_tiles(img_layer, zoom=19, min_lat=dwg_bounds[1], min_lon=dwg_bounds[0], max_lat=dwg_bounds[3], max_lon=dwg_bounds[2])
    #get_osm_tiles(zoom=14, min_lat=12.5, min_lon=99.5, max_lat=12.7, max_lon=99.7)

## OpenStreetMap images
def group_img_osm2ac():
    msg = 'Please define the area required in AutoCAD drawing,\n'
    msg += 'then press OK.'
    show_message(msg)
    dwg_bounds = get_active_document_bounds()
    dwg_bounds = bbox2geo(dwg_bounds)
    print(f"DWG. bounds: {dwg_bounds}")
    img_layer = 'OSM'
    get_img_tiles(img_layer, zoom=19, min_lat=dwg_bounds[1], min_lon=dwg_bounds[0], max_lat=dwg_bounds[3], max_lon=dwg_bounds[2])
    #get_osm_tiles(zoom=14, min_lat=12.5, min_lon=99.5, max_lat=12.7, max_lon=99.7)
