import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# Serial config
SERIAL_PORT = 'COM6'
BAUD_RATE = 115200

# Rolling buffer length
MAX_POINTS = 200

# Data buffers
buffer1 = deque(maxlen=MAX_POINTS)
buffer2 = deque(maxlen=MAX_POINTS)
buffer3 = deque(maxlen=MAX_POINTS)
buffer4 = deque(maxlen=MAX_POINTS)

# Setup plot
fig, ax = plt.subplots()
line1, = ax.plot([], [], label='Sensor 1')
line2, = ax.plot([], [], label='Sensor 2')
line3, = ax.plot([], [], label='Sensor 3')
line4, = ax.plot([], [], label='Sensor 4')

ax.set_ylim(-200000, 2000000)  # Adjust based on expected values
ax.set_xlim(0, MAX_POINTS)
ax.set_title("Real-Time HX711 Readings")
ax.set_xlabel("Samples")
ax.set_ylabel("Sensor Value")
ax.legend()
ax.grid(True)

# Open serial
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

def update(frame):
    try:
        line = ser.readline().decode('utf-8').strip()
        parts = line.split(',')
        if len(parts) == 5:
            v1 = abs(int(parts[1]))
            v2 = abs(int(parts[2]))
            v3 = abs(int(parts[3]))
            v4 = abs(int(parts[4]))
            buffer1.append(v1)
            buffer2.append(v2)
            buffer3.append(v3)
            buffer4.append(v4)

            line1.set_data(range(len(buffer1)), buffer1)
            line2.set_data(range(len(buffer2)), buffer2)
            line3.set_data(range(len(buffer3)), buffer3)
            line4.set_data(range(len(buffer4)), buffer4)

    except Exception as e:
        print(f"Error: {e}")

    return line1, line2, line3, line4

# Initialize plot limits
def init():
    line1.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    line4.set_data([], [])
    return line1, line2, line3, line4

ani = animation.FuncAnimation(fig, update, init_func=init, interval=50, blit=True)

try:
    plt.tight_layout()
    plt.show()
except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    ser.close()
