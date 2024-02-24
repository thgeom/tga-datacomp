from pkg01.url_req import *
from pkg02.cadlib import *
import matplotlib.pyplot as plt
from datetime import datetime

#import matplotlib.image as mpimg
#import numpy as np
from PIL import Image
import io

# Add WMS layer
def getWMSdata(wms_url, wms_layer, viewpar, npixel, bounds, crs='EPSG:4326', srsname='EPSG:4326'):

    # Craft your new WMS GetMap request URL based on the new extent
    wms_request_url = f"{wms_url}?service=WMS&version=1.1.1&request=GetMap&layers={wms_layer}&viewparams={viewpar}&WIDTH={npixel}&HEIGHT={npixel}" \
                      f"&bbox={bounds[0]},{bounds[1]},{bounds[2]},{bounds[3]}&crs={crs}&format=image/geotiff&transparent=TRUE&srsname={srsname}&exceptions=application/vnd.ogc.se_inimage"

    # Print or process the WMS request URL as needed
    #print("WMS Request:", wms_request_url)
    print("WMS Request URL:", wms_url)
    print(f"Req. bounds: {bounds}")

    try:
        wms_byte = requests.get(wms_request_url, timeout=20)
    except requests.exceptions.Timeout:
        print("Request to WMS timed out. Try again later or reduce the data scope.")
        return None
    except requests.exceptions.ConnectionError:
        print('WMS error occurred, no parcel data!!!!')
        return None
    except Exception:
        print('An error occurred, no parcel data!!!!')
        return None

    if wms_byte:
        wms_img = wms_byte.content
         #print(wfs_str)
        return wms_img
    else:
        return None

## Make Image transparent by color range
def make_color_range_transparent(image, target_color, tolerance=30):
    """
    Make a range of colors in the image transparent based on a target color and tolerance.
    """
    rgba_image = image.convert("RGBA")
    width, height = rgba_image.size

    # Create a new image with fully transparent background
    transparent_bg_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Define the color range based on the target color and tolerance
    min_color = (target_color[0] - tolerance, target_color[1] - tolerance, target_color[2] - tolerance)
    max_color = (target_color[0] + tolerance, target_color[1] + tolerance, target_color[2] + tolerance)

    # Make pixels within the color range transparent
    print(f'Image transparency processing...')
    for x in range(width):
        for y in range(height):
            pixel = rgba_image.getpixel((x, y))
            if min_color[0] <= pixel[0] <= max_color[0] and \
                    min_color[1] <= pixel[1] <= max_color[1] and \
                    min_color[2] <= pixel[2] <= max_color[2]:
                transparent_bg_image.putpixel((x, y), (0, 0, 0, 0))
            else:
                transparent_bg_image.putpixel((x, y), pixel)

    return transparent_bg_image


# WMS to AutoCAD
def wms2ac(wms_url, wms_layer, view_params, npixel=256):
    from pkg01.global_var import ACAD_CRS
    global acad, doc

    # Check AutoCAD ready or not
    doc = is_cadready()
    if not doc:
        return False

    acad = win32com.client.Dispatch("AutoCAD.Application")
    #acprompt = doc.Utility.Prompt
    ms = doc.ModelSpace
    dwg_bounds = get_active_document_bounds()
    #dwg_bounds = bbox2geo(dwg_bounds)
    x_size = dwg_bounds[2] - dwg_bounds[0]
    y_size = dwg_bounds[3] - dwg_bounds[1]
    m_size = max(x_size, y_size)                        # compute max. size of X&Y
    #m_size = (2 * x_size + y_size) / 3
    ur = (dwg_bounds[0] + m_size, dwg_bounds[1] + m_size)
    b_box = dwg_bounds[0:2] + ur
    #m_size = min(x_size, y_size)
    #ur = dwg_bounds[2:4]
    #b_box = (98.5, 5.5, 105.5, 21.5)
    #print(f"dol_ows_url: {dol_ows_url}")
    #print(f"m_size: {m_size}")

    ## For DOL case
    if (wms_url == dol_ows_url):
        layer = 'parcels'
        if (m_size > 1200):
            print('Please reduce the specified area!!!, then try again.') ## For DOL case
            print('Specified area must less than 1200 m. by 1200 m.')
            return None
    else:
        layer = wms_layer.rsplit(':')[1]    ## Not DOL layer

    #wms_data = getWMSdata(wms_url,wms_layer,viewpar='',npixel=2048,bounds=[dwg_bounds[0:2],dwg_bounds[2:4]],crs='EPSG:32647',srsname='EPSG:32647')
    wms_data = getWMSdata(wms_url,wms_layer,viewpar=view_params,npixel=npixel,bounds=b_box,crs=ACAD_CRS,srsname=ACAD_CRS)
    if wms_data:
        wms_img = Image.open(io.BytesIO(wms_data))
    else:
        return None
    #img_array = np.asarray(imgx, dtype=np.float32)

    plt.imshow(wms_img)
    plt.title(f'[{layer}] : Web Map Service Preview')
    plt.show()
    now = datetime.now()                                    # current date and time
    date_time = now.strftime("%m%d%Y%H%M%S")
    wms_img_path = f"{IMAGE_PATHNAME}/wms_image_{date_time}.gif"  # define temporary file
    #wms_img.apply_transparency()

    # Specify the target color and tolerance for the color range
    target_color = (255, 255, 255)  # Example: White background
    tolerance = 20

    # Apply transparency to the color range
    #result_img = make_color_range_transparent(wms_img, target_color, tolerance)
    result_img = wms_img

    #result_img.save(wms_img_path, format="PNG")
    result_img.save(wms_img_path)

    #print(ms.__dir__())
    #print(ms.AddRaster())
    #image_def = ms.AddRaster(img_path, pt_vtpt(dwg_bounds[0:2]), dwg_bounds[2:4][0] - dwg_bounds[0:2][0], 0)

    image_ent = add_image(wms_img_path, dwg_bounds[0:2], m_size, 0, f'WMS_{layer}')
    #image_entity = image_def[0]
    chProp(image_ent, 70, 15)               # set image to transparency
    #chProp(image_ent, 8, 'WMS')
    doc.Regen(1)
    print(f"WMS image has been added to AutoCAD drawing.")
    #print(f"image_ent: {image_ent}")
    # End wms2ac()

#wms_url = "https://geoserver.thgeom-academy.com/geoserver/thgeom/wms"
#wms_layer = "thgeom:province"
#dol_ows_url = "https://landsmaps.dol.go.th/geoserver/LANDSMAPS/ows"
#dol_layer_name = 'V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO,V_PARCEL47_LANDNO'
#dol_view_params = 'utmmap:51363,utmmap:51364,utmmap:50362,utmmap:50361'

# Test Province
#wms2ac(wms_url,wms_layer,'')

# Test DOL
def dol_wms2ac():
    wms2ac(dol_ows_url, dol_layer_name, dol_view_params, npixel=1408)

# Test get_wms2ac by Province layer
def get_wms2ac():
    wms2ac(wms_url,wms_layer,'', npixel=1024)