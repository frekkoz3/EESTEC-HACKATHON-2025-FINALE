import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading

# Open serial port
ports = list(serial.tools.list_ports.comports())
for i, port in enumerate(ports):
    print(f"{i}: {port.device} - {port.description}")

index = int(input("Select port index: "))
ser = serial.Serial(ports[index].device, 115200)

# Flag to stop the thread safely
running = True

def read_serial():
    while running and ser.is_open:
        try:
            line = ser.readline().decode('utf-8').strip()
            output.insert(tk.END, line + '\n')
            output.see(tk.END)
        except Exception as e:
            print(f"Error reading serial: {e}")
            break

def send_open():
    ser.write(b'3\n')  # Assuming 3V = open command

def send_close():
    ser.write(b'-3\n')  # Assuming -3V = close command

def on_close():
    global running
    running = False  # Stop the serial reading loop
    if ser.is_open:
        ser.close()
    root.destroy()

root = tk.Tk()
root.title("Smart Gripper Monitor")
root.protocol("WM_DELETE_WINDOW", on_close)  # Handle window close

frame = ttk.Frame(root, padding=10)
frame.grid()

ttk.Button(frame, text="Open Gripper", command=send_open).grid(row=0, column=0)
ttk.Button(frame, text="Close Gripper", command=send_close).grid(row=0, column=1)

output = tk.Text(frame, height=20, width=50)
output.grid(row=1, column=0, columnspan=2)

# Start serial reader thread
thread = threading.Thread(target=read_serial, daemon=True)
thread.start()

root.mainloop()
