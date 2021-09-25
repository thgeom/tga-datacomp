import pandas as pd
import csv
from pkg03.utility import *

class Data4File:
    def __init__(self, fdir, fxls):
        self.fdir = fdir
        self.fxls = fxls
        self.dtxls = []

    # Add each X-section data for 3 formats
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
