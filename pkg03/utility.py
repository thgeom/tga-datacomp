import ast
import math
from tkinter import *
from tkinter import messagebox

# Define root window
def set_root_window():
    #global top, sta_label, child_window
    root = Tk()
    root.title('Main window!')
    root.geometry('200x100')
    root.geometry('+200+300')

    #top.lower()
    #child_window = Toplevel(top)
    #child_window.geometry('400x100')
    #child_window.geometry('+200+300')
    #child_window.title("Status Window")
    return root


# Get Project Parameters from .par file
def getProjParams(fdir, inpfile):
    fctr = open(fdir + inpfile, "r", encoding='UTF-8')
    try:
        contents = fctr.read()
        fctr.close()
    except:
        contents = {}
    try:
        proj_dict = ast.literal_eval(contents)
    except:
        proj_dict = {}
    return proj_dict

# Status message
def statusbox(label_id, msg, y=1.0):
    print(msg)
    label_id.configure(text=': '+msg, width=40, fg='#65B017')
    #label_id.pack()
    label_id.place(relx=-0.01, rely=y, anchor=SW)
    label_id.master.update()

# Status message2
def statusbox2(msg, y=0.5):
    win = Tk()
    win.geometry('300x150')
    win.geometry('+100+400')                 # Position ('+Left+Top')
    win.title('Info')

    label2 = Label(win, text=': ', width=40)
    label2.configure(text=': '+msg, width=40)
    label2.place(relx=0.5, rely=y, anchor=CENTER)
    win.mainloop()

# Function echo message
def show_message(msg, batch=False):
    print(msg)
    if not batch:
        messagebox.showinfo('Information', msg)

# Function warning message
def warn_message(msg, batch=False):
    if batch:
        print(msg)
        sys.exit(1)
    else:
        print(msg)
        messagebox.showwarning('Warning', msg)


# To compare first element
def cmp(a, b):
    return lambda a, b: a[0] < b[0]

# Sorting list of XYZ by X element
def sort_x(lis):
    lis2 = sorted({tuple(x): x for x in lis}.values())
    return lis2

# Sorting list of points by specified element
def sort_rtk_x(lis):
    return sorted(lis, key=lambda e: e[1])
    #return lis2
