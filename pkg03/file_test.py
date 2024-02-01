import os
import datetime

def get_last_modified_date(file_path):
    try:
        # Get the last modified timestamp of the file
        timestamp = os.path.getmtime(file_path)

        # Convert the timestamp to a human-readable date and time
        last_modified_date = datetime.datetime.fromtimestamp(timestamp)

        return last_modified_date
    except FileNotFoundError:
        return None

# Example usage:
url_reg_dir = "d:/TGA_TEST/datacomp/"
url_req_file = "url_req_params.parx"
#url_req_file = "PParams-4.par"
file_path = url_reg_dir + url_req_file
last_modified_date = get_last_modified_date(file_path)

if last_modified_date:
    print(f'The last modified date of {file_path} is: {last_modified_date}')
else:
    print(f'File {file_path} not found.')


if last_modified_date:
    current_datetime = datetime.datetime.now()

    if last_modified_date > current_datetime:
        print(f'The file {file_path} was modified after the current date and time.')
    elif last_modified_date < current_datetime:
        print(f'The file {file_path} was modified before the current date and time.')
    else:
        print(f'The file {file_path} was modified at the same date and time as now.')
else:
    print(f'File {file_path} not found.')


if last_modified_date:
    current_datetime = datetime.datetime.now()
    time_difference = current_datetime - last_modified_date

    # Get the number of days
    days_difference = time_difference.days

    print(f'The file {file_path} was last modified {days_difference} days ago.')
else:
    print(f'File {file_path} not found.')



if last_modified_date:
    current_datetime = datetime.datetime.now()
    time_difference = current_datetime - last_modified_date

    # Get the total number of minutes
    minutes_difference = time_difference.total_seconds() / 60

    print(f'The file {file_path} was last modified {minutes_difference:.2f} minutes ago.')
else:
    print(f'File {file_path} not found.')


"""
## Test io.StringIO()
import sys, io
### To solve pywintypes.com_error in Windows 11
buffer = io.StringIO()
print(f"1 buffer.__sizeof__: {buffer.__sizeof__()}")
sys.stdout = sys.stderr = buffer
#sys.stderr = buffer
print(f"buffer.__dir__: {buffer.__dir__()}")

print('1234567890abcdefghijklmnopqrstuvwxyz')
#print(f"buffer.__sizeof__: {buffer.__sizeof__()}")
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
print(f"2 buffer.__sizeof__: {buffer.__sizeof__()}")
print(f"buffer.getvalue: {buffer.getvalue()[:20000]}")
print(sys.stderr)
"""

