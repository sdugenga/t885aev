import math
import csv
import time

from aev_utils import decide_acceleration, power_required

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
        # dont allow velocity to drop below zero
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
            segment_energy += power * dt
            # This is where I might add some regen in to the equation

    return segment_energy, segment_time


def calculate_incline(run, rise):
    return(math.atan(rise/run))


if __name__ == "__main__":
    main()