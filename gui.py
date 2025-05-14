import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import time

# === Select COM Port ===
ports = list(serial.tools.list_ports.comports())
for i, port in enumerate(ports):
    print(f"{i}: {port.device} - {port.description}")

index = int(input("Select port index: "))
PORT = ports[index].device
BAUD = 115200
ser = serial.Serial(PORT, BAUD, timeout=1)
a = serial.serial
# === Initialize Serial Communication ===
def init_serial():
    time.sleep(3)  # Give Arduino time to reset after connection

# === Flag ===
running = True  # Used to stop the thread on exit

# === Read Data from Arduino ===
def read_serial():
    while running and ser.is_open:
        try:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                output.insert(tk.END, f"[Arduino] {line}\n")
                output.see(tk.END)
                # qua interpreto il messaggio e chiamo la funzione corrispondente
                #TODO
        except Exception as e:
            output.insert(tk.END, f"[Error] {e}\n")
            break

# === Send Commands to Arduino ===
def send_open():
    ser.write(b'open\n')

def send_close():
    ser.write(b'close\n')

# === Close Program ===
def on_close():
    global running
    running = False
    if ser.is_open:
        ser.close()
    root.quit()

# === GUI Setup ===
root = tk.Tk()
root.title("Smart Gripper Monitor")
root.protocol("WM_DELETE_WINDOW", on_close)

frame = ttk.Frame(root, padding=10)
frame.grid()

ttk.Button(frame, text="Train", command=send_open).grid(row=0, column=0)
ttk.Button(frame, text="Touch grass", command=send_close).grid(row=0, column=1)

output = tk.Text(frame, height=20, width=50)
output.grid(row=1, column=0, columnspan=2)

# === Start Serial Reader Thread ===
init_serial()
thread = threading.Thread(target=read_serial, daemon=True)
thread.start()

# === Start GUI ===
root.mainloop()
