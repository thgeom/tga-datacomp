import sys
import io
import time

# Redirect stdout and stderr to the buffer
buffer = io.StringIO()
sys.stdout = sys.stderr = buffer

# Your code that may raise pywintypes.com_error
# ...
for i in range(100000000):

    buffer_size = buffer.tell()
    #buffer_size = sys.stdout.tell()
    print(f"Tile image at i : {i}, buffer_size : {buffer_size}")
    if buffer_size>102400000:
        sys.stdout = sys.__stdout__
        print(f'TIME SLEEP....@ {i}: buffer size: {buffer_size}')
        time.sleep(10)
        # Clear the content of the buffer
        sys.stdout = buffer
        buffer.truncate(0)
        buffer.seek(0)


# Get the current size of the buffer
buffer_size = buffer.tell()

#print(f"Current size of buffer: {buffer_size} characters")

# Reset stdout and stderr to their original values
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
print(f"Current size of buffer: {buffer_size} characters")

import sys

max_string_size = sys.maxsize
print(f"Maximum size of a string: {max_string_size}")

