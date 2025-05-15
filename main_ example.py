# This will be later pasted into the arduino manager code;
# The arduino_listener function will be switched with our actual function

from multiprocessing import Process
import subprocess
import time
import requests
import uvicorn

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

    for more infos, inspect the dictionary all_section_values.
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

    for more infos, inspect the dictionary all_section_values
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

# def arduino_listener():
#     while True:
#         # Replace with actual serial logic
#         # Fake touch detection every 5s
#         print("Simulating: Touch detected")
#         requests.post("http://127.0.0.1:8000/set_status/touched")
#         time.sleep(5)
#         print("Simulating: Released")
#         requests.post("http://127.0.0.1:8000/set_status/released")
#         time.sleep(5)

if __name__ == "__main__":
    Process(target=run_api).start()
    time.sleep(1)  # Let API start up

    Process(target=arduino_listener).start()
    run_streamlit()
