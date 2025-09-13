import matplotlib.pyplot as plt
import numpy as np
import pickle
import random

# This file creates the data to be used in the visualization

debug = True # whether or not to show debugging plots

# Creating the Data Files
velocity_file = open("velocity_data.txt", "wb")
acc_pedal1_file = open("acc_pedal1_data.txt", "wb")
acc_pedal2_file = open("acc_pedal2_data.txt", "wb")
wheel_rpm_file = open("wheel_rpm_data.txt", "wb")
time_series_file = open("time_series.txt", "wb")
brake_pedal_file = open("brake_pedal_data.txt", "wb")
distance_file = open("distance_data.txt", "wb")


# Define a gaussian noise function to create sensor noise limited by the sensor lower_and upper bounds
def gaussian_noise(dataset, size, lower_bound = -1, upper_bound = -1):
    for i in range(len(dataset)):
        # Create Gaussian Noise for the data
        new =  dataset[i] + 2 * size * (random.uniform(0, 1) - 0.5)
    
        # Keep the values within the bounds if the bounds are set and the noise crosses the boudns
        if new < lower_bound and lower_bound != -1:
            new = lower_bound
        
        elif new > upper_bound and upper_bound != -1:
            new = upper_bound
    
        dataset[i] = new

# Creating lists of data
velocities = []
acc_pedal1_list = []
acc_pedal2_list = []
brake_pedal_list = []
wheel_rpm_list = []
time_series = []
distances_traveled = []

# Part one, defining Constants 

# Approximate mass of the car, in Kilograms, derived from AME25 website
mass = 200 

# Approximate top speed of car, in Meters/Second, derived from AME25 website
v_top = 38

# Output Power of the car, in watts, derived from AME25 website
power = 80000

# Approximate the circumference of the tires of the car in meters, assuming a wheel diameter of one foot
wheel_diameter = 0.3048
wheel_circumference = np.pi * wheel_diameter

'''
At the highest velocity v_top, the car's propulsion force (which is power / v_top)
and the air resistance force, which is some constant multiplied by v_top^2
are equal, so we can determine the air_resistance coefficient by calculating
P / v_top ^ 3
'''
air_res = power / (v_top ** 3)

'''
Force * Acceleration (or dv/dt) is equal to the 
force of power (which is power / current velocity) - the force of air resistance
(which is the coefficient of air resistance multiplied by the square of velocity)
so the change in velocity, can be calculated by  (((P/v) - air_res * (v ** 2)) * dt) / m
Where P is the input power, v is the current velocity, air_res is the prev. coefficient, 
and m is the car_mass  
'''

'''
The 5 statuses we'll define
accelerating = the car is accelerating at max thrust
braking = the car is braking at max thrust
wheel_slip = the wheels are slipping and the car is accelerating at 50% efficiency
turning = the car speed is held steady as the car turns
stopping = APPS anomaly triggered, and the car is slowing down with 50% braking to a stop
'''
status = 'wheel_slip'

#Define Sensor Values to be tracked over time
velocity = 0
velocity_delta = 0

time = 0
time_delta = 0.2

acc_pedal1 = 1
acc_pedal2 = 1
wheel_rpm = 0
brake_pedal = 0

distance_traveled = 0

# Define sensor values at next time step for euler's approximation
new_velocity = 0
new_time = 0
new_acc_pedal1 = 1
new_acc_pedal2 = 1
new_brake_pedal = 0
new_wheel_rpm = 0

# Variable to determine distance to tag the start of each drive phase

phase_start_distance = 0
phase_start_time = 0

time_series.append(time)

velocities.append(velocity)
wheel_rpm_list.append(wheel_rpm)

acc_pedal1_list.append(acc_pedal1)
acc_pedal2_list.append(acc_pedal2)
brake_pedal_list.append(brake_pedal)

