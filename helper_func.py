import time
import os
from datetime import timedelta

def getExpID():
    current_seconds = time.time()
    return int(current_seconds)



def write2Log(ExpID, content):
    # Specify directory and file name
    directory = "logs"
    filename = f"{ExpID}.txt"

    # Make sure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Full file path
    file_path = os.path.join(directory, filename)

    # Write content to the file
    with open(file_path, "a") as file:
        file.write(f"{content}")

def calcRunTime(stt,edt):
    elapsed_time = edt - stt
    # elapsed_time=elapsed_time/3600
    formatted_time = str(timedelta(seconds=int(elapsed_time)))
    return formatted_time


