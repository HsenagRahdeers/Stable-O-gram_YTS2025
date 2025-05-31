import sys
import serial
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import numpy as np
import threading
# ---------- Configuration ----------
SERIAL_PORT = 'COM6'
BAUD_RATE = 115200
PLATFORM_WIDTH = 0.5
PLATFORM_LENGTH = 0.5
TRACER_BUFFER_SIZE = 80  # Number of previous points to show
# ---------- Global Variables ----------
data_lock = threading.Lock()
cop_x, cop_y = 0, 0
trace_buffer = []
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
    global cop_x, cop_y, trace_buffer
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
        print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
    except Exception as e:
        print(f"Failed to connect to {SERIAL_PORT}: {e}")
        return
# Open CSV file for appending
    with open("Debug.csv", "a") as f:
        f.write("x,y\n")  # Write header
        while True:
            try:
                line = ser.readline().decode().strip()
                parts = list(map(float, line.split(',')))
                if len(parts) != 5:
                    continue
                _, fl, fr, rl, rr = parts
                fl, fr, rl, rr = (
                    -(20000/12000)*((20000/1215500 * fl) -31650),
                    -(20000/5880)*((20000/2535000 * fr)+14000),
                    -(20000/143000)*(1/5 * rl+892800),
                    -(20000/139000)*(1/5 * rr+766000)         
                )            
                x, y = compute_center_of_pressure(fl, fr, rl, rr)
                print(f"FL: {fl:.1f}, FR: {fr:.1f}, RL: {rl:.1f}, RR: {rr:.1f} => CoP: ({x:.3f}, {y:.3f})")
                # Write to CSV
                f.write(f"{x},{y}\n")
                f.flush()
                with data_lock:
                    cop_x, cop_y = x, y
                    trace_buffer.append((x, y))
                    if len(trace_buffer) > TRACER_BUFFER_SIZE:
                        trace_buffer.pop(0)
            except Exception as e:
                print(f"Serial Read Error: {e}")
                continue
# ---------- Start Serial Thread ----------
threading.Thread(target=read_serial, daemon=True).start()
# ---------- PyQtGraph Real-Time Plot ----------
app = QApplication([])
win = pg.GraphicsLayoutWidget(title="Stable-o-gram (Center of Pressure)")
plot = win.addPlot()
plot.setAspectLocked(True)
plot.setXRange(-PLATFORM_WIDTH / 2, PLATFORM_WIDTH / 2)
plot.setYRange(-PLATFORM_LENGTH / 2, PLATFORM_LENGTH / 2)
plot.showGrid(x=True, y=True)
# CoP dot
dot = plot.plot([0], [0], pen=None, symbol='o', symbolSize=10, symbolBrush='r')
# Tracer plot
tracer = plot.plot([], [], pen=pg.mkPen('g', width=1))
# ---------- Update Function ----------
def update():
    with data_lock:
        dot.setData([cop_x], [cop_y])
        if trace_buffer:
            x_vals, y_vals = zip(*trace_buffer)
            tracer.setData(x_vals, y_vals)
# Timer to update ~80 FPS
timer = QTimer()
timer.timeout.connect(update)
timer.start(12)
# ---------- Run App ----------
win.show()
sys.exit(app.exec())
