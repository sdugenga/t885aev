import pandas as pd

def main():
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

    print(f"Total number of segments: {len(segments)}")
    print(f"Segment keys: {list(segments.keys())}")

    dataframe.to_csv("data/processed/udds_whole_segments.csv")


if __name__ == "__main__":
    main()