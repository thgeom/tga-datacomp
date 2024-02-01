#import tkinter as tk

"""
def change_font_size():
    new_size = font_size_var.get()
    label.config(font=("Arial", new_size))

root = tk.Tk()

default_font_size = 12

label = tk.Label(root, text="Hello, Tkinter!", font=("Arial", default_font_size))
label.pack()

# Entry widget to enter the new font size
font_size_var = tk.StringVar()
font_size_entry = tk.Entry(root, textvariable=font_size_var)
font_size_entry.pack()

# Button to change the font size dynamically
change_font_button = tk.Button(root, text="Change Font Size", command=change_font_size)
change_font_button.pack()

root.mainloop()
"""

"""
def on_select(event):
    # Function to be called when an item is selected in the listbox
    selected_item = listbox.get(listbox.curselection())
    print(f"Selected item: {selected_item}")

# Create the main Tkinter window
root = tk.Tk()
root.title("Listbox Example")

# List of items for the listbox
listbox_items = ["Item 1", "Item 2", "Item 3", "Item 4"]

# Create the Listbox widget
listbox = tk.Listbox(root, selectmode=tk.SINGLE)
for item in listbox_items:
    listbox.insert(tk.END, item)

# Bind the on_select function to the listbox selection event
listbox.bind("<<ListboxSelect>>", on_select)

listbox.pack(padx=20, pady=20)

# Run the Tkinter event loop
root.mainloop()
"""

"""
from tkinter import ttk
import geopandas as gpd

# Create a GeoDataFrame (replace this with your actual GeoDataFrame)
# For demonstration purposes, we'll create a simple GeoDataFrame with Point geometries.
data = {'Name': ['Point 1', 'Point 2', 'Point 3'],
        'Latitude': [40.7128, 34.0522, 41.8781],
        'Longitude': [-74.0060, -118.2437, -87.6298]}

geometry = gpd.points_from_xy(data['Longitude'], data['Latitude'])
gdf = gpd.GeoDataFrame(data, geometry=geometry)

def on_dropdown_change(*args):
    # Function to be called when the dropdown selection changes
    selected_column = dropdown_var.get()
    print(f"Selected column: {selected_column}")
    return selected_column

def on_ok_button_click():
    # Function to be called when the OK button is clicked
    selected_column = on_dropdown_change()
    print(f"Selected column from OK button: {selected_column}")
    # Add your additional actions here

    # Close the Tkinter window
    root.destroy()

# Create the main Tkinter window
root = tk.Tk()
root.title("Select Column Example")

# Create a StringVar to store the selected column
dropdown_var = tk.StringVar(root)

# List of column names from the GeoDataFrame
column_names = list(gdf.columns)

# Set the default value for the dropdown
dropdown_var.set(column_names[0])

# Create the OptionMenu widget
dropdown_menu = ttk.Combobox(root, textvariable=dropdown_var, values=column_names)
dropdown_menu.bind("<<ComboboxSelected>>", on_dropdown_change)
dropdown_menu.pack(padx=40, pady=20)

# Create the OK button
ok_button = tk.Button(root, text="OK", command=on_ok_button_click)
ok_button.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()

#selected_column = on_dropdown_change()
#print(f"Returned column: {selected_column}")
"""

