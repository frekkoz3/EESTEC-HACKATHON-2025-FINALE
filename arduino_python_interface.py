import serial
import csv
from collections import deque
import online_data_provider
from models import *

def split_data(data):
    """
    This function takes a comma-separated string and splits it into a list of floats.
    """
    return [float(d) for d in data]

def inference_interface(data_provider):
    detecting_data = []
    profiling_data = []
    while True:
        checking, detecting, profiling, holding, releasing, line = data_provider.read_data()
        print(line)
        if checking and detecting:
            detecting_data = [split_data(d) for d in data_provider.detecting_data]
            needed_data = [d[0] for d in detecting_data]
            response = detection_data(needed_data) # This is the algorithm that decide if it is noise signal or actually detected
            data_provider.write_data(response)
        elif checking and profiling:
            profiling_data = [split_data(d) for d in data_provider.profiling_data]
            response = "H" # Here should be the algorithm that decides the response
            data_provider.write_data(response)
        else:
            pass

def train_interfsce():
    pass

if __name__ == "__main__":
    data_provider = online_data_provider.DataProvider("COM7", 115200)
    inference_interface(data_provider)
