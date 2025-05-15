from multiprocessing import Process
import subprocess
import time
import requests
import uvicorn

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

    # Process(target=arduino_listener).start()
    run_streamlit()
