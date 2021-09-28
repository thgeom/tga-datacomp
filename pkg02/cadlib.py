import win32com.client                                                  # For Application connection
import pythoncom
from pkg03.utility import *

acad = win32com.client.Dispatch("AutoCAD.Application")                  # AutoCAD connection
"""
Require pywin32
"""
#doc = acad.ActiveDocument
#print(dir(acad))

# Check AutoCAD Opened?
def is_cadopen():
    cadopen = False

    #print(dir(acad))
    if acad.Visible:
        cadopen = True
        #return doc
    else:
        msg = 'AutoCAD is not Running!!!\n'
        msg += 'Please open AutoCAD Drawing then try again.'
        warn_message(msg)
    return cadopen

# Verify AutoCAD connection
def is_cadready():
    global doc, acprompt, ms
    cadready = False
    try:
        doc = acad.ActiveDocument
        acprompt = doc.Utility.Prompt                                   # ACAD prompt
        ms = doc.ModelSpace
        #print(doc)
        print('File {} connected.'.format(doc.Name))
        #doc.Utility.Prompt("Execute from python\n")
        cadready = True
        #return doc
    except AttributeError:
        #print('Connect to AutoCAD failed!!!')
        #print('Press Esc on AutoCAD window then try again.')
        msg = 'AutoCAD currently in use!!!\n'
        msg += 'Press Esc on AutoCAD window then try again.'
        warn_message(msg)
        return cadready
    return doc

# Declare code dictionary
codedict = {0:['Text', 'Line', 'Circle'], 1:['TextString', None, None], 8:['Layer', 'Layer', 'Layer'],
            40:['Height', None, 'Radius'], 50:['Rotation', None, None], 62:['Color', 'Color', 'Color']}

# Coordinate conversion
def vtpt(x, y, z=0):
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, z))

def vtobj(obj):
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, obj)

def vtFloat(lis):
    """ list converted to floating points"""
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, lis)

def vtint(val):
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_I2, val)

def vtvariant(var):
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, var)

# Convert pt to vtpt
def pt_vtpt(pt):
    if len(pt)==2:
        return vtpt(pt[0], pt[1])
    else:
        return vtpt(pt[0], pt[1], pt[2])

# Get Pnts from given polygon object
def getpnts_polygon(obj):
    plpts = list(polyvertex(obj))
    plpts.append(plpts[0])
    plpts.append(plpts[1])
    #print(plpts)
    pnts = []
    nopts = len(plpts) // 2
    for i in range(nopts):
        pnts.append(plpts[i * 2])
        pnts.append(plpts[i * 2 + 1])
        pnts.append(0.0)
    return pnts

# Polar function by giving point, angle, distance & Return 3D point(z=0)
def polar(p, a, d):
    x = p[0] + d * math.cos(a)
    y = p[1] + d * math.sin(a)
    return[x, y, 0.0]

# Distance function by giving 2D point1, point2
def distance(p, q):
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    return math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))

# Angle function by giving 2D point1, point2
def angle(p, q):
    dx = q[0] - p[0]
    dy = q[1] - p[1]
    return math.atan2(dy, dx)

# Compute boundary of giving Line entity & buffer
def line_bounds(e, b):
    al = e.Angle + math.pi * 0.5
    ar = e.Angle - math.pi * 0.5
    p1 = e.StartPoint
    p2 = e.EndPoint
    p11 = polar(p1, al, b)
    p12 = polar(p1, ar, b)
    p21 = polar(p2, al, b)
    p22 = polar(p2, ar, b)
    return [p11, p12, p22, p21, p11]

# Get vertexes of define polygon
def polyvertex(obj):
    plvts = obj.Coordinates
    return plvts

# Checking layer exist or not
def layerexist(lay):
    layers = doc.Layers
    layers_nums = layers.count
    layers_names = [layers.Item(i).Name for i in range(layers_nums)]    # List of ACAD layers
    if lay in layers_names:
        return True
    else:
        return False

# AutoCAD entity creation
# Create point
def make_point(pt, lay=''):
    pointObj = ms.AddPoint(pt_vtpt(pt))
    if lay != '':
        if not layerexist(lay):
            doc.Layers.Add(lay)
        pointObj.Layer = lay
    return pointObj

# Create line
def make_line(p1, p2, lay=''):
    lineObj = ms.AddLine(pt_vtpt(p1), pt_vtpt(p2))
    if lay != '':
        if not layerexist(lay):
            doc.Layers.Add(lay)
        lineObj.Layer = lay
    return lineObj

