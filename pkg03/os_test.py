import platform

def get_os_version():
    system_info = platform.system()

    if system_info == 'Windows':
        version_info = platform.version()

        if '10' in version_info:
            return 'Windows 10'
        elif '11' in version_info:
            return 'Windows 11'
        else:
            return 'Windows (version unknown)'

    # Add more conditions for other operating systems if needed
    elif system_info == 'Linux':
        # Handle Linux version detection
        return 'Linux'

    elif system_info == 'Darwin':
        # Handle macOS version detection
        return 'macOS'

    else:
        return 'Unknown operating system'

# Example usage
#os_version = get_os_version()
#print(f"Detected operating system: {os_version}")

import ctypes
import time
import atexit

# Define constants for SetThreadExecutionState
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

def get_execution_state():
    # Call GetThreadExecutionState to retrieve the current execution state
    return ctypes.windll.kernel32.GetThreadExecutionState()
def prevent_sleep():
    # Call SetThreadExecutionState to prevent sleep
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
    ## if need the screen to stay on
    #ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
    #print('*** Disabling Sleep Mode ***')
    print("*** Preventing Windows from going to sleep ***")

def allow_sleep():
    # Call SetThreadExecutionState to allow sleep
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    #ctypes.windll.kernel32.SetThreadExecutionState(0)   # Reset to default state
    #print('*** Enabling Sleep Mode ***')
    print("*** Allowing Windows to go to sleep ***")

@atexit.register
def cleanup():
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    print('*** Windows: NORMAL STATE ***')
# Do Stuff

"""
# Prevent sleep during script execution
prevent_sleep()

# Your script code goes here
for i in range(20):
    print(i)
    time.sleep(1)

# Allow sleep after script execution
allow_sleep()
"""

"""
import ctypes

# Define constants for SetThreadExecutionState and GetThreadExecutionState
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001

def get_execution_state():
    # Call GetThreadExecutionState to retrieve the current execution state
    return ctypes.windll.kernel32.GetThreadExecutionState()

def prevent_sleep():
    # Call SetThreadExecutionState to prevent sleep
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)

def allow_sleep():
    # Call SetThreadExecutionState to allow sleep
    ctypes.windll.kernel32.SetThreadExecutionState(0)  # Reset to default state

# Get and print the current execution state
current_state = get_execution_state()
print(f"Current Execution State: {current_state}")

# Prevent sleep during script execution
prevent_sleep()

# Your script code goes here
for i in range(10):
    print(i)
    time.sleep(1)

# Allow sleep after script execution
allow_sleep()

# Get and print the execution state after allowing sleep
current_state = get_execution_state()
print(f"Current Execution State: {current_state}")
"""