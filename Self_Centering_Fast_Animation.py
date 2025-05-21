import sys
import serial
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import threading

# ---------- Configuration ----------
SERIAL_PORT = 'COM6'
BAUD_RATE = 115200
PLATFORM_WIDTH = 0.5
PLATFORM_LENGTH = 0.5

# ---------- Global Variables ----------
data_lock = threading.Lock()
cop_x, cop_y = 0, 0

# Calibration variables
calibration_samples = 100  # number of samples to average for zeroing
calib_count = 0
calib_x_sum = 0
calib_y_sum = 0
x_offset, y_offset = 0, 0
calibrated = False

# ---------- CoP Calculation ----------
def compute_center_of_pressure(fl, fr, rl, rr):
    total = fl + fr + rl + rr
    if total == 0:
        return 0, 0
    x = ((fr + rr) - (fl + rl)) * (PLATFORM_WIDTH / 2) / total
    y = ((fl + fr) - (rl + rr)) * (PLATFORM_LENGTH / 2) / total
    return x, y

# ---------- Serial Reading Thread ----------
def read_serial():
    global cop_x, cop_y, calib_count, calib_x_sum, calib_y_sum, x_offset, y_offset, calibrated
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
        print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
    except Exception as e:
        print(f"Failed to connect to {SERIAL_PORT}: {e}")
        return

    while True:
        try:
            line = ser.readline().decode().strip()
            parts = list(map(float, line.split(',')))
            if len(parts) != 5:
                continue
            _, fl, fr, rl, rr = parts
            x, y = compute_center_of_pressure(fl, fr, rl, rr)

            if not calibrated:
                # Collect calibration data
                calib_x_sum += x
                calib_y_sum += y
                calib_count += 1

                if calib_count >= calibration_samples:
                    x_offset = calib_x_sum / calibration_samples
                    y_offset = calib_y_sum / calibration_samples
                    calibrated = True
                    print(f"Calibration done: x_offset={x_offset:.4f}, y_offset={y_offset:.4f}")

                # Show zero during calibration
                with data_lock:
                    cop_x, cop_y = 0, 0
            else:
                # Subtract offset from raw data
                with data_lock:
                    cop_x, cop_y = x - x_offset, y - y_offset

        except Exception as e:
            print(f"Serial Read Error: {e}")
            continue

# ---------- Start Serial Thread ----------
threading.Thread(target=read_serial, daemon=True).start()

# ---------- PyQtGraph Real-Time Plot ----------
app = QApplication([])
win = pg.GraphicsLayoutWidget(title="Stable-o-gram (Center of Pressure)")
plot = win.addPlot()
plot.setXRange(-PLATFORM_WIDTH / 2, PLATFORM_WIDTH / 2)
plot.setYRange(-PLATFORM_LENGTH / 2, PLATFORM_LENGTH / 2)
plot.showGrid(x=True, y=True)

# CoP dot
dot = plot.plot([0], [0], pen=None, symbol='o', symbolSize=20, symbolBrush='r')

# ---------- Update Function ----------
def update():
    with data_lock:
        dot.setData([cop_x], [cop_y])

# Timer to update ~80 FPS
timer = QTimer()
timer.timeout.connect(update)
timer.start(12)

# ---------- Run App ----------
win.show()
sys.exit(app.exec())
