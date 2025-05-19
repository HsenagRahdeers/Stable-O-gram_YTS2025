import serial
import csv
import os

# Configuration
SERIAL_PORT = 'COM6'         # Replace with your COM port if needed
BAUD_RATE = 115200

# Save file to Desktop
OUTPUT_FILE = os.path.expanduser('~/Desktop/hx711_data2.csv')

def main():
    full_path = os.path.abspath(OUTPUT_FILE)
    print("Saving CSV to:", full_path)

    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser, \
             open(full_path, mode='w', newline='') as csvfile:

            writer = csv.writer(csvfile)
            writer.writerow(['timestamp_us', 'value1', 'value2', 'value3', 'value4'])  # header

            print("Reading data... Press Ctrl+C to stop.")

            while True:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    parts = line.split(',')
                    if len(parts) == 5:
                        writer.writerow(parts)
                        print(parts)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nLogging stopped by user.")
        print(f"File saved to: {full_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
