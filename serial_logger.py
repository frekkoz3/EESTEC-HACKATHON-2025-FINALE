import serial
import csv
from collections import deque

SERIAL_PORT = "COM6"
BAUD_RATE = 115200

file_index = input("Inserisci il numero del file:")
OUTPUT_FILE = f"data\dati_oggetto_{file_index}.csv"

# Buffer circolare di 30 elementi
buffer = deque(maxlen=30)

# Avvia connessione seriale
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
print(f"Connesso a {SERIAL_PORT} a {BAUD_RATE} baud")
while True:
    line = ser.readline().decode('utf-8').strip()
    if line:
        print(line)  # stampa per debug
        buffer.append(line)

        # Scrivi il buffer su CSV
        with open(OUTPUT_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            for entry in buffer:
                # supponendo i valori separati da virgola
                writer.writerow(entry.split(','))