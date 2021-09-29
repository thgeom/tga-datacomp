from tkinter import filedialog as fd
from pkg01.datainput import *
from pkg01.dataoutput import *
from pkg02.cadlib import *
import matplotlib.pyplot as plt

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

top = Tk()

# Set up parameters
# :project parameter shall be utilized for data manipulation
def setparams():
    global doc, cadapp
    global workdir, csvfile, csvcolumns, csvencoding
    global xsline_layer, chn_layer
    global xscode_layer, xsname_layer, xspoint_layer
    global xsline_completed_layer
    global completed_color, Buffer
    global filter_code, filter_content
    global xlsfile

    workdir = proj_params['WorkDirectory']
    csvfile = proj_params['CSVDatatFile']
    csvcolumns = proj_params['CSVColumns']
    csvencoding = proj_params['CSVEncoding']
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

    doc = is_cadopen()                          # Checking AutoCAD is opened or not?
    if doc is None:
        return False
    return doc

# Select parameter file
def selectfile():
    global proj_params

    statusbox(sta_label, 'Open parameter file.')
    parfile = fd.askopenfilename(title='Select Parameter File')
    if parfile == '':
        return
    proj_params = getProjParams('', parfile)
    #print(proj_params)
    if proj_params == {}:
        msg = 'Incorrect Parameter File format!!!'
        for i in range(4):
            cad.entryconfig(i, state=DISABLED)
        warn_message(msg)
        return
    conn_ok = setparams()               # Check parameters & CAD connection
    #print(conn_ok)
    if csvfile != '' and workdir != '' and conn_ok:
        cad.entryconfig(0, state=NORMAL)
    if cadapp != '' and workdir != '' and conn_ok:
        #cad.entryconfig(1, state=NORMAL)
        cad.entryconfig(2, state=NORMAL)
        cad.entryconfig(3, state=NORMAL)
        statusbox(sta_label, 'AutoCAD connected.')

# Import CSV & Plot
def plotCSV():
    global csvdata

    csvdata = getCSV(workdir, csvfile, csvcolumns, csvencoding)
    #csvdata.show_data()
    #plt.figure(figsize=(9,9))
    for pt in csvdata.restab.values:
        plt.plot(pt[2], pt[3], 'r+')
    plt.ylabel('Northing')
    plt.xlabel('Easting')
    plt.title('Location of CSV Points')
    plt.show()
    cad.entryconfig(1, state=NORMAL)

# Create points from CSV data
def cr_cadpoints():
    csv2ac(csvdata, xscode_layer, xsname_layer, xspoint_layer)

# Entities selection
def select_by_polygon():
    global doc, ass9

    #filter_code = [0, 1, 8]
    #filter_content = ['Text', 'ป่า', xscode_layer]
    doc = is_cadready()
    if doc is None:
        return False
    objSel = doc.Utility.GetEntity()                  # Get XS_Line entity by pick
    #return (<COMObject GetEntity>, (506465.30556296057, 1861201.4573297906, 0.0))
    obj = objSel[0]
    pnts = getpnts_polygon(obj)
    #print(pnts)
    ass9 = AcSelectionSets('SS9')
    #ass9.ssCond([0, 8], ['Text', xscode_layer])              # Select all as condition
    pnts = vtFloat(pnts)
    ass9.ssPolygonCond(pnts, filter_code, filter_content)  # Select by Polygon as condition
    #print('{} Texts selected'.format(ass9.slset.count))
    msg = '>>>> Total {} Texts selected.'.format(ass9.slset.count)
    show_message(msg)
    cad.entryconfig(4, state=NORMAL)                # Enable Data->Excel menu

    """
    for i in ass9.slset:
        print(i.TextString, ' : ', i.InsertionPoint)
    """

# Create Excel file of selected data
def data2file(slset):
    dt4file = Data4File(workdir, xlsfile)
    dt4file.dtAdd(slset)
    dt4file.show_data()
    dt4file.dt2File(csvencoding)

# For menu call
def dt2file():
    data2file(ass9.slset)

def main():
    global doc, cad, sta_label

    #plotCSV()
    #cadopen = is_cadopen()
    #doc = is_cadready()

    #cr_pl('test_poly')
    #cr_circle('test_circle')
    #select_by_polygon()
    #data2file(ass9.slset)

    menubar = Menu(top)
    file = Menu(menubar, tearoff=0)
    #file.add_command(label="New")
    file.add_command(label="Open", command=selectfile)
    #file.add_command(label="Save")
    #file.add_command(label="Save as...")
    #file.add_command(label="Close")

    file.add_separator()
    file.add_command(label="Exit", command=top.quit)

    menubar.add_cascade(label="File", menu=file)
    cad = Menu(menubar, tearoff=0)
    draw = Menu(menubar, tearoff=0)
    cad.add_command(label="Import points", state=DISABLED, command=plotCSV)
    cad.add_command(label="Create CAD points", state=DISABLED, command=cr_cadpoints)
    cad.add_cascade(label="Draw", state=DISABLED, menu=draw)
    draw.add_command(label='Circle', command=cr_circle)
    draw.add_command(label='Line', state=DISABLED, command=cr_line)
    draw.add_command(label='Polyline', command=cr_pl)
    cad.add_command(label="Select by Polygon", state=DISABLED, command=select_by_polygon)
    #cad.add_command(label="Select by Polygon", command=select_by_polygon)
    cad.add_command(label="Data->Excel", state=DISABLED, command=dt2file)

    cad.add_separator()

    #edit.add_command(label="Cut")
    #edit.add_command(label="Copy")
    #edit.add_command(label="Paste")
    #edit.add_command(label="Delete")
    cad.add_command(label="Select All", state=DISABLED)

    menubar.add_cascade(label="CAD", menu=cad)
    help = Menu(menubar, tearoff=0)
    help.add_command(label="About", state=DISABLED)
    menubar.add_cascade(label="Help", menu=help)

    top.config(menu=menubar)
    top.geometry('605x400')
    top.geometry('+150+100')                 # Position ('+Left+Top')
    top.title('THGeom Academy (Field data & CAD manipulation & Excel output)')
    sta_label = Label(top, text=': ', width=40)
    #sta_label.place(x=-1.0, rely=1.0, anchor='sw')
    sta_label.pack()
    sta_label.place(relx=-0.1, rely=1.0, anchor=SW)
    #top.update()
    top.mainloop()


if __name__ == '__main__':
    main()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