# Create polyline
def make_pline(pts, lay=''):
    plineObj = ms.AddPolyline(vtFloat(pts2pnts(pts)))
    if lay != '':
        if not layerexist(lay):
            doc.Layers.Add(lay)
        plineObj.Layer = lay
    return plineObj

# Create circle
def make_circle(pt, r, lay=''):
    circleObj = ms.AddCircle(pt_vtpt(pt), r)
    if lay != '':
        if not layerexist(lay):
            doc.Layers.Add(lay)
        circleObj.Layer = lay
    return circleObj

# Create Text
def ptxt(txt, pt, ht, lay):
    textObj = ms.AddText(txt, pt_vtpt(pt), ht)
    if not layerexist(lay):
        doc.Layers.Add(lay)
    textObj.Layer = lay
    return textObj

# Prompt on Python & AutoCAD window
def pycad_prompt(msg):
    print(msg)
    doc.Utility.Prompt(msg + '\n')

# Select entities by filter codes
def sscode(ss_name, ftyp, ftdt):
    """
    # Filtered of Line on layer XS_Line (Example)
    ftyp = [0, 8]
    ftdt = ["Line", 'XS_line']                                  # Filter with Line & XS_Line layer
    """
    # Add the name "SS0" selection set
    try:
        doc.SelectionSets.Item(ss_name).Delete()
    except:
        print("Delete selection failed")
    ssres = doc.SelectionSets.Add(ss_name)

    # Set format of filter
    filterType = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_I2, ftyp)
    filterData = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, ftdt)
    ssres.Select(5, 0, 0, filterType, filterData)            # Select all with filtering
    return ssres

# Change selection set property by etype & code
def chg_ss_bycode(ss, etype, code, val):
    i = 0
    for e in ss:
        #print(dir(e))p
        #evar = 'e.' + codedict[code]
        #exec("%s = %s" % (evar, val))
        #print(codedict[code][codedict[0].index(etype)])
        try:
            setattr(e, codedict[code][codedict[0].index(etype)], val)                 # Assign val to e.variable
            i += 1
        except:
            print('{} can not be changed'.format(codedict[code][codedict[0].index(etype)]))
        #str = evar + '= val'
        #exec(str)
        #print(str)
        """
        if code==1:
            e.TextString = val
        if code==8:
            e.Layer = val
        if code==40:
            e.Height = val
        if code==50:
            e.Rotation = val
        if code==62:
            e.Color = val
        """

    print('Number of entities {}/{} have been changed.'.format(i, ss.count))
    return ss


# Class of AutoCAD Selection set
class AcSelectionSets:
    num_ss = 0
    def __init__(self, ss_name):
        self.ss_name = ss_name
        self._initslset()
        AcSelectionSets.num_ss += 1

    def _initslset(self):
        # Add the name "ss_name" selection set
        try:
            doc.SelectionSets.Item(self.ss_name).Delete()
        except:
            print("Delete selection failed")
        self.slset = doc.SelectionSets.Add(self.ss_name)

    def ssCond(self, ftyp, ftdt):
        # Set format of filter
        filterType = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_I2, ftyp)
        filterData = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, ftdt)
        self.slset.Select(5, 0, 0, filterType, filterData)            # Select all with filtering
        print('{} entities have been selected.'.format(self.slset.count))

    def ssPolygonCond(self, pnts, ftyp, ftdt):
        # Set format of filter
        filterType = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_I2, ftyp)
        filterData = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, ftdt)
        self.slset.SelectByPolygon(6, pnts, filterType, filterData)            # Select all with filtering
        print('{} entities have been selected.'.format(self.slset.count))

    def chProp(self, code, val):
        i = 0
        if code==8 and not layerexist(val):                         # If code=8 & layer not exist add it
            doc.Layers.Add(val)
        for e in self.slset:
            #etype = e.EntityName.replace('AcDb', '')
            etype = e.EntityName[4:]                                # EntityName = 'AcDbCircle'
            #print(etype)
            try:
                setattr(e, codedict[code][codedict[0].index(etype)], val)                 # Assign val to e.variable
                i += 1
            except:
                #print('{} can not be changed'.format(codedict[code][codedict[0].index(etype)]))
                print('{}: can not be changed by code = {}'.format(etype, code))
        pycad_prompt('Number of entities {}/{} have been changed.'.format(i, self.slset.count))