"""
from tkinter import ttk
import geopandas as gpd

# Create a GeoDataFrame (replace this with your actual GeoDataFrame)
data = {'Name': ['Point 1', 'Point 2', 'Point 3'],
        'Latitude': [40.7128, 34.0522, 41.8781],
        'Longitude': [-74.0060, -118.2437, -87.6298]}

geometry = gpd.points_from_xy(data['Longitude'], data['Latitude'])
gdf = gpd.GeoDataFrame(data, geometry=geometry)


def on_dropdown_change(*args):
    # Function to be called when the dropdown selection changes
    selected_column_var.set(dropdown_var.get())


def on_ok_button_click():
    # Function to be called when the OK button is clicked
    selected_column = selected_column_var.get()
    print(f"Selected column from OK button: {selected_column}")

    # Add your additional actions here

    # Close the Tkinter window
    root.destroy()


# Create the main Tkinter window
root = tk.Tk()
root.title("Select Column Example")

# Create a StringVar to store the selected column
selected_column_var = tk.StringVar(root)

# Create a StringVar to store the selected column from the dropdown
dropdown_var = tk.StringVar(root)

# List of column names from the GeoDataFrame
column_names = list(gdf.columns)

# Set the default value for the dropdown
dropdown_var.set(column_names[0])

# Create the OptionMenu widget
dropdown_menu = ttk.Combobox(root, textvariable=dropdown_var, values=column_names)
dropdown_menu.bind("<<ComboboxSelected>>", on_dropdown_change)
dropdown_menu.pack(padx=20, pady=20)

# Create the OK button
ok_button = tk.Button(root, text="OK", command=on_ok_button_click)
ok_button.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()

# After the window is destroyed, you can access the selected_column_var value
returned_value = selected_column_var.get()
print(f"Returned value: {returned_value}")
"""
"""
import tkinter as tk
from tkinter import ttk

def create_dropdown_window(column_names, callback):
    def on_dropdown_change(*args):
        selected_column_var.set(dropdown_var.get())

    def on_ok_button_click():
        selected_column = selected_column_var.get()
        print(f"Selected column from OK button: {selected_column}")

        # Call the callback function with the selected column
        callback(selected_column)

        # Close the Tkinter window
        dropdown_window.destroy()

    # Create the Toplevel window
    dropdown_window = tk.Toplevel()
    dropdown_window.title("Select Column Example")

    # Create a StringVar to store the selected column
    selected_column_var = tk.StringVar(dropdown_window)

    # Create a StringVar to store the selected column from the dropdown
    dropdown_var = tk.StringVar(dropdown_window)

    # Set the default value for the dropdown
    dropdown_var.set(column_names[0])

    # Create the OptionMenu widget
    dropdown_menu = ttk.Combobox(dropdown_window, textvariable=dropdown_var, values=column_names)
    dropdown_menu.bind("<<ComboboxSelected>>", on_dropdown_change)
    dropdown_menu.pack(padx=20, pady=20)

    # Create the OK button
    ok_button = tk.Button(dropdown_window, text="OK", command=on_ok_button_click)
    ok_button.pack(pady=10)

# Example of using the create_dropdown_window function
def main_function():
    # Your main function logic here

    # List of column names from the GeoDataFrame
    column_names = ["Name", "Latitude", "Longitude"]

    # Callback function to handle the selected column
    def callback(selected_column):
        print(f"Callback function received selected column: {selected_column}")

    # Call the function to create and display the dropdown window
    create_dropdown_window(column_names, callback)

# Create the main Tkinter window
root = tk.Tk()
root.title("Main Window")

# Create a button to trigger the dropdown window
button = tk.Button(root, text="Open Dropdown", command=main_function)
button.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
"""
"""
import tkinter as tk
from tkinter import ttk

def create_dropdown_window(column_names, shared_var, callback):
    def on_dropdown_change(*args):
        shared_var.set(dropdown_var.get())

    def on_ok_button_click():
        callback()
        # Close the Tkinter window
        dropdown_window.destroy()

    # Create the Toplevel window
    dropdown_window = tk.Toplevel()
    dropdown_window.title("Select Column Example")

    # Create a StringVar to store the selected column from the dropdown
    dropdown_var = tk.StringVar(dropdown_window)

    # Set the default value for the dropdown
    dropdown_var.set(column_names[0])

    # Create the OptionMenu widget
    dropdown_menu = ttk.Combobox(dropdown_window, textvariable=dropdown_var, values=column_names)
    dropdown_menu.bind("<<ComboboxSelected>>", on_dropdown_change)
    dropdown_menu.pack(padx=20, pady=20)

    # Create the OK button
    ok_button = tk.Button(dropdown_window, text="OK", command=on_ok_button_click)
    ok_button.pack(pady=10)

# Example of using the create_dropdown_window function
def main_function():
    # Your main function logic here

    # List of column names from the GeoDataFrame
    column_names = ["Name", "Latitude", "Longitude"]

    # Create a StringVar to store the selected column
    selected_column_var = tk.StringVar()

    # Callback function to handle the selected column
    def callback():
        selected_column = selected_column_var.get()
        print(f"Callback function received selected column: {selected_column}")
        # Use 'selected_column' in 'main_function'

    # Call the function to create and display the dropdown window
    create_dropdown_window(column_names, selected_column_var, callback)

# Create the main Tkinter window
root = tk.Tk()
root.title("Main Window")

# Create a button to trigger the dropdown window
button = tk.Button(root, text="Open Dropdown", command=main_function)
button.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
"""
"""
import tkinter as tk
from tkinter import ttk

def create_dropdown_window(column_names, shared_var, callback):
    def on_dropdown_change(*args):
        shared_var[0] = dropdown_var.get()

    def on_ok_button_click():
        callback(shared_var[0])
        # Close the Tkinter window
        dropdown_window.destroy()

    # Create the Toplevel window
    dropdown_window = tk.Toplevel()
    dropdown_window.title("Select Column Example")

    # Create a StringVar to store the selected column from the dropdown
    dropdown_var = tk.StringVar(dropdown_window)

    # Set the default value for the dropdown
    dropdown_var.set(column_names[0])

    # Create the OptionMenu widget
    dropdown_menu = ttk.Combobox(dropdown_window, textvariable=dropdown_var, values=column_names)
    dropdown_menu.bind("<<ComboboxSelected>>", on_dropdown_change)
    dropdown_menu.pack(padx=20, pady=20)

    # Create the OK button
    ok_button = tk.Button(dropdown_window, text="OK", command=on_ok_button_click)
    ok_button.pack(pady=10)

# Example of using the create_dropdown_window function
def main_function():
    # Your main function logic here

    # List of column names from the GeoDataFrame
    column_names = ["Name", "Latitude", "Longitude"]

    # Create a list to store the selected column
    selected_column = [None]

    # Callback function to handle the selected column
    def callback(selected_column_value):
        selected_column[0] = selected_column_value
        print(f"Callback function received selected column: {selected_column[0]}")
        # Use 'selected_column[0]' in 'main_function'

    # Create a list to store the selected column
    selected_column_var = [tk.StringVar()]

    # Call the function to create and display the dropdown window
    dropdown_window = create_dropdown_window(column_names, selected_column_var, callback)

    # Wait for the dropdown window to be destroyed
    dropdown_window.wait_window()

    # Access the selected_column after the Tkinter window is destroyed
    print(f"Selected column in main_function: {selected_column[0]}")

# Create the main Tkinter window
root = tk.Tk()
root.title("Main Window")

# Create a button to trigger the dropdown window
button = tk.Button(root, text="Open Dropdown", command=main_function)
button.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
"""
"""
import tkinter as tk
from tkinter import ttk

def create_dropdown_window(column_names, shared_var, callback):
    def on_dropdown_change(*args):
        shared_var.set(dropdown_var.get())

    def on_ok_button_click():
        callback(shared_var.get())
        # Close the Tkinter window
        dropdown_window.destroy()

    # Create the Toplevel window
    dropdown_window = tk.Toplevel()
    dropdown_window.title("Select Column Example")

    # Create a StringVar to store the selected column from the dropdown
    dropdown_var = tk.StringVar(dropdown_window)

    # Set the default value for the dropdown
    dropdown_var.set(column_names[0])

    # Create the OptionMenu widget
    dropdown_menu = ttk.Combobox(dropdown_window, textvariable=dropdown_var, values=column_names)
    dropdown_menu.bind("<<ComboboxSelected>>", on_dropdown_change)
    dropdown_menu.pack(padx=20, pady=20)

    # Create the OK button
    ok_button = tk.Button(dropdown_window, text="OK", command=on_ok_button_click)
    ok_button.pack(pady=10)

    # Wait for the StringVar to be set
    dropdown_window.wait_variable(shared_var)

# Example of using the create_dropdown_window function
def main_function():
    # Your main function logic here

    # List of column names from the GeoDataFrame
    column_names = ["Name", "Latitude", "Longitude"]

    # Create a StringVar to store the selected column
    selected_column_var = tk.StringVar()

    # Callback function to handle the selected column
    def callback(selected_column_value):
        print(f"Callback function received selected column: {selected_column_value}")
        # Use 'selected_column_value' in 'main_function'

    # Call the function to create and display the dropdown window
    create_dropdown_window(column_names, selected_column_var, callback)

    # Wait for the StringVar to be set
    selected_column_var.get()
    print(f"Selected column in main_function: {selected_column_var.get()}")

# Create the main Tkinter window
root = tk.Tk()
root.title("Main Window")

# Create a button to trigger the dropdown window
button = tk.Button(root, text="Open Dropdown", command=main_function)
button.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
"""

