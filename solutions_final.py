import random
from math import pi, cos, sin
import math

# please refer to ppt file for justification of selected parameters
time_duration = 160 # this is the number of planemove|s
board_width = 20 # translates to 560 km
board_height = 8 # translates to 240 km
starting_point = (4, 4)
sensor_detector_range = 1 # 43km radius, scaled down to 30km radius
UAV_speed = 0.933 # 222 km hr-1, translated to 0.933 units on a 8 by 20 grid

def random_fly(previous_move):
    '''Function that uses polar coordinate function to produce a random cartesian coordinate to fly towards
        Takes in the previous coordinate to determine the next position
        Outputs a tuple, which is the cartesian coordinate of the new 
    '''
    
    # each flight movement is 1 unit
    radius = UAV_speed
    
    check = 0
    # while loop eventually checks for position of new coordinate (prevent new coordinate from being outside the board)
    while check == 0:
        theta = random.randint(-180, 180)

        # Converting theta from degree to radian
        theta = theta * math.pi/180.0;

        # Converting polar to cartesian coordinates
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)

        new_x = previous_move[0] + x
        new_y = previous_move[1] + y

        # prevent plane from flying out of board
        if new_x > 0 and new_x < board_width and new_y > 0 and new_y < board_height:
            check += 1
       
    return (new_x, new_y)

def check_if_inside_circle(center, point, radius):
    '''function that will check point vs center to see whether point is within a circle radius (detected by sensor)
        Takes in the center of circle (plane position), point (point being checked), and radius of circle (sensor radius)
        Outputs a boolean, regarding whether the point is inside the circle.
    '''

    dx = abs(point[0]-center[0])
    dy = abs(point[1]-center[1])
    
    # if point is likely outside of circle
    if dx > radius: 
        return False
    if dy > radius: 
        return False
    
    # if point is very likely inside circle
    if dx + dy <= radius:
        return True
    
    # unsure about point, use cartesian equation of circle
    if (pow(dx,2) + pow(dy,2)) <= pow(radius,2):
        return True
    
    else:
        return False


def sensor_circle(center, length, speed, time, history):
    ''' Function that takes in position of plane (plane_position: tuple of cartesian coordinates)
        , and calculates all the intruders found within a distance (sensor_detector_range: integer),
        based on the intruder's speed (speed: integer), the current time (time: integer).
        history is a list of previous intruders.
        Outputs a count of new intruders found (number_intruders: integer) as well as the new history
        
    '''

    temp_history = list.copy(history)
        

    counter = 0
                
    #if bounds is out of arena, then do not pick up any intruder
    x_left_bound = max(0, int(math.floor(center[0]) - length))
    x_right_bound = min(board_width, int(math.ceil(center[0]) + length + 1))
    y_low_bound = max(0, int(math.floor(center[1]) - length))
    y_up_bound = min(board_height, int(math.ceil(center[1]) + length + 1))
    
    # iterate through the bounds
    y_index = y_low_bound
    while y_index < y_up_bound:
        
        x_index = x_left_bound
        while x_index < x_right_bound:

            # check if scanned row has already been scanned before. if scanned before, move to next y_counter row
            if (speed, y_index) not in temp_history:
                
                # check if 
                if check_if_inside_circle(center, (x_index, y_index), length):

                    # check if the current time is the correct time that the intruder is on that position
                    # based on its speed
                    if (board_width - x_index)/speed == time:
                        
                        counter += 1
                        temp_history.append((speed, y_index))

            # short circuit while loop if scanned row has been scanned before
            else:
                x_index += x_right_bound

            x_index += 1

        y_index += 1

    return (counter, temp_history)

def make_best_move (sensor_scan_history, previous_move, time, speed):
    """
        Function that takes in previous_move of plane (previous_move: tuple of cartesian coordinates)
        and produces a new move. Each move will calculate max probability of detecting the most number of 
        intruders based on the current time and the speed of the intruder.
    
        Outputs a new move (tuple of cartesian coordinates), a counter of number of intruders detected in move, and adds to the
        sensor_scan_history of all detected intruders.
    """
    
    counter = 0

    sensor_scan_history_temp = list.copy(sensor_scan_history)
    sensor_scan_history_temp_return = list.copy(sensor_scan_history)
    
    move_temp = previous_move
    
    # repeat 10 random movements until the highest sum of intruders are detected
    for m in range (10):

        current_counter = 0
        move = random_fly(previous_move)

        # check and sum up all intruders within censor radius for new move.
        (counter1, sensor_scan_history_temp2) = sensor_circle(move, sensor_detector_range, speed, time, sensor_scan_history_temp)    
        current_counter += counter1
        
        
        # check for whether a move generates more number of intruders detected than previous moves
        if current_counter > counter:
            counter = current_counter
            sensor_scan_history_temp_return = list.copy(sensor_scan_history_temp2)
            move_temp = move

    # if there is no best move, a random move is made
    if counter == 0:
        move_temp = random_fly(previous_move)
    
    return move_temp, counter, sensor_scan_history_temp_return
    
