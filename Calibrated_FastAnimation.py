import sys
import serial
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import numpy as np
import threading

# ---------- Configuration ----------
SERIAL_PORT = 'COM8'
BAUD_RATE = 115200
PLATFORM_WIDTH = 0.4
PLATFORM_LENGTH = 0.4

# ---------- Global Variables ----------
data_lock = threading.Lock()
cop_x, cop_y = 0, 0

# ---------- CoP Calculation ----------
def compute_center_of_pressure(fl, fr, rl, rr):

    total =   fl + fr + rl + rr
    if total == 0:
        return 0, 0
    x = ((fr + rr) - (fl + rl)) * (PLATFORM_WIDTH / 2) / total
    y = ((fl + fr) - (rl + rr)) * (PLATFORM_LENGTH / 2) / total
    return x, y

# ---------- Serial Reading Thread ----------
def read_serial():
    global cop_x, cop_y
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
            fl, fr, rl, rr = (4250/(-156450) * fl) , (4250/(-147000)*fr) , (4250/(-115500)*rl) , (4250/(-175000)*rr)
            x, y = compute_center_of_pressure(fl, fr, rl, rr)

            # DEBUG: print readings and CoP
            print(f"FL: {fl:.1f}, FR: {fr:.1f}, RL: {rl:.1f}, RR: {rr:.1f} => CoP: ({x:.3f}, {y:.3f})")

            with data_lock:
                cop_x, cop_y = x, y
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
