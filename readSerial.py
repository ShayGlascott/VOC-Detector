import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import datetime
import csv
import os

style.use('fivethirtyeight')

ser = serial.Serial('/dev/cu.usbmodem11401', 9600)

fig, axs = plt.subplots(5, 1, sharex=True)
fig.subplots_adjust(hspace=0.5)

times = []
co2_levels = []
tvoc_levels = []
temperatures = []
pressures = []
humidities = []

filename = 'data-' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.csv'
if not os.path.exists(filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'CO2', 'TVOC', 'Temperature', 'Pressure', 'Humidity'])

def animate(i):
    line = ser.readline().decode('utf-8').strip()
    if line.startswith('(') and line.endswith(')'):
        line = line[1:-1] 
        data = line.split(',')
        if len(data) == 5:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            times.append(now)
            co2_levels.append(float(data[0]))
            tvoc_levels.append(float(data[1]))
            temperatures.append(float(data[2]))
            pressures.append(float(data[3]))
            humidities.append(float(data[4]))

            with open(filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([now] + data)

            x_times = list(range(len(times)))
            axs[0].clear()
            axs[0].plot(x_times, co2_levels, label='CO2 (ppm)')
            axs[0].set_ylabel('CO2 (ppm)')
            axs[0].legend(loc='upper left')

            axs[1].clear()
            axs[1].plot(x_times, tvoc_levels, label='TVOC (ppb)')
            axs[1].set_ylabel('TVOC (ppb)')
            axs[1].legend(loc='upper left')

            axs[2].clear()
            axs[2].plot(x_times, temperatures, label='Temp (F)')
            axs[2].set_ylabel('Temperature (F)')
            axs[2].legend(loc='upper left')

            axs[3].clear()
            axs[3].plot(x_times, pressures, label='Pressure (Pa)')
            axs[3].set_ylabel('Pressure (Pa)')
            axs[3].legend(loc='upper left')

            axs[4].clear()
            axs[4].plot(x_times, humidities, label='Humidity (%)')
            axs[4].set_ylabel('Humidity (%)')
            axs[4].legend(loc='upper left')

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()