import tkinter as tk
from tkinter import ttk

def create_dropdown_window(column_names, shared_var, real_number_var, callback):
    def on_dropdown_change(*args):
        shared_var.set(dropdown_var.get())

    def on_ok_button_click():
        callback(shared_var.get(),real_number_var.get())
        # Close the Tkinter window
        dropdown_window.destroy()

    # Create the Toplevel window
    dropdown_window = tk.Toplevel()
    dropdown_window.geometry('500x150')
    dropdown_window.title("Select Column Example")

    # Label before the dropdown
    label = tk.Label(dropdown_window, text="Select a label:", width=25)
    label.grid(column=0, row=5,  padx=5,  pady=5)
    #label.pack(padx=10, pady=5)

    # Create a StringVar to store the selected column from the dropdown
    dropdown_var = tk.StringVar(dropdown_window)

    # Set the default value for the dropdown (first column)
    dropdown_var.set(column_names[0])

    # Create the OptionMenu widget
    dropdown_menu = ttk.Combobox(dropdown_window, textvariable=dropdown_var, values=column_names)
    dropdown_menu.grid(column=1, row=5,  padx=5,  pady=5)
    dropdown_menu.bind("<<ComboboxSelected>>", on_dropdown_change)
    #dropdown_menu.pack(padx=80, pady=10)

    label = tk.Label(dropdown_window, text="Font size:", width=25)
    label.grid(column=0, row=9,  padx=5,  pady=5)

    # text box entry
    #ttk.Label(dropdown_window, text="Enter a name:").grid(column=0, row=0)
    #fontsize = tk.StringVar()
    #real_number_var = tk.DoubleVar()
    enter_real_number = ttk.Entry(dropdown_window, width=12, textvariable=real_number_var)
    enter_real_number.grid(column=1, row=9,  padx=5,  pady=5, sticky=tk.W)

    # Create the OK button
    ok_button = tk.Button(dropdown_window, text="OK", command=on_ok_button_click)
    ok_button.grid(column=1, row=13,  padx=5,  pady=15, sticky=tk.W)
    #ok_button.pack(pady=10)

    # Return the Toplevel window
    return dropdown_window

