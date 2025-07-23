import math
import csv
import time


# TODO: Gather together route data and put it into a suitable data structure
# TODO: Iterate over the route data data structure to get route energy
# TODO: Visualise the route energy usage
# TODO: Visualise the route topography and distance etc.
# TODO: I need to get a calculation together to get a radians value in the incline section

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
    
    start_time = time.time()

    input_file = "data/segments/route_c_segments.csv"
    output_file = "data/results/route_c_energy.csv"

    segments = []
    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            segments.append({
                'segment_id': row['segment_number'],
                'segment_length': float(row['segment_length']),
                'segment_elev_change': float(row['segment_elev_change'])
            })

    results = []
    total_energy = 0
    total_time = 0
    total_length = 0

    for segment in segments:
        segment_energy, segment_time = process_segment(segment['segment_length'],
                                         segment['segment_elev_change'],
                                         parameters
                                         )
        total_energy += segment_energy
        total_time += segment_time
        total_length += segment['segment_length']

        results.append({
            'segment_id': segment['segment_id'],
            'segment_length': segment['segment_length'],
            'cumulative_length': total_length,
            'segment_elev_change': segment['segment_elev_change'],
            'segment_time': segment_time,
            'cumulative_time': total_time,
            'segment_energy': segment_energy,
            'cumulative_energy': total_energy
        })

    with open(output_file, 'w', newline='') as outfile:
        fieldnames = [
            'segment_id',
            'segment_length', 'cumulative_length', 'segment_elev_change',
            'segment_time', 'cumulative_time',
            'segment_energy', 'cumulative_energy'
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Processed {len(segments)} segments.")
    print(f"Route data saved to {output_file}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"simulation took {elapsed_time} seconds")


def convert_mph_ms(mph):
    metres_in_mile = 1609.344 # constant (source)
    seconds_in_hour = 3600 # s/h
    miles_per_second = mph/seconds_in_hour # miles/s
    metres_per_second = miles_per_second*metres_in_mile
    
    return metres_per_second


def process_segment(segment_length, segment_elev_change, parameters):
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
    incline = calculate_incline(segment_length, segment_elev_change)

    while position < segment_length:
        # decide whether the vehicle is accelerating or decelerating
        acceleration = decide_acceleration(position, velocity, segment_length, max_velocity, max_accel, max_decel)

        # update velocity and position
        velocity += acceleration * dt
        velocity = max(0, min(velocity, max_velocity))
        # checks if the next step will take us beyond the final position
        # this would basically stop the vehicle just short of the actual segment length
        if position + velocity * dt > segment_length:
            position = segment_length
            segment_time += dt
            break
        else:
            position += velocity * dt
            # increment time
            segment_time += dt

        # Calculate power at given time segment
        power = power_required(acceleration, velocity, drag, rolling_resistance, incline, mass, frontal_area)
        if power > 0:
            segment_energy += power
            # This is where I might add some regen in to the equation

    return segment_energy, segment_time


def calculate_incline(run, rise):
    return(math.atan(rise/run))


def decide_acceleration(pos, v, len, v_max, a_max, d_max):
    distance_remaining = len - pos
    if v > 0:
        stopping_distance = math.pow(v, 2)/(2*d_max)
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
    power = 0.6125*frontal_area*drag*math.pow(velocity, 3)+9.81*mass*velocity*(rolling_resistance+incline+0.107*acceleration)
    return(power)

if __name__ == "__main__":
    main()

'''
    # These should not be dependent on the max accel decel values
    cruise_distance = example_segment_length - max_accel_distance - max_decel_distance
    cruise_time = cruise_distance / max_velocity 
    total_segment_time = max_accel_time + max_decel_time + cruise_time

    # From here we are carrying out calculations on a given segment
    rounded_time = math.ceil(total_segment_time)

    segment_energy = 0
    for t in range(rounded_time):
        # Period where vehicle is accelerating
        if t < accel_time:
            acceleration = max_accel
            velocity = max_accel * t
            print(f"accelerating...")
        # Period where vehicle is cruising
        elif t < accel_time + cruise_time:
            acceleration = 0
            velocity = max_velocity
            print(f"cruising...")
        # Period where vehicle is decelerating
        elif t < total_segment_time:
            acceleration = -max_decel
            velocity = max_velocity - max_decel * (t - accel_time - cruise_time)
            print(f"decelerating...")
        # Set to 0 where period exceeds actual max period due to rounding
        else:
            acceleration = 0
            velocity = 0

        power = power_required(acceleration, velocity, drag, rolling_resistance, incline, mass, frontal_area)
        if power > 0:
            segment_energy += power
            # This is where I might add some regen in to the equation
        print(f"power at time {t} = {power}")
        print(f"segment energy at time {t} = {segment_energy}")

    print(f"max speed = {max_velocity}")
    print(f"acceleration time = {accel_time}")
    print(f"deceleration time = {decel_time}")
    print(f"acceleration distance = {accel_distance}")
    print(f"deceleration distance = {decel_distance}")
    print(f"cruise distance = {cruise_distance}")
    print(f"cruise time = {cruise_time}")
    print(f"total segment time = {total_segment_time}")

'''