# Get pick points from CAD window
def getpts(msg):
    pts = []
    pt = []
    pt0 = []
    #print(dir(doc.Utility))
    i = 0
    while pt != None:
        try:
            doc.Utility.Prompt(msg + ' No.{} <enter to end> : '.format(i+1))
            if i>0:
                #print('Start point:', pt_vtpt(pt0))
                pt = doc.Utility.GetPoint(pt_vtpt(pt0))         # GetPoint with draw line from prev. point
                cmd = '(grdraw ' + '\'' + str(pt0).replace(",", "") + '\'' + str(pt).replace(",", "") + ' 1) '
                doc.SendCommand(cmd)                            # Send (grdraw p1 p2 1) in AutoLISP format
            else:
                pt = doc.Utility.GetPoint()                     # Get 1st point
            pts.append(pt)
            pt0 = pt
            i += 1
        except:
            pt = None
    return pts

# Convert points array to list
def pts2pnts(pts):
    pnts = ()                                           # init. tuple
    for p in pts:
        pnts = pnts + p                                 # Add tuples
    return list(pnts)                                   # Convert to List

# Create line by specified layer
def cr_line(lay=''):
    pts = getpts('Pick line point')
    if len(pts)>1:
        lineObj = make_line(pts[0], pts[1], lay)
        return lineObj

# Create polyline by specified layer
def cr_pl(lay=''):
    pts = getpts('Pick polyline point')
    if len(pts)>1:
        plObj = make_pline(pts, lay)
        #plObj = make_pline(pts, 'test_pl_lay')
        return plObj

# Create circle by specified layer
def cr_circle(lay=''):
    doc = is_cadready()
    if doc is None:
        return False
    cc = r = None
    #print(doc)
    doc.Utility.Prompt('Pick center of circle:')
    try:
        cc = doc.Utility.GetPoint()
    except:
        cc = None
    doc.Utility.Prompt('Enter radius of circle:')
    try:
        r = doc.Utility.GetReal()
    except:
        r = None
    if cc and r:
        ccObj = make_circle(cc, r, lay)
        doc.Application.Update()
        return ccObj
    return None

# Draw points in CAD
def pts2ac(pts, code_lay, name_lay, point_lay):
    #To create entities of RTK points
    p1 = [0.0, 0.0, 0.0]
    i = 0
    print('Processing.', end='')
    acprompt('Points processing.')
    for pt in pts.restab.values:
        p1[0] = pt[2]
        p1[1] = pt[3]
        p1[2] = pt[4]
        code = pt[0]
        name = pt[1]
        #print('Processing point : ' + name)
        if (i % 20) == 0:
            print('.', end='')                                        # Print dot for every 20 points
            acprompt('.')

        p_code = ms.AddText(code, pt_vtpt(p1), 1.5)
        p_code.Layer = code_lay                                       # Define Code layer
        p_code.Rotation = math.pi * 0.45
        p_name = ms.AddText(name, pt_vtpt(p1), 2)
        p_name.Layer = name_lay                                        # Define Name layer
        p_pt = ms.AddPoint(pt_vtpt(p1))
        p_pt.Layer = point_lay                                         # Define Point layer
        i = i + 1
    msg = '\nTotal RTK {0:d} points imported to DWG.'.format(i)
    acprompt(msg + '\n')  # Echo to ACAD with format
    #print('\nTotal RTK point = ' + str(i) + ', imported to DWG.')
    show_message(msg)                   # Print with format

#==========
def csv2ac(csvdt, code_lay, name_lay, point_lay):
    doc = is_cadready()
    if doc is None:
        return False
    print('Drawing Name is {}'.format(doc.Name))                        # Print ACAD Dwg. name
    print('Import Field data CSV format')
    #acprompt('Hi, from Python : To manage RTK\n')
    acprompt('CSV file importing...\n')

    if not layerexist(code_lay):
        doc.Layers.Add(code_lay)                                      # Add layer if not exist
    #else:
    #print('{} already exist.'.format(layer_code))

    if not layerexist(name_lay):
        doc.Layers.Add(name_lay)
    if not layerexist(point_lay):
        doc.Layers.Add(point_lay)


    pts2ac(csvdt, code_lay, name_lay, point_lay)
    print('Import Field Data Points : Completed.')
    #show_message('Import Field Data Points : Completed.')
    doc.Regen(1)
    acprompt('Import & Draw Points Completed.\n')
