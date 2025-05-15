import serial
import csv

class DataProvider:
    def __init__(self, serial_port, baud_rate):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.detecting_data = [] # These are the data collected during the detecting phase
        self.profiling_data = [] # These are the data collected during the profiling phase
        self.holding_data = [] # These are the data collected during the holding phase
        self.checking = False # This is the signal to start processing data
        self.detecting = False # This is the signal to start colleting detection data
        self.profiling = False # This is the signal to start colleting profiling data
        self.holding = False # This is the signal to start holding the object
        self.releasing = False # This is the signal to start releasing the object
        self.ser = serial.Serial(self.serial_port, self.baud_rate)
        print(f"Connesso a {self.serial_port} a {self.baud_rate} baud")

    def read_data(self): # Function to read one line of data from the serial port
        self.checking = False 
        line = self.ser.readline().decode('utf-8').strip()
        if line == "Checking":
            print("Time to compute results from data collected...")
            self.checking = True
        elif line == "Detecting":
            print("Detecting in corso...")
            self.detecting = True
            self.profiling = False
            self.holding = False
            self.releasing = False
            self.detecting_data = [  ]
        elif line == "Profiling":
            print("Profiling in corso...")
            self.detecting = False
            self.profiling = True
            self.holding = False
            self.releasing = False
            self.profiling_data = []
        elif line == "Holding":
            print("Holding...")
            self.detecting = False
            self.profiling = False
            self.holding = True
            self.releasing = False
        elif line == "Releasing":
            print("Releasing...")
            self.detecting = False
            self.profiling = False
            self.holding = False
            self.releasing = True
        elif self.detecting:
            if line:
                self.detecting_data.append(line.strip().split(','))
        elif self.profiling:
            if line:
                self.profiling_data.append(line.strip().split(','))  
        elif self.holding:
            if line:
                self.holding_data.append(line.strip().split(','))
        else:
            pass
        return self.checking , self.detecting, self.profiling, self.holding, self.releasing, line
    
    def write_data(self, data):
        mex = f"{data}\n"
        self.ser.write(mex.encode('utf-8'))
        print(f"Data sent: {mex.encode('utf-8')}")

    def write_to_csv(self, data, file):
        self.output_file = file
        data = data
        with open(self.output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for entry in self.buffer:
                writer.writerow(entry.split(','))

if __name__ == "__main__":

    SERIAL_PORT = "COM7"
    BAUD_RATE = 115200

    OUTPUT_FILE = f"online_data.csv"

    prov = DataProvider(1, 2)
    while True:
        if True:
            file_path = "dati oggetto n"
            prov.write_data(prov.profiling_data, file_path)