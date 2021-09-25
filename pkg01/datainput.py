import pandas as pd

# Class of Field data from CSV file
class FieldDataCSV:
    def __init__(self,fname):
        #self.fdir = fdir
        #self.fname = fname
        #self.pathname = fdir + fname
        self.pathname = fname

    def getdata(self, columns, rtkencoding):
        """
        self.restab = pd.read_csv(self.pathname, encoding='ANSI',
                                  usecols=['Code','Name','N','E','Z'])[['Code','Name','E','N','Z']]
        """
        self.restab = pd.read_csv(self.pathname, encoding=rtkencoding,
                                  usecols=columns)[columns]
    def show_data(self):
        print(self.restab.head(100))

# Get data from CSV file
def getCSV(fdir, csvfile, csvcolumns, csvencoding):
    csv = FieldDataCSV(fdir+csvfile)
    csv.getdata(csvcolumns, csvencoding)             # Get data from csv file
    csv.show_data()
    return csv
