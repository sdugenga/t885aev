    # extract the first moving segment to work on as a test
    moving_keys = [key for key in segments.keys() if 'moving' in key]

    processed_segments = []

    for key in moving_keys:
        segment = segments[key]
        segment_length = segment['incremental_distance'].sum()

        simulated_segment = process_segment(segment_length, parameters)
        simulated_segment = resample_dataframe(simulated_segment)

        simulated_segment['segment_key'] = key

        processed_segments.append(simulated_segment)



    first_moving_key = moving_keys[0]
    first_moving_segment = segments[first_moving_key]

    # calculate the distance for this segment
    segment_length = first_moving_segment['incremental_distance'].sum()

    segment_dataframe = process_segment(segment_length, parameters)
    segment_dataframe = resample_dataframe(segment_dataframe)
