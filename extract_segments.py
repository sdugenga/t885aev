import numpy as np
import pandas as pd

def main():
    # vehicle design parameters from Julians spreadsheets etc.
    parameters = {'max_velocity': convert_mph_ms(25),
                  'max_accel': 1,
                  'max_decel': 1,
                  'drag': 0.5,
                  'rolling_resistance': 0.03,
                  'mass': 1350,
                  'frontal_area': 2.646
                  }
    
    dataframe = pd.read_csv("data/processed/udds_processed.csv")

    # boolean mask to determine stopped status
    is_stopped = dataframe['speed_ms'] == 0

    # identify segment boundaries between stopped and moving segments
    segment_change = is_stopped.ne(is_stopped.shift()).cumsum()

    # add the segment number column
    dataframe['segment_number'] = segment_change

    # add a segment type column based on stopped or moving
    dataframe['segment_type'] = is_stopped.map({True: 'stopped', False: 'moving'})

    # put together a dictionary of pandas dataframes, one for each segment
    segments = {}
    for segment_number, segment_df in dataframe.groupby('segment_number'):
        segment_type = segment_df['segment_type'].iloc[0]
        key = f"segment{segment_number}_{segment_type}"
        segments[key] = segment_df

    # extract the first moving segment to work on as a test
    moving_keys = [key for key in segments.keys() if 'moving' in key]
    first_moving_key = moving_keys[0]
    first_moving_segment = segments[first_moving_key]

    # calculate the distance for this segment
    segment_length = first_moving_segment['incremental_distance'].sum()

    segment_dataframe = process_segment(segment_length, parameters)

    segment_dataframe.to_csv(f"data/processed/{first_moving_key}_processed.csv")
    print(f"New file generated")


def convert_mph_ms(mph):
    metres_in_mile = 1609.344 # constant (source)
    seconds_in_hour = 3600 # s/h
    miles_per_second = mph/seconds_in_hour # miles/s
    metres_per_second = miles_per_second*metres_in_mile
    
    return metres_per_second


def process_segment(segment_length, parameters):
    # set up initial variables for segment processing
    dt = 1
    position = 0
    segment_time = 0
    velocity = 0
    segment_energy = 0
    
    # get the variables out of the parameters dict
    max_velocity = parameters['max_velocity']
    max_accel = parameters['max_accel']
    max_decel = parameters['max_decel']
    drag = parameters['drag']
    rolling_resistance = parameters['rolling_resistance']
    mass = parameters['mass']
    frontal_area = parameters['frontal_area']

    # calculate the incline of the segment
    incline = 0

    rows = []

    while position < segment_length:
        # decide whether the vehicle is accelerating or decelerating
        acceleration = decide_acceleration(position, velocity, segment_length, max_velocity, max_accel, max_decel)

        # update velocity and position
        velocity += acceleration * dt
        velocity = max(0, min(velocity, max_velocity))
        # checks if the next step will take us beyond the final position
        # this would basically stop the vehicle just short of the actual segment length

        incremental_distance = velocity * dt

        # if the next step would overshoot, trum and break the loop
        if position + incremental_distance >= segment_length:
            incremental_distance = segment_length - position
            position = segment_length

            velocity = 0
        
            # Calculate power at given time segment
            power = power_required(acceleration, velocity, drag, rolling_resistance, incline, mass, frontal_area)
            if power > 0:
                segment_energy += power
                
                
                # This is where I might add some regen in to the equation

            rows.append({'time_s': segment_time,
                        'speed_ms': velocity,
                        'incremental_distance': incremental_distance,
                        'cumulative_distance': position,
                        'acceleration_mss': acceleration,
                        'power_W': power,
                        'incremental_energy_J': power,
                        'cumulative_energy_J': segment_energy
            })

            break
        
        position += incremental_distance

        # Calculate power at given time segment
        power = power_required(acceleration, velocity, drag, rolling_resistance, incline, mass, frontal_area)
        if power > 0:
            segment_energy += power

        rows.append({'time_s': segment_time,
                     'speed_ms': velocity,
                     'incremental_distance': incremental_distance,
                     'cumulative_distance': position,
                     'acceleration_mss': acceleration,
                     'power_W': power,
                     'incremental_energy_J': power,
                     'cumulative_energy_J': segment_energy
        })

        segment_time += dt

    return pd.DataFrame(rows)


def decide_acceleration(pos, v, len, v_max, a_max, d_max):
    distance_remaining = len - pos
    if v > 0:
        stopping_distance = np.power(v, 2)/(2*d_max)
    else:
        stopping_distance = 0

    if distance_remaining <= stopping_distance:
        # need to decelerate to stop in time
        return -d_max
    elif v < v_max:
        # can keep accelerating up to max velocity
        return a_max
    else:
        # continue to cruise at max velocity
        return 0


def power_required(acceleration,
                   velocity,
                   drag,
                   rolling_resistance,
                   incline,
                   mass,
                   frontal_area):
    # power equation from Julian's document
    # unsure about negative incline here
    power = 0.6125*frontal_area*drag*np.power(velocity, 3)+9.81*mass*velocity*(rolling_resistance+incline+0.107*acceleration)
    return(power)


if __name__ == "__main__":
    main()