def detection_data(data, epsilon = 0.2):
    """
    This function takes a list of data and an epsilon value as input.
    It returns if this data means that an object is detected or not.
    """
    too_small = [x for x in data if abs(x) < epsilon]
    if len(too_small) >= 3:
        return "N"
    else:
        return "D"
    
def profiling_curve(data)
