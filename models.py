import os 
import pandas as pd
from sklearn.linear_model import LogisticRegression

class DataRetriever:
    """
    This class is used to retrieve data from the data folder.
    """
    def __init__(self, path):
        self.path = path
        self.data = []
        self.objects = [] # These are the labels for classification
        self.types = [] # These are the labels for profiling
        self.load_data()

    def load_data(self):
        """
        This function loads the data from the data folder. It knows how the file name is structured
        """
        for file in os.listdir(self.path):
            if ".csv" not in file:
                continue
            with open(os.path.join(self.path, file), 'r') as f:
                # Assuming the file name is in the format "object_type_timestamp.csv"
                self.objects.append(file.split("_")[0])
                self.types.append(file.split("_")[1])
                self.data.append(pd.read_csv(f, header=None, names=["DMagnitude", "X", "Y", "Z"]))

    def get_data(self):
        return self.data
    
    def get_column(self, column, mode = "all"):
        """
        This function takes a column name as input and returns the data in that column. 
        """
        if column not in ["DMagnitude", "X", "Y", "Z"]:
            raise ValueError("Invalid column name")
        if mode == "all":
            return [d[column] for d in self.data], self.objects, self.types # return all the data for the wanted column plus all the labels
        elif mode == "objs":
            return [d[column] for d in self.data], self.objects # return all the data for the wanted column plus the objects labels
        elif mode == "types":
            return [d[column] for d in self.data], self.types # return all the data for the wanted column plus the types labels
        else:
            return [d[column] for d in self.data] # return all the data for the wanted column

class DetectionModel:
    """
    This class is used to detect if an object is detected or not.
    """
    def __init__(self, path = "models/detecting_model.csv", data_folder = "data/detecting data"):
        self.path = path
        self.upload_model()
        self.data_folder = data_folder
    
    def upload_model(self):
        with open(self.path, 'r') as f:
            self.epsilon = float(f.readline().strip())

    def tune_model(self):
        """
        This function takes all the data from the data folder in order to fine tune the model
        """
        # For now this do nothing since this is not a real model LOL
        return self.epsilon
    
    def save_model(self):
        with open(self.path, 'w') as f:
            f.write(f"{self.epsilon}\n")

    def detect(self, data):
        """
        This function takes a list of data and an epsilon value as input.
        It returns if this data means that an object is detected or not.
        """
        too_small = [x for x in data if abs(x) < self.epsilon]
        if len(too_small) >= 3:
            return "N"
        else:
            return "D"

class ProfilingModel:
    """
    This class is used to classify the profile of the resistance curve. This model is a logistic regression model.
    """
    def __init__(self, path = "models/profiling_model.csv", data_folder = "data/profiling data"):
        self.path = path
        self.upload_model()
        self.data_folder = data_folder
    
    def upload_model(self):
        with open(self.path, 'r') as f:
            line = f.readline().strip()
            self.slope = float(line.split(",")[0])
            self.b = float(line.split(",")[1])
    
    def peak_position(self, data):
        """
        This function takes a list of data and returns the position of the peak in the data.
        """
        # Here we should implement the peak detection algorithm
        # For now we just return the first element:
        data = list(data)
        peak_pos = max(data), data.index(max(data))
        return peak_pos
    
    def tune_model(self):
        """
        This function takes all the data from the data folder in order to fine tune the model
        """
        # This can be done, a bit of trust in the model
        data_retriever = DataRetriever(self.data_folder)
        data, types = data_retriever.get_column("DMagnitude", "types")
        # Here we implement the model training
        # This is a logistic regression model
        x = [self.peak_position(d) for d in data]
        y = [1 if t == 's' else 0 for t in types]
        clf = LogisticRegression()
        clf.fit(x, y)
        w = clf.coef_[0]
        b = clf.intercept_[0]
        slope = -w[0] / w[1]
        intercept = -b / w[1]
        self.slope = slope
        self.b = intercept
        self.save_model()
    
    def save_model(self):
        with open(self.path, 'w') as f:
            line = f"{self.slope},{self.b}\n"
            f.write(line)   

    def predict(self, data):
        """
        This function takes a list of data as input.
        It uses the linear seperator to classify if an object is a "s" (x over the separator) or "h" (x under the separator).
        """
        x = self.peak_position(data) 
        if x[0] > self.slope*x[1] + self.b:
            return "S"
        else:
            return "H"
        
if __name__ == "__main__":
    dr = DataRetriever("data/profiling data")
    data = dr.get_column("DMagnitude", "types")
    model = ProfilingModel()
    model.tune_model()