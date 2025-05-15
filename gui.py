import streamlit as st
import time
import subprocess
import requests
import uvicorn
import json


# secret global variables since there's no time left
selected_object = None
selected_hardness = None

# === Support Functions ===
def set_session_state(**kwargs):
    for key, value in kwargs.items():
        st.session_state[key] = value
    
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
        pass
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
        # print(f"[READ] {variable} =", value)
        return value
    else:
        print(f"[READ ERROR] Failed to read '{variable}' - {response.status_code}")
        return None

def reset_all_variables():
    """
    Sends a POST request to reset all variables in the shared state to "NA".
    """
    endpoint = f"{BASE_URL}/reset"
    response = requests.post(endpoint)
    if response.ok:
        print("[WRITE] All variables reset to 'NA'")
    else:
        print(f"[WRITE ERROR] Failed to reset variables - {response.status_code}")


# === Landing Page ===
def show_landing_page():
    st.image("touch grass.png", width=400)
    st.title("🌿 Grass Toucher")
    st.markdown("Welcome to the site many people don't know about! Select an action below to proceed.")

    col1, col2 = st.columns(2)
    with col1:
        st.button("Touch Some Grass", on_click = set_session_state, kwargs = {"page": "grass"})
    with col2:
        st.button("Train the Model", on_click = set_session_state, kwargs = {"page": "train_setup"})


# ╔══════════════════════════════════════════════════╗
# ║    Section: Pages used in the training process   ║
# ╚══════════════════════════════════════════════════╝

# === Train Setup Page ===
def show_train_setup():
    screen = st.empty()
    with screen.container():
        st.title("Training Setup")

        st.markdown("### Select Object to Train With:")
        selected_object = st.selectbox("", ["Balloon", "Wood Stick", "Steel Bar"], index=0)
            
        st.markdown("### Select Hardness Level:")
        selected_hardness = st.selectbox("", ["Soft", "Medium", "Hard"], index=0)

        st.button("Start Training", on_click = set_session_state, kwargs = {"page": "train_start"})


# === Training Flow ===
def train_router():
    # === Sub-router ===
    if st.session_state.train == "begin":
        train_begin()
    elif st.session_state.train == "closing":
        train_closing()
    elif st.session_state.train == "release":
        train_release()
    else:
        st.error("Invalid training state.")

def train_begin():
    # Send the data collected just earlyer to the server
    write_to_api("data", json.dumps({"obj": selected_object, "type": selected_hardness}))

    screen = st.empty()
    with screen.container():
        st.header("Training is About to Begin")
        st.button("Start Trial", on_click = set_session_state, kwargs = {"train": "closing"})

def train_closing():
    # Send the message to start the procedure
    write_to_api("request", "begin")

    screen = st.empty()
    with screen.container():
        st.header("Training in Progress")
        st.markdown("Gripper is approaching the object...")

        # Wait for contact to happen
        while read_from_api("section") != "detected":
            time.sleep(0.03)

        st.markdown("Object detected.")

        # Wait for holding to be secure
        while read_from_api("section") != "holding":
            time.sleep(0.03)

        st.markdown("Now holding the object")

        st.button("Release", on_click = set_session_state, kwargs = {"train": "release"})

def train_release():
    write_to_api("request", "release")
    screen = st.empty()
    with screen.container():
        st.header("Training in Progress")
        st.markdown("Releasing object...")

        # Wait for release to be completed
        while read_from_api("section") != "still":
            time.sleep(0.03)

        st.markdown("Object has been released.")
        st.success("Training steps completed!")

        st.button("See Results", on_click = set_session_state, kwargs = {"page": "train_results"})

# === Results Of The Training Phase ===
def show_train_results():
    screen = st.empty()
    with screen.container():
        # TODO
        # show some results

        # Reset all variables of the server
        reset_all_variables()
        st.session_state.train = "begin"
        st.button("New Object", on_click = set_session_state, kwargs = {"page": "train_setup"})
        st.button("Home Page", on_click = set_session_state, kwargs = {"page": "landing"})


# ╔═══════════════════════════════════════════════════════╗
# ║    Section: Pages used in the main gripping process   ║
# ╚═══════════════════════════════════════════════════════╝

# === Grass Sub-Router ===
def grass_router():
    if st.session_state.grassing == "ready":
        show_begin_grassing()
    elif st.session_state.grassing == "begun":
        show_grassing_process()
    else:
        st.error("Invalid grassing state.")

# === Begin Touching Grass ===
def show_begin_grassing():
    screen = st.empty()
    with screen.container():
        st.header("Grass touching is about to happen")
        st.button("Begin", on_click = set_session_state, kwargs = {"grassing": "begun"})
        st.button("Home Page", on_click = set_session_state, kwargs = {"page": "landing"})

# === Gripper Closing and Holding ===
def show_grassing_process():
    screen = st.empty()
    with screen.container():
        st.header("Grass touching in process...")
        
        # Wait for contact
        while read_from_api("section") != "detected":
            time.sleep(0.03)
        st.markdown("Object encountered")

        # Wait for holding
        while read_from_api("section") != "holding":
            time.sleep(0.03)
        st.markdown("Object is being held")

        # Check wether objectis are being released
        while read_from_api("section") != "releasing":
            time.sleep(0.03)
        st.markdown("Object is being released")

        # Check wether objectis have been released
        while read_from_api("section") != "still":
            time.sleep(0.03)
        st.markdown("Object has been released")
        
        # Chech for ceased activity
        while read_from_api("section") != "still":
            time.sleep(0.03)
        st.markdown("Execution ended. Here are the results:")
        # TODO : add some information, like plots or classification 

        # Reset all variables of the server
        reset_all_variables()        

        st.button("Try Again", on_click = set_session_state, kwargs = {"grassing": "ready"})
        st.button("Home Page", on_click = set_session_state, kwargs = {"page": "landing"})


# ╔═══════════════════════════════════════════════════════╗
# ║   Section: Actual program that will run when called   ║
# ╚═══════════════════════════════════════════════════════╝

if __name__ == "__main__":
    # === Setup Global Variables ===
    if 'page' not in st.session_state:
        st.session_state.page = "landing"
    if "train" not in st.session_state:
        st.session_state.train = "begin"
    if "grassing" not in st.session_state:
        st.session_state.grassing = "ready"

    # === Page Router ===
    if st.session_state.page == "landing":
        show_landing_page()
    elif st.session_state.page == "train_setup":
        show_train_setup()
    elif st.session_state.page == "train_start":
        train_router()
    elif st.session_state.page == "train_results":
        show_train_results()
    elif st.session_state.page == "grass":
        grass_router()