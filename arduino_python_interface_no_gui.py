import serial
import csv
import online_data_provider
from models import *

def split_data(data):
    """
    This function takes a comma-separated string and splits it into a list of floats.
    """
    return [float(d) for d in data]

def inference_interface(data_provider, collecting=False):
    detecting_data = []
    profiling_data = []
    # time stamp da computare qui 
    detect_model = DetectionModel()
    profile_model = ProfilingModel()
    while True:
        # leggere la pipeline e salvarsi localmente i dati della pipeline
        # start, release, object, type = pipeline
        #
        checking, detecting, profiling, holding, releasing, line = data_provider.read_data()
        print(line)
        if checking and detecting:
            detecting_data = [split_data(d) for d in data_provider.detecting_data] # this is a matrix in the form DMagnitude, X, Y, Z 
            if collecting:
                # Here we should collect the data and save it to a file
                data_provider.write_to_csv(detecting_data, f"./data/detecting/A.csv")
            needed_data = [d[0] for d in detecting_data]
            response = detect_model.detect(needed_data) # This is the algorithm that decide if it is noise signal or actually detected
            data_provider.write_data(response)
        elif checking and profiling:
            profiling_data = [float(split_data(d)[0]) for d in data_provider.profiling_data] # this is a list in the form DMAgnitude
            if collecting:
                # Here we should collect the data and save it to a file
                data_provider.write_to_csv(profiling_data, f"./data/profiling/B.csv")
            response = profile_model.predict(profiling_data) # Here should be the algorithm that decides the response
            data_provider.write_data(response)
        else:
            pass



if __name__ == "__main__":

    data_provider = online_data_provider.DataProvider("COM6", 115200)
    inference_interface(data_provider)