import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation

SERIAL_PORT = 'COM8'
BAUD_RATE = 115200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

W = 25  
L = 25  

load_cell_positions = [
    (-W, -L),   
    (+W, -L),  
    (-W, +L),   
    (+W, +L),   
]

fig, ax = plt.subplots()
ax.set_xlim(-W - 10, W + 10)
ax.set_ylim(-L - 10, L + 10)
ax.set_aspect('equal')
ax.set_title("Real-Time Center of Pressure (Stabilogram)")
ax.set_xlabel("X (cm)")
ax.set_ylabel("Y (cm)")
dot, = ax.plot([], [], 'ro', markersize=10)

square = plt.Rectangle((-W, -L), 2*W, 2*L, fill=False, linestyle='--')
ax.add_patch(square)

def compute_center_of_pressure(readings):
    total_force = sum(readings)
    if total_force == 0:
        return 0, 0  # Default to center
    x = sum(f * pos[0] for f, pos in zip(readings, load_cell_positions)) / total_force
    y = sum(f * pos[1] for f, pos in zip(readings, load_cell_positions)) / total_force
    return x+8, y-8

def update(frame):
    line = ser.readline().decode().strip()
    try:
        readings = list(map(int, line.split(',')))
        if len(readings) == 4:
            abs_readings = [abs(f) for f in readings]
            x, y = compute_center_of_pressure(abs_readings)
            dot.set_data([x], [y])
    except ValueError:
        pass
    return dot,

ani = animation.FuncAnimation(
    fig, update, interval=12, blit=True, cache_frame_data=False
)

plt.tight_layout()
plt.show()
ser.close()
