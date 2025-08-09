import numpy as np
import pandas as pd

from aev_utils import process_segment, get_parameters

def main():
    # vehicle design parameters from Julians spreadsheets etc.
    parameters = get_parameters()
    
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

    segment_elev_change = 0 # just because the function expects something like this

    for key in ordered_keys:
        segment = segments[key]
        # check if the segment is a moving segment or not
        if 'moving' in key:
            # if it is a moving segment, it needs to be processed and we need the distance
            segment_length = segment['incremental_distance'].sum()
            # then we can process it based on the length and parameters
            simulated_segment, _, _ = process_segment(segment_length, segment_elev_change, parameters)
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

    stitched_df.to_csv(f"data/results/stitched_data.csv")
    print(f"New file generated")


if __name__ == "__main__":
    main()