# Example of using the create_dropdown_window function
def main_function():
    # Your main function logic here

    # List of column names from the GeoDataFrame
    column_names = ["Name", "Latitude", "Longitude"]

    # Create a StringVar to store the selected column with the default value (first column)
    selected_column_var = tk.StringVar(value=column_names[0])
    fontsize_var = tk.DoubleVar(value=2.5)

    # Callback function to handle the selected column
    def callback(selected_column_value, fontsize_var):
        print(f"Callback function received selected column: {selected_column_value}")
        print(f"Callback function received real number: {fontsize_var}")
        # Use 'selected_column_value' in 'main_function'

    # Call the function to create and display the dropdown window
    dropdown_window = create_dropdown_window(column_names, selected_column_var, fontsize_var, callback)

    # Wait for the dropdown window to be destroyed
    dropdown_window.wait_window(dropdown_window)

    # Access the selected_column after the Tkinter window is destroyed
    print(f"Selected column in main_function: {selected_column_var.get()}")
    # Access the font size after the Tkinter window is destroyed
    print(f"Font size in main_function: {fontsize_var.get()}")

# Create the main Tkinter window
root = tk.Tk()
root.title("Main Window")

# Create a button to trigger the dropdown window
button = tk.Button(root, text="Open Dropdown", command=main_function)
button.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()
