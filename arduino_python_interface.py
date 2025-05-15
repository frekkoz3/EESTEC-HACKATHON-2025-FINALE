import serial
import csv
import online_data_provider
from models import *

from multiprocessing import Process
import subprocess
import time
import requests
import uvicorn
import json

def split_data(data):
    """
    This function takes a comma-separated string and splits it into a list of floats.
    """
    return [float(d) for d in data]

def inference_interface(data_provider):
    detecting_data = []
    profiling_data = []
    # time stamp da computare qui 
    detect_model = DetectionModel()
    profile_model = ProfilingModel()
    collecting = read_from_api("mode") == "train"
    names = read_from_api("data")
    time = time.time()
    if names != "NA":
        names = json.loads(names)
        object = names["obj"]
        type = names["type"]
    while True:
        # leggere la pipeline e salvarsi localmente i dati della pipeline
        # start, release, object, type = pipeline
        #
        checking, detecting, profiling, holding, releasing, line = data_provider.read_data()
        print(line)
        if checking and detecting:
            write_to_api("section", "detected")
            detecting_data = [split_data(d) for d in data_provider.detecting_data] # this is a matrix in the form DMagnitude, X, Y, Z 
            if collecting:
                # Here we should collect the data and save it to a file
                data_provider.write_to_csv(detecting_data, f"./data/detecting/{object}_{type}_{time}.csv")
            needed_data = [d[0] for d in detecting_data]
            response = detect_model.detect(needed_data) # This is the algorithm that decide if it is noise signal or actually detected
            data_provider.write_data(response)
        elif checking and profiling:
            write_to_api("section", "holding")
            profiling_data = [float(split_data(d)[0]) for d in data_provider.profiling_data] # this is a list in the form DMAgnitude
            print(profiling_data)
            if collecting:
                # Here we should collect the data and save it to a file
                data_provider.write_to_csv(profiling_data, f"./data/profiling/B.csv")
            response = profile_model.predict(profiling_data) # Here should be the algorithm that decides the response
            data_provider.write_data(response)
        elif releasing:
            write_to_api("section", "releasing")
            # Here we should collect the data and save it to a file
            data_provider.write_to_csv(profiling_data, f"./data/profiling/A.csv")
            response = profile_model.predict(profiling_data)
            if line == "Restarting\n":
                write_to_api("section", "still")
        else:
            pass

# === Outline of all possible variables one can access or edit and their possible values ===
#     "mode": "NA", "grab", "train"
#     "section": "NA", "still", "detect", "hold", "release" 
#     "request": "NA"
#     "data": many things, like images or strings, handled case by case


BASE_URL = "http://127.0.0.1:8000"

def write_to_api(variable: str, value: str):
    """
    Sends a POST request to set a specific variable in the shared state.

    Args:
        variable (str): The name of the variable to set.
        value (str): The value to assign to the variable.
    """
    endpoint = f"{BASE_URL}/{variable}/{value}"
    response = requests.post(endpoint)
    if response.ok:
        print(f"[WRITE] Set '{variable}' to '{value}'")
    else:
        print(f"[WRITE ERROR] Failed to set '{variable}' to '{value}' - {response.status_code}")

def read_from_api(variable: str):
    """
    Sends a GET request to retrieve the value of a specific variable from the shared state.

    Args:
        variable (str): The name of the variable to set.
    """
    response = requests.get(f"{BASE_URL}/{variable}")
    if response.ok:
        value = response.json().get(variable)
        print(f"[READ] {variable} =", value)
        return value
    else:
        print(f"[READ ERROR] Failed to read '{variable}' - {response.status_code}")
        return None


def run_api():
    uvicorn.run("api_server:app", host="127.0.0.1", port=8000, log_level="warning")

def run_streamlit():
    subprocess.Popen(["streamlit", "run", "gui.py"], shell=True)

if __name__ == "__main__":

    Process(target=run_api).start()
    time.sleep(1)  # Let API start up

    data_provider = online_data_provider.DataProvider("COM6", 115200)

    Process(target=inference_interface(data_provider)).start()
    run_streamlit()