while True:
    #We're calculting for the next time step, so change the new_time to get the next time step:
    new_time = time + time_delta
    
    if status == 'wheel_slip':
        # Determine the change in velocity for euler's method approximation approximation
        try:
            # Let the power be one half of the power that could normally be generated
            velocity_delta = ((((power / velocity) / 2) - air_res * (velocity ** 2)) * time_delta) / (mass)
        except:
            # If velocity is zero we set the velocity delta to a reasonable value to avoid division by zero
            velocity_delta = 6.5
        
        # Car is accelerating at full power
        new_acc_pedal1 = 1
        new_acc_pedal2 = 1
        new_brake_pedal = 0
        
        # Add the values of velocity_delta to get velocity at the next time step
        new_velocity = velocity + velocity_delta 

        # As the wheel is slipping, the wheel rpm is double the velocity
        new_wheel_rpm = new_velocity / wheel_diameter * 60 * 2
        
        # Track the distance travelled
        distance_traveled += (velocity + ((new_velocity - velocity) / 2)) * time_delta

        # after 0.6 seconds, the wheel gets traction and the power goes back to normal
        if new_time > 0.6:
            status = 'accelerating'
    
    elif status == 'accelerating':
        # Determine the change in velocity for euler's method approximation approximation
        try:
            velocity_delta = (((power / velocity) - air_res * (velocity ** 2)) * time_delta) /  (mass)
        except:
            velocity_delta = 13
        
        # Add the values of velocity_delta to get velocity at the next time step
        new_velocity = velocity + velocity_delta 

        # Calculate the wheel RPM based on velocity
        new_wheel_rpm = new_velocity / wheel_diameter * 60

        # Car is accelerating at full power
        new_acc_pedal1 = 1
        new_acc_pedal2 = 1
        new_brake_pedal = 0

        # Add distance travelled to know when to switch to deceleration (at the end of a straight)
        distance_traveled += (velocity + ((new_velocity - velocity) / 2)) * time_delta

        if distance_traveled - phase_start_distance >= 200:
            # Travelled to the end of the straight, start braking for the turn
            status = 'braking'


    elif status == 'braking':
        # Determine the change in velocity for euler's method approximation approximation
        # Braking is similar to Accelerating, except the motor force is negated
        try:
            velocity_delta = ((-(power / velocity) - air_res * (velocity ** 2)) * time_delta) /  (mass)
        except:
            #If velocity is zero we set the velocity delta to a reasonable value to avoid division by zero
            velocity_delta = -13
        
        # Add the values of velocity_delta to get velocity at the next time step
        new_velocity = velocity + velocity_delta

        # Calculate the wheel RPM based on velocity
        new_wheel_rpm = new_velocity / wheel_diameter * 60

        # Car is decelerating at full power
        new_acc_pedal1 = 0
        new_acc_pedal2 = 0
        new_brake_pedal = 1
        
        # Add distance travelled for distance graph
        distance_traveled += (velocity + ((new_velocity - velocity) / 2)) * time_delta

        # Once slow enough, we begin the turn
        if new_velocity < 5:
            new_velocity = 5
            new_wheel_rpm = new_velocity / wheel_diameter * 60
            phase_start_time = new_time
            status = 'turning'
    
    elif status == 'turning' :
        # Keep the velocity constant as the car corners the turn
        # To determine the length of the turning phase, we assume that 
        # the acceleration stays constant at around 1.2 g lateral force with the car
        # going at 5 m/s for a full hairpin
        new_velocity = 5

        # Calculate the wheel RPM based on velocity
        new_wheel_rpm = new_velocity / wheel_diameter * 60

        # Car is neither accelerating nor decelerating (as air resistance is negligable at this low speed)
        new_acc_pedal1 = 0
        new_acc_pedal2 = 0
        new_brake_pedal = 0

        # Update distance traveled for graphing
        distance_traveled += 5 * time_delta
        
        # Begin accelerating once the turn duration is complete
        if(time - phase_start_time >= 2.6):
            status = 'accelerating'
            phase_start_distance = distance_traveled


    # Append the updated values to the lists and repeat
    velocities.append(new_velocity)
    wheel_rpm_list.append(new_wheel_rpm)
    time_series.append(new_time)
    distances_traveled.append(distance_traveled)
    
    acc_pedal1_list.append(new_acc_pedal1)
    acc_pedal2_list.append(new_acc_pedal2)
    brake_pedal_list.append(new_brake_pedal)

    # Set current values to the predicted next value and continue the loop
    velocity = new_velocity
    wheel_rpm = new_wheel_rpm
    time = new_time
    acc_pedal1 = new_acc_pedal1
    acc_pedal2 = new_acc_pedal2
    brake_pedal = new_brake_pedal

    # Once time exceed 45 seconds, we simulate the APPS anomaly
    if time >= 45:
        break

# The car is stopping due to APPS anomaly
while velocity > 0:
        new_time = time + time_delta
        
        # Determine the change in velocity for euler's method approximation approximation
        # Brake until stopped at 1/4 brake pressure, as the APPS trigger condition has shut down propulsion
        try:
            velocity_delta = ((-(power / velocity) / 4 - air_res * (velocity ** 2)) * time_delta) /  (mass)
        except:
            #If velocity is zero we set the velocity delta to a reasonable value to avoid division by zero
            velocity_delta = -3.25
        
        # Add the values of time_delta and velocity_delta
        new_velocity = velocity + velocity_delta 

        # Calculate the wheel RPM based on velocity
        new_wheel_rpm = new_velocity / wheel_diameter * 60
         
        # Once the car has stopped, the deceleration has ended
        if new_velocity < 0:
            new_velocity = 0
        
        # APPS anomaly, 1/4 braking and mismatch on accelerator pedals
        new_acc_pedal1 = 0
        new_acc_pedal2 = 1
        new_brake_pedal = 0.25

        # Calculate the distance travelled for graphing
        distance_traveled += (velocity + ((new_velocity - velocity) / 2)) * time_delta
        
        #Append the updated values to the lists and repeat
        velocities.append(new_velocity)
        wheel_rpm_list.append(new_wheel_rpm)
        time_series.append(new_time)
        distances_traveled.append(distance_traveled)
        
        acc_pedal1_list.append(new_acc_pedal1)
        acc_pedal2_list.append(new_acc_pedal2)
        brake_pedal_list.append(new_brake_pedal)

        # Set current values to the predicted next value and continue the loop
        velocity = new_velocity
        wheel_rpm = new_wheel_rpm
        time = new_time
        acc_pedal1 = new_acc_pedal1
        acc_pedal2 = new_acc_pedal2
        brake_pedal = new_brake_pedal

# Add gausian noise to each of the datasets to emulate sensor error
# The error is relatively high, as we assume that we use GPS to calculate velocity
# This could be improved with commercial survey GPS units, or an inertial reference unit 
gaussian_noise(velocities, 1, 0)

# Though we assume the pedals' gaussian error to be relatively high
# This error is relatively high, it is still within the 10% implausibility threshold
# The large error could be indicative of a faulty sensor that needs to be improved/replaced
gaussian_noise(acc_pedal1_list, 0.03, 0, 1)
gaussian_noise(acc_pedal2_list, 0.03, 0, 1)
gaussian_noise(brake_pedal_list, 0.03, 0, 1)

# A conservative estimate, at top speed this would be around 1% error
# This is assumed, as an encoder typically typically has very small error rate, 
# Which is less noticable at higher speeds
gaussian_noise(wheel_rpm_list, 100, 0) 


# Tentative plots for debugging 

if debug:
    plt.figure(1)
    plt.plot(time_series, velocities)
    plt.title("Velocity")
    plt.axvspan(45, time_series[-1], color='red', alpha=0.2)


    plt.figure(2)
    plt.plot(time_series, acc_pedal1_list)
    plt.plot(time_series, acc_pedal2_list)
    plt.plot(time_series, brake_pedal_list)
    plt.title("Acceleration and Braking")
    plt.axvspan(45, time_series[-1], color='red', alpha=0.2)


    plt.figure(3)
    plt.plot(time_series, wheel_rpm_list)
    plt.title("Wheel_RPM")
    plt.axvspan(45, time_series[-1], color='red', alpha=0.2)
    plt.show()

# Export final noisy data
pickle.dump(time_series, time_series_file)
pickle.dump(wheel_rpm_list, wheel_rpm_file)
pickle.dump(velocities, velocity_file)
pickle.dump(acc_pedal1_list, acc_pedal1_file)
pickle.dump(acc_pedal2_list, acc_pedal2_file)
pickle.dump(brake_pedal_list, brake_pedal_file)

#Close all files to prevent file issues
wheel_rpm_file.close()
acc_pedal2_file.close()
acc_pedal1_file.close()
velocity_file.close()
time_series_file.close() 
brake_pedal_file.close()