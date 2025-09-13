import pickle
from math import *
import matplotlib.pyplot as plt


# This program creates views for the data to be analyzed


# Import all data
velocity_file = open("velocity_data.txt", "rb")
acc_pedal1_file = open("acc_pedal1_data.txt", "rb")
acc_pedal2_file = open("acc_pedal2_data.txt", "rb")
wheel_rpm_file = open("wheel_rpm_data.txt", "rb")
time_series_file = open("time_series.txt", "rb")
brake_pedal_file = open("brake_pedal_data.txt", "rb")


velocity_list = pickle.load(velocity_file)
acc_pedal1_list = pickle.load(acc_pedal1_file)
acc_pedal2_list = pickle.load(acc_pedal2_file)
wheel_rpm_list = pickle.load(wheel_rpm_file)
time_series_list = pickle.load(time_series_file)
brake_pedal_list = pickle.load(brake_pedal_file)

# Create 4 Figure Plots
plt.figure(1)
plt.plot(time_series_list, velocity_list, label = "velocity")
plt.title("Velocity")
plt.xlabel("Time (in seconds)")
plt.ylabel("Velocity (in m/s)")
plt.axvspan(45, time_series_list[-1], color='red', alpha=0.1)
plt.legend(loc = 'upper right')


plt.figure(2)
plt.plot(time_series_list, acc_pedal1_list, label = "accel. pedal 1",  alpha = 0.25, color = 'green')
plt.plot(time_series_list, acc_pedal2_list, label = "accel. pedal 2", alpha = 0.25, color = 'blue')
plt.plot(time_series_list, brake_pedal_list, label = "brake pedal", color = 'red')
plt.title("Acceleration and Braking")
plt.xlabel("Time (in seconds)")
plt.ylabel("Pedal Pressure Percent")
plt.ylim(0, 1.3)
plt.axvspan(45, time_series_list[-1], color='red', alpha=0.1)
plt.legend(loc = 'upper right')


plt.figure(3)
plt.plot(time_series_list, wheel_rpm_list, label = "wheel RPM")
plt.legend(loc = 'upper right')
plt.title("Wheel RPM")
plt.xlabel("Time (in seconds)")
plt.ylabel("Wheel RPM")
plt.axvspan(45, time_series_list[-1], color='red', alpha=0.1)


plt.show()





wheel_rpm_file.close()
acc_pedal2_file.close()
acc_pedal1_file.close()
velocity_file.close()
time_series_file.close() 
brake_pedal_file.close()

