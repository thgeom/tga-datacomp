from tkinter import *
from pkg02.cadlib import *
from pkg01.dataoutput import *

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
    msg = '>>>> Total {} Entities selected.'.format(ass9.slset.count)
    show_message(msg)
    select.entryconfig(7, state=NORMAL)                # Enable Data->Excel menu

    """
    for i in ass9.slset:
        print(i.TextString, ' : ', i.InsertionPoint)
    """
# Entities selection by specified polygon
def select_by_window():
    global doc, ass9

    #filter_code = [0, 1, 8]
    #filter_content = ['Text', 'ป่า', xscode_layer]
    doc = is_cadready()
    if doc is None:
        return False
    # Get bounds from ACAD window
    dwg_bounds = get_active_document_bounds()
    print(f'Dwg. bounds: {dwg_bounds}')
    ll = dwg_bounds[0:2]
    ur = dwg_bounds[2:4]
    #print(f"ll : {ll}")
    #print(f"ur : {ur}")

    ass9 = AcSelectionSets('SS9')

    """
    try:
        #filter_criteria
        filter_content = filter_criteria
    except:
        filter_content = proj_params['FilterContent']
    """

    #ass9.ssCond([0, 8], ['Text', xscode_layer])              # Select all as condition
    ll_vtpt = pt_vtpt(ll)
    ur_vtpt = pt_vtpt(ur)
    ass9.ssWindowCond(ll_vtpt, ur_vtpt)  # Select by Window as condition

    #ass9.ssWindowCond(ll_vtpt, ur_vtpt, filter_code, filter_content)  # Select by Window as condition
    #print('{} Texts selected'.format(ass9.slset.count))
    msg = f'>>>> Total {ass9.slset.count} Entities selected.'
    print(msg)
    return ass9



# Create Excel file of selected data
def data2file(slset):
    dt4file = Data4File(workdir, xlsfile)
    dt4file.dtAdd(slset)
    #dt4file.show_data()
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
