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
        
        segment_df = segment_df.copy().reset_index(drop=True)
        segment_df['time_s'] = np.arange(len(segment_df))
        segment_df['segment_number'] = int(segment_number)
        
        segments[key] = segment_df

    ### START STITCHING BACK TOGETHER HERE ###

    stitched_segments = []
    time_offset = 0

    ordered_keys = sorted(segments.keys(), key=lambda x: int(x.split('_')[0].replace('segment', '')))

    for key in ordered_keys:
        segment = segments[key]
        # check if the segment is a moving segment or not
        if 'moving' in key:
            # if it is a moving segment, it needs to be processed and we need the distance
            segment_length = segment['incremental_distance'].sum()
            # then we can process it based on the length and parameters
            simulated_segment = process_segment(segment_length, parameters)
            # simulated_segment = resample_dataframe(simulated_segment)
            # the time column needs to be adjusted so it all lines up
            simulated_segment['time_s'] += time_offset
            # and the time offset needs to be updated for the next segment
            time_offset = simulated_segment['time_s'].iloc[-1] + 1
            # then we can append the simulated segment to the list of segments
            segment_number = int(key.split('_')[0].replace('segment', ''))
            simulated_segment['segment_number'] = segment_number
            stitched_segments.append(simulated_segment)
        else:
            # the same process for the stopped segments
            segment = segment.copy()
            segment['time_s'] += time_offset
            time_offset = segment['time_s'].iloc[-1] + 1
            stitched_segments.append(segment)

    stitched_df = pd.concat(stitched_segments, ignore_index=True)

    cols_to_drop = [
        col for col in stitched_df if col.startswith('Unnamed')] + [
            'speed_mph',
            'speed_mph_capped',
            'cumulative_distance',
            'cumulative_energy_J',
            'segment_type'
        ]
    
    stitched_df = stitched_df.drop(columns=[
        col for col in cols_to_drop if col in stitched_df.columns
    ])

    stitched_df['cumulative_distance'] = stitched_df['incremental_distance'].cumsum()
    stitched_df['cumulative_energy'] = stitched_df['incremental_energy_J'].cumsum()

    cols = list(stitched_df.columns)

    cols.remove('cumulative_distance')
    cols.remove('cumulative_energy')

    distance_idx = cols.index('incremental_distance') + 1
    energy_idx = cols.index('incremental_energy_J') + 1

    cols.insert(distance_idx, 'cumulative_distance')
    cols.insert(energy_idx, 'cumulative_energy')

    stitched_df = stitched_df[cols]

    stitched_df.to_csv(f"data/processed/stitched_data.csv")
    print(f"New file generated")


def convert_mph_ms(mph):
    metres_in_mile = 1609.344 # constant (source)
    seconds_in_hour = 3600 # s/h
    miles_per_second = mph/seconds_in_hour # miles/s
    metres_per_second = miles_per_second*metres_in_mile
    
    return metres_per_second


def process_segment(segment_length, parameters):
    # set up initial variables for segment processing
    dt = 0.1
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

        # if the next step would overshoot, trim and break the loop
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


def resample_dataframe(dataframe):
    # keeping the last and first index:
    indices = [0] + list(range(10, len(dataframe) -1, 10)) + [len(dataframe)-1]
    resampled_dataframe = dataframe.iloc[indices].reset_index(drop=True)

    resampled_dataframe['time_s'] = np.arange(len(resampled_dataframe))
    return resampled_dataframe


if __name__ == "__main__":
    main()