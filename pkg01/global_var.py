#from tkinter import filedialog as fd
#from pkg03.utility import

from pkg02.cadlib import *
from pkg03.os_test import *

import sys, io
import os
import winsound


global acad, doc, select, top, sta_label, os_version, buffer, ACAD_CRS
#global workdir, csvfile, csvcolumns, csvencoding, dwgfile

os_version = get_os_version()
print(f"Running on operating system: {os_version}")

top = set_root_window()
doc = is_cadready()
#print(doc)
if not doc:
    sys.exit(-1)

### To solve pywintypes.com_error in Windows 11
buffer = io.StringIO()
#sys.stdout = sys.stderr = buffer
#sys.stderr = buffer

# Reset stdout and stderr to their original values
#sys.stdout = sys.__stdout__
#sys.stderr = sys.__stderr__

## Define temporary image folder
dwg_prefix = get_autocad_variable("DWGPREFIX")
dwg_prefix = dwg_prefix.replace('\\', '/')
DWG_PREFIX = dwg_prefix[:-1]

IMAGE_PATHNAME = f"{DWG_PREFIX}/images"
#IMAGE_PATHNAME = 'd:/usr/tmp'
if not os.path.exists(IMAGE_PATHNAME):
    os.makedirs(IMAGE_PATHNAME)

## Define current working directory
CWD = os.getcwd()
CWD = CWD.replace('\\', '/')
#print(f"CWD: {CWD}")

## Define Zoom Level
GGS_Z = 20

def get_datacomp_config():
    datacomp_dir = "d:/TGA_TEST/datacomp/"
    datacomp_file = "datacomp.par"
    file_path = datacomp_dir + datacomp_file

    try:
        datacomp_params = getProjParams(datacomp_dir, datacomp_file)
    except Exception:
        return False

    #print(f"URL Params : {url_req_params}")
    return datacomp_params

"""
datacomp_params = get_datacomp_config()
print(f"datacomp_params : {datacomp_params}")
print(f"TempDirectory : {datacomp_params['TempDirectory']}")
"""


def show_current_crs():
    msg = f"Coordinate Reference System : {ACAD_CRS}"
    print(msg)

def ac_crs_32648(batch=False):
    global ACAD_CRS

    ACAD_CRS = 'EPSG:32648'
    msg = f">>>> Coordinate Reference System (CRS): <{ACAD_CRS}>"
    show_message(msg, batch=batch)
    #show_current_crs()

def ac_crs_32647(batch=False):
    global ACAD_CRS

    ACAD_CRS = 'EPSG:32647'
    msg = f">> Coordinate Reference System (CRS): <{ACAD_CRS}>"
    show_message(msg, batch=batch)


## Get CRS from ACAD drawing
def get_crs_from_acad():
    dwg_useri5 = get_autocad_variable('USERI5')  ## Use USERI5 to store EPSG code
    if dwg_useri5 == 32647:
        ac_crs_32647(batch=True)
    elif dwg_useri5 == 32648:
        ac_crs_32648(batch=True)
    else:
        msg = '>>> EPSG code has not been defined in the drawing <<<'
        show_message(msg, batch=True)
        freq = 500
        dur = 1000
        winsound.Beep(freq, dur)

## Put CRS to ACAD drawing
def put_crs_to_acad():
    #from pkg01.global_var import ACAD_CRS

    epsg = int(ACAD_CRS.rsplit(':')[1])
    set_autocad_variable('USERI5', epsg)
    msg = f"<<< EPSG:{epsg} has been stored to Dwg. >>>"
    doc.SendCommand('_qsave ')
    acprompt(msg + '\n')
    show_message(msg)

## By Default
ACAD_CRS = 'EPSG:32647'
#msg = f"Coordinate Reference System : {ACAD_CRS}"
#print(msg)

## Check EPSG from ACAD drawing
get_crs_from_acad()
