import streamlit as st
import serial
import serial.tools.list_ports
import time

st.markdown(
    """
    <style>
    body {
        background-color: "#ffffff";
    }
    </style>
    """,
    unsafe_allow_html=True
)

# === Page State ===
if 'page' not in st.session_state:
    st.session_state.page = "landing"
if 'ser' not in st.session_state:
    st.session_state.ser = None
if 'serial_output' not in st.session_state:
    st.session_state.serial_output = ""

# === Landing Page ===
def show_landing_page():
    st.image("touch grass.png", width=400)  # Replace with your image file
    st.title("Smart Gripper Interface")
    st.write("Welcome! Control and monitor your gripper from here.")

    if st.button("Touch grass"):
        st.session_state.page = "main"

# === Main Interface Page ===
def show_main_page():
    st.title("Smart Gripper Monitor")

    ports = list(serial.tools.list_ports.comports())
    port_options = [f"{port.device} - {port.description}" for port in ports]
    selected_port = st.selectbox("Select COM Port", port_options)

    if selected_port:
        port_device = selected_port.split(" - ")[0]

    if st.button("Connect"):
        try:
            st.session_state.ser = serial.Serial(port_device, 115200, timeout=1)
            time.sleep(2)
            st.success(f"Connected to {port_device}")
        except Exception as e:
            st.error(f"Failed to connect: {e}")

    if st.session_state.ser and st.session_state.ser.is_open:
        col1, col2 = st.columns(2)
        if col1.button("Train"):
            st.session_state.ser.write(b'open\n')S
        if col2.button("Touch grass"):
            st.session_state.ser.write(b'close\n')

        if st.button("Read Serial"):
            try:
                lines = []
                while st.session_state.ser.in_waiting:
                    line = st.session_state.ser.readline().decode('utf-8').strip()
                    lines.append(line)
                if lines:
                    st.session_state.serial_output += "\n".join(lines) + "\n"
            except Exception as e:
                st.session_state.serial_output += f"[Error] {e}\n"

        st.text_area("Serial Output", st.session_state.serial_output, height=300)

        if st.button("Quit"):
            if st.session_state.ser and st.session_state.ser.is_open:
                st.session_state.ser.close()
            st.success("Session ended.")
            st.session_state.page = "landing"
            st.stop()

# === Router ===
if st.session_state.page == "landing":
    show_landing_page()
else:
    show_main_page()
