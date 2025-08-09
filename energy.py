import math
import csv
import time

from aev_utils import process_segment

def main():
    # vehicle design parameters from Julians spreadsheets etc.
    parameters = {'max_velocity': convert_mph_ms(25),
                  'max_accel': 2,
                  'max_jerk' : 2.5,
                  'drag': 0.5,
                  'rolling_resistance': 0.03,
                  'mass': 1350,
                  'frontal_area': 2.646
                  }
    
    start_time = time.time()

    input_file = "data/segments/route_a_segments.csv"
    output_file = "data/results/route_a_energy_alt.csv"

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


if __name__ == "__main__":
    main()