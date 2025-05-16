import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation

SERIAL_PORT = 'COM8'  
BAUD_RATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

fig, ax = plt.subplots()
bars = ax.bar(['Load Cell 1', 'Load Cell 2', 'Load Cell 3', 'Load Cell 4'], [0, 0, 0, 0])
ax.set_ylim(-10, 1000000)  

def update(frame):
    line = ser.readline().decode().strip()
    try:
        values = list(map(int, line.split(',')))
        if len(values) == 4:
            for bar, val in zip(bars, values):
                bar.set_height(abs(val))
    except ValueError:
        pass  

ani = animation.FuncAnimation(fig, update, interval=12) 
plt.title("Real-Time Load Cell Readings")
plt.ylabel("Load Cell Output (raw)")
plt.tight_layout()
plt.show()

ser.close()
