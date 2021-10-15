import pandas as pd
import csv
from pkg02.cadlib import *
from pkg03.utility import *

# Prepare data for Excel file output
class Data4File:
    def __init__(self, fdir, fxls):
        self.fdir = fdir
        self.fxls = fxls
        self.dtxls = []

    # Add each point in the selection set to data list
    def dtAdd(self, slset):
        for i in slset:
            lst = list(i.InsertionPoint)
            lst.insert(0, i.TextString)
            self.dtxls.append(lst)

    def show_data(self):
        print(self.dtxls)


    # Writing data to Excel file using Pandas Data Frame
    def dt2File(self, dtenconding):
        dfxls = pd.DataFrame(self.dtxls, columns=['Code', 'East', 'North', 'Elevation']) # DataFrame to Excel
        xlsname = self.fdir + self.fxls
        print(dfxls)
        #writer = pd.ExcelWriter(xlsname, mode='w')
        try:
            writer = pd.ExcelWriter(xlsname, mode='w')
        except:
            msg = 'Excel File : {} : currently in use!!!'.format(xlsname)
            msg += '\nPlease close it, then process again.'
            warn_message(msg)
            return False
        dfxls.to_excel(writer, sheet_name='Coordinate_List')
        writer.save()
        msg = '>>>> Excel File : {} :\n'.format(xlsname)
        msg += 'has been created.'
        show_message(msg)

# Prepare data for Txt output
class Data4Txt:
    def __init__(self, fdir, ftxt):
        self.fdir = fdir
        self.ftxt = ftxt
        self.dttxt = []

    # Add each polyline in the selection set to data list
    def dtAdd(self, slset):
        lst = []
        for i in slset:
            plpts = list(polyvertex(i))
            pnts = []
            nopts = len(plpts) // 2
            for j in range(nopts):
                x = plpts[j * 2]
                y = plpts[j * 2 + 1]
                z = i.Elevation
                pnts.append((x, y, z))
            lst = pnts
            lst.insert(0, i.Length)
            lst.insert(0, i.Area)
            self.dttxt.append(lst)

    def show_data(self):
        for pl in self.dttxt:
            parea = pl[0]
            pperim = pl[1]
            print('Area : {:0.4f}'.format(parea))
            print('Perimeter : {:0.4f}'.format(pperim))
            for pt in pl[2:]:
                print(pt)

    # Write data to Text file
    def dt2TxtFile(self):
        txtfile = self.fdir + self.ftxt
        f1 = open(txtfile, "a")
        for pl in self.dttxt:
            parea = pl[0]
            pperim = pl[1]
            f1.write('Area : {:0.4f}\n'.format(parea))
            f1.write('Perimeter : {:0.4f}\n'.format(pperim))
            f1.write('No.       ' + 'East              ' + 'North            ' + 'Elevation\n')
            i = 1
            for pt in pl[2:]:
                f1.write('{0:d}    {1:12.4f}     {2:12.4f}      {3:6.3f}\n'.format(i, pt[0], pt[1],pt[2]))
                i += 1
            f1.write('#\n')
        f1.close()
        msg = '>>>> Txt File : {} :\n'.format(txtfile)
        msg += 'has been created.'
        show_message(msg)

