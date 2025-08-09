import math
import csv
import time
import pandas as pd

from aev_utils import process_segment, get_parameters

def main():
    # vehicle design parameters from Julians spreadsheets etc.
    parameters = get_parameters()
    
    start_time = time.time()

    input_file = "data/segments/route_a_segments.csv"
    output_file = "data/results/route_a_energy.csv"
    output_detail_file = "data/results/route_a_detailed.csv"

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
    all_detailed_segments = []
    total_energy = 0
    total_time = 0
    total_length = 0
    time_offset = 0

    for segment in segments:
        detailed_df, segment_energy, segment_time = process_segment(
            segment['segment_length'],
            segment['segment_elev_change'],
            parameters
        )

        detailed_df['time_s'] += time_offset
        time_offset = detailed_df['time_s'].iloc[-1] + 1

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

        # add segment ID to detailed_df and append to master list
        detailed_df['segment_id'] = segment['segment_id']
        all_detailed_segments.append(detailed_df)

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

    # save full detailed CSV
    stitched_df = pd.concat(all_detailed_segments, ignore_index=True)
    stitched_df['cumulative_distance'] = stitched_df['incremental_distance'].cumsum()
    stitched_df.to_csv(output_detail_file, index=False)

    print(f"Processed {len(segments)} segments.")
    print(f"Route data saved to {output_file}")
    print(f"Detailed simulation saved to {output_detail_file}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"simulation took {elapsed_time} seconds")


if __name__ == "__main__":
    main()