def flight_path (starting_point, duration):
    """
        Generates a flight path based on a given starting_point (tuple of cartesian coordinates) and duration of flight.
        Flight path generate tries to maximise the number of intruders to be detected.
        
    """
    # initialise starting parameters
    previous_move = starting_point
    sensor_scan_history = []
    flight_path_coordinates = []
    intruder_detected = 0
    
    # maximise moves for first batch of intruders (planes with relative speed of 4x UAV)
    sensor_scan_history_temp = list.copy(sensor_scan_history)
    
    for time in range (int(duration/32)): # int(duration/32) because planes will exit arena by int(duration/32) = 5
        
        
        previous_move, counter, sensor_scan_history_temp = make_best_move (sensor_scan_history_temp, previous_move, time, 4)
        intruder_detected += counter
        flight_path_coordinates.append(previous_move)
        
    # maximise moves for second batch of intruders (UAVs with relative speed of 1x UAV)
    sensor_scan_history_temp2 = list.copy(sensor_scan_history_temp)
    for time in range (int(duration/32), int(duration/32)+int(duration/8)):
            # int(duration/32)+int(duration/8) because UAVs will exit arena by int(duration/32)+int(duration/8) = 20
        
        previous_move, counter, sensor_scan_history_temp2 = make_best_move (sensor_scan_history_temp2, previous_move, time, 1)
        intruder_detected += counter
        flight_path_coordinates.append(previous_move)
    
    # maximise moves for third batch of intruders (Frigates with relative speed of 0.1x UAV)
    sensor_scan_history_temp3 = list.copy(sensor_scan_history_temp2)
    for time in range (int(duration/8), duration):
        
        previous_move, counter, sensor_scan_history_temp3 = make_best_move (sensor_scan_history_temp3, previous_move, time, 0.1)
        intruder_detected += counter
        flight_path_coordinates.append(previous_move)
        
    sensor_scan_history = list.copy(sensor_scan_history_temp3)
     
    return {"flight_path_coordinates": flight_path_coordinates, "intruder_detected": intruder_detected, "sensor_scan_history": sensor_scan_history}




# Run the program
import statistics

all_highest_runs = []
highest_run = {
                "intruder_detected": 0,
                "flight_path_coordinates": [],
                "sensor_scan_history": []     
        }

# taking an average of 100 runs
for m in range(10):
    
    intruder_detected = 0
    flight_path_coordinates = []
    sensor_scan_history = []
    
    repeats = 100
    for n in range (repeats):

        flight = flight_path (starting_point, time_duration)
            
        if flight["intruder_detected"] >= intruder_detected:

            intruder_detected = flight["intruder_detected"]
            flight_path_coordinates = flight["flight_path_coordinates"]
            sensor_scan_history = flight["sensor_scan_history"]
    
    # 24 is the maximum possible number of intruders
    # appending the probability of meeting at least one intruder
    all_highest_runs.append(intruder_detected/24)
    
    if intruder_detected/24 == max(all_highest_runs):
        
        highest_run = {
                        "intruder_detected": intruder_detected/24,
                        "flight_path_coordinates": flight_path_coordinates,
                        "sensor_scan_history": sensor_scan_history     
        }
    
print("Completed all flights")
print("Average probability of a simulated run:", sum(all_highest_runs)/len(all_highest_runs))
print("Standard Deviation of probability of a simulated run:", statistics.stdev(all_highest_runs))
print("Highest probability:", highest_run["intruder_detected"])


#plotting flight path
best_route = highest_run["flight_path_coordinates"]
x_vals = [x for (x,y) in (best_route)]
y_vals = [y for (x,y) in (best_route)]


from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.style.use('seaborn-whitegrid')


iterx = iter(x_vals)
itery = iter(y_vals)
   
x_plot = []
y_plot = []
    

def animate(i):
    
    x_plot.append(next(iterx))
    y_plot.append(next(itery))
    
    plt.cla()
    plt.xlim(-0.5, board_width)
    plt.ylim(-0.5, board_height)
    plt.plot(x_plot, y_plot, '-')
    
    plt.gca().set_aspect("equal")
    
ani = FuncAnimation(plt.gcf(), animate, interval=1)

plt.tight_layout()
plt.show()