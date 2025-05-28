import sys
import glob
import csv
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication

# ---------- Configuration ----------
PLATFORM_WIDTH = 0.5
PLATFORM_LENGTH = 0.5
CSV_PATTERN = "cop_e_*.csv"  # Matches cop_data.csv, cop_data_2.csv, etc.
COLORS = ['r', 'g', 'b', 'm', 'c', 'y', 'w']

# ---------- Load Trajectories ----------
def load_trajectories():
    file_paths = glob.glob(CSV_PATTERN)
    trajectories = []

    for file in sorted(file_paths):
        with open(file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            data = [(float(x), float(y)) for x, y in reader if x and y]
            if data:
                trajectories.append((file, data))
    
    return trajectories

# ---------- PyQtGraph Plot ----------
app = QApplication([])
win = pg.GraphicsLayoutWidget(title="Multiple CoP Trajectories")
plot = win.addPlot()
plot.setAspectLocked(True)
plot.setXRange(-PLATFORM_WIDTH / 2, PLATFORM_WIDTH / 2)
plot.setYRange(-PLATFORM_LENGTH / 2, PLATFORM_LENGTH / 2)
plot.showGrid(x=True, y=True)

trajectories = load_trajectories()

for i, (filename, data) in enumerate(trajectories):
    x_vals, y_vals = zip(*data)
    color = COLORS[i % len(COLORS)]
    label = filename.replace(".csv", "")
    plot.plot(x_vals, y_vals, pen=pg.mkPen(color, width=2), name=label)

win.show()
sys.exit(app.exec())
