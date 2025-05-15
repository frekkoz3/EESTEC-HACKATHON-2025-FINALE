import serial
import csv
from collections import deque
import online_data_provider
from models import *

data_provider = online_data_provider.DataProvider("COM7", 115200, "online_data.csv")
detecting_data = []
profiling_data = []

def split_data(data):
    """
    This function takes a comma-separated string and splits it into a list of floats.
    """
    return [float(d) for d in data]

while True:
    checking, detecting, profiling, line = data_provider.read_data()
    print(line)
    if checking and detecting:
        detecting_data = [split_data(d) for d in data_provider.detecting_data]
        needed_data = [d[0] for d in detecting_data]
        response = detection_data(needed_data) # Here should be the algorithm that decides the response
        data_provider.write_data(response)
    elif checking and profiling:
        profiling_data = [split_data(d) for d in data_provider.profiling_data]
        response = "H" # Here should be the algorithm that decides the response
        data_provider.write_data(response)
    else:
        pass