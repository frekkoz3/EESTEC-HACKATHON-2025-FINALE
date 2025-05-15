import streamlit as st
import time

# === Support Function ===
def set_session_state(**kwargs):
    for key, value in kwargs.items():
        st.session_state[key] = value
    
# === Landing Page ===
def show_landing_page():
    st.image("touch grass.png", width=400)
    st.title("🌿 Grass Toucher")
    st.markdown("Welcome to the site programmers *rarely* use! Select an action below to proceed.")

    col1, col2 = st.columns(2)
    with col1:
        st.button("Touch Some Grass", on_click = set_session_state, kwargs = {"page": "grass"})
    with col2:
        st.button("Train the Model", on_click = set_session_state, kwargs = {"page": "train_setup"})

# === Train Setup Page ===
def show_train_setup():
    screen = st.empty()
    with screen.container():
        st.title("Training Setup")

        st.markdown("### Select Object to Train With:")
        selected_object = st.selectbox("", ["Balloon", "Wood Stick", "Steel Bar"])
            
        st.markdown("### Select Hardness Level:")
        selected_hardness = st.selectbox("", ["Soft", "Medium", "Hard"])

        # TODO: Store or use selected_object and selected_hardness

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
    screen = st.empty()
    with screen.container():
        st.header("Training is About to Begin")
        st.button("Start Trial", on_click = set_session_state, kwargs = {"train": "closing"})

def train_closing():
    # TODO: Link a function to actially start gripping

    screen = st.empty()
    with screen.container():
        st.header("Training in Progress")
        st.markdown("Gripper is approaching the object...")

        # TODO
        # wait for signal from library
        # while not api.contact_signal():
        #     time.sleep(0.01)

        st.markdown("Object detected.")

        # TODO This might not be needed — confirm with final signals
        # wait for signal from library
        # while not api.now_holding():
        #     time.sleep(0.01)

        st.markdown("Now holding the object")

        st.button("Release", on_click = set_session_state, kwargs = {"train": "release"})

def train_release():
    screen = st.empty()
    with screen.container():
        st.header("Training in Progress")
        st.markdown("Releasing object...")

        # TODO
        # wait for signal from library
        # while not api.released():
        #     time.sleep(0.01)
        
        st.markdown("Object has been released.")
        st.success("Training steps completed!")

        st.button("See Results", on_click = set_session_state, kwargs = {"page": "train_results"})

# === Results Of The Training Phase ===
def show_train_results():
    screen = st.empty()
    with screen.container():
        # TODO
        # show some results

        st.session_state.train = "begin"
        st.button("Home Page", on_click = set_session_state, kwargs = {"page": "landing"})

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
        
        # TODO : wait for contact and print next phrase
        st.markdown("Object encountered, now holding it")

        # TODO : if object is pulled of, enter release mode
        st.markdown("Object is being released...")
        
        # TODO : once arduino ceases activity, print the following:
        st.markdown("Execution ended. Do you want to try again?")
        st.button("Try Again", on_click = set_session_state, kwargs = {"grassing": "ready"})
        st.button("Home Page", on_click = set_session_state, kwargs = {"page": "landing"})

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