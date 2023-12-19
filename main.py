from tkinter import filedialog as fd
from tkinter import ttk
from pkg01.datainput import *
from pkg01.dataoutput import *
from pkg02.cadlib import *
import matplotlib.pyplot as plt
#import os, sys
import subprocess

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
    csvfile = proj_params['CSVDatatFile']
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

    doc = is_cadready()                          # Checking AutoCAD is opened or not?
    if doc is None:
        return False
    return doc

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
        #cad.entryconfig(1, state=NORMAL)
        cad.entryconfig(2, state=NORMAL)
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
    cad.entryconfig(1, state=NORMAL)

# Create points from CSV data
def cr_cadpoints():
    csv2ac(csvdata, xscode_layer, xsname_layer, xspoint_layer)

# Setting Criteria
def sel_criteria():
    cond_w = Tk()
    cond_w.geometry("350x180+400+200")   # Size & Position of the window
    cond_w.title("Selection Criteria")   # Adding a title
    def criteria_set():
        global filter_criteria

        sel_typ = cb1.get()           # selected option
        sel_lay = cb2.get()
        filter_criteria = [sel_typ, sel_lay]

        print('Selection Criteria : {} <==> {}'.format(filter_code, filter_criteria))
        select.entryconfig(4, state=NORMAL)
        cond_w.destroy()

    def criteria_clear():
        global filter_criteria

        try:
            #filter_criteria
            del filter_criteria
            print('Selection Criteria has been deleted.')
            select.entryconfig(4, state=DISABLED)
        except:
            pass

    l1 = Label(master=cond_w, text="Entity type : ", width=12)
    l1.grid(row=1,column=1)
    typ_conds=['Point','Text', 'Circle'] # options
    cb1 = ttk.Combobox(cond_w, values=typ_conds, width=10)  # Combobox
    cb1.grid(row=1, column=2, padx=10, pady=20)             # adding to grid
    cb1.set("Point")
    l2= Label(master=cond_w, text="Entity layer : ", width=12)
    l2.grid(row=2,column=1)
    lay_conds=['*','XS_Code'] # options
    cb2 = ttk.Combobox(cond_w, values=lay_conds, width=10)  # Combobox
    cb2.grid(row=2, column=2, padx=10, pady=5)             # adding to grid
    cb2.set("*")
    b1 = Button(cond_w,text=" OK ", command=criteria_set)
    b1.grid(row=3,column=2, padx=20, pady=25)
    b2 = Button(cond_w,text=" Clear ", command=criteria_clear)
    b2.grid(row=3,column=3, padx=20, pady=25)
    cond_w.mainloop()   # Keep the window open

# Entities selection
def select_by_entities():
    global doc, ass9

    doc = is_cadready()
    if doc is None:
        return False
    objSel = ()
    try:
        ass9
    except:
        ass9 = AcSelectionSets('SS9')

    while objSel != None:
        try:
            doc.Utility.Prompt('Select [Point/Text] <Enter to end>')
            objSel = doc.Utility.GetEntity()                  # Get entity by pick
            #return (<COMObject GetEntity>, (506465.30556296057, 1861201.4573297906, 0.0))
        except:
            objSel = None
        #print(objSel)
        if objSel is not None:
            obj = objSel[0]
            if obj.EntityName == 'AcDbPoint' or obj.EntityName == 'AcDbText':
                ass9.slset.AddItems(vtobj([obj]))

    if ass9.slset.count > 0:
        msg = '>>>> Total {} Entities selected.'.format(ass9.slset.count)
        show_message(msg)
        select.entryconfig(7, state=NORMAL)                # Enable Data->Excel menu

# Entities selection by specified criteria
def select_by_criteria():
    global doc, ass9

    filter_code = [0, 8]
    #filter_cont = ['Text', 'XS_Code']
    try:
        filter_criteria
    except:
        print('Criteria not defined!!!')
        return
    doc = is_cadready()
    if doc is None:
        return False

    try:
        ass9
    except:
        ass9 = AcSelectionSets('SS9')
    ass9.ssCond(filter_code, filter_criteria)              # Select all as condition
    msg = '>>>> Total {} Entities selected.'.format(ass9.slset.count)
    show_message(msg)
    select.entryconfig(7, state=NORMAL)                # Enable Data->Excel menu

# LWPolyline Entities selection
def select_by_clicklw():
    global doc, ass8

    doc = is_cadready()
    if doc is None:
        return False
    objSel = ()
    try:
        ass8
    except:
        ass8 = AcSelectionSets('SS8')

    while objSel != None:
        try:
            doc.Utility.Prompt('Select LWPolyline <Enter to end>')
            objSel = doc.Utility.GetEntity()                  # Get entity by pick
            #return (<COMObject GetEntity>, (506465.30556296057, 1861201.4573297906, 0.0))
        except:
            objSel = None
        #print(objSel)
        if objSel is not None:
            obj = objSel[0]
            if obj.EntityName == 'AcDbPolyline':
                ass8.slset.AddItems(vtobj([obj]))

    if ass8.slset.count > 0:
        msg = '>>>> Total {} Entities selected.'.format(ass8.slset.count)
        show_message(msg)
        select.entryconfig(6, state=NORMAL)                # Enable Data->Txt menu

# Entities selection by specified polygon
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

    try:
        #filter_criteria
        filter_content = filter_criteria
    except:
        filter_content = proj_params['FilterContent']

    #ass9.ssCond([0, 8], ['Text', xscode_layer])              # Select all as condition
    pnts = vtFloat(pnts)
    ass9.ssPolygonCond(pnts, filter_code, filter_content)  # Select by Polygon as condition
    #print('{} Texts selected'.format(ass9.slset.count))
    msg = '>>>> Total {} Entitiess selected.'.format(ass9.slset.count)
    show_message(msg)
    select.entryconfig(7, state=NORMAL)                # Enable Data->Excel menu

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

# For menu call : Data->CSV
def dt2txt():
    txtoutfile = "Out.txt"
    dt4txt = Data4Txt(workdir, txtoutfile)
    dt4txt.dtAdd(ass8.slset)
    dt4txt.show_data()
    dt4txt.dt2TxtFile()

# For menu call
def dt2file():
    data2file(ass9.slset)

# Call tga_traverse.exe
def traverse():
    print('Traverse...')
    #os.system('d:/TGA_TEST/datacomp/tga_traverse.exe')
    subprocess.call('d:/TGA_TEST/datacomp/tga_traverse.exe')

def main():
    global acad, doc, cad, select, sta_label

    #plotCSV()
    #cadopen = is_cadopen()
    #doc = is_cadready()

    #cr_pl('test_poly')
    #cr_circle('test_circle')
    #select_by_polygon()
    #data2file(ass9.slset)

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

    # Add Help menu
    help = Menu(menubar, tearoff=0)
    help.add_command(label="About", state=DISABLED)
    menubar.add_cascade(label="Help", menu=help)

    top.config(menu=menubar)
    top.geometry('605x400')
    top.geometry('+150+100')                 # Position ('+Left+Top')
    top.title('THGeom Academy (Field data & CAD manipulation & Export file)')
    sta_label = Label(top, text=': ', width=40)
    #sta_label.place(x=-1.0, rely=1.0, anchor='sw')
    sta_label.pack()
    sta_label.place(relx=-0.1, rely=1.0, anchor=SW)
    #top.update()
    top.mainloop()


if __name__ == '__main__':
    main()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
