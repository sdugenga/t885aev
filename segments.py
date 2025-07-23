import csv
import math

def main():
    input_csv = "data/elevations/route_c_elev.csv"
    output_csv = "data/segments/route_c_segments.csv"

    points = []
    with open(input_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            points.append({'latitude': float(row['latitude']),
                           'longitude': float(row['longitude']),
                           'elevation': float(row['elevation'])
                           })
            
    segments = []
    for i in range(len(points) -1):
        start = points[i]
        end = points[i + 1]
        distance = coords_to_distance(start['latitude'],
                                      start['longitude'],
                                      end['latitude'],
                                      end['longitude']
                                      )
        elevation_change = end['elevation'] - start['elevation']

        segments.append({'segment_number': i + 1,
                         'start_latitude': start['latitude'],
                         'start_longitude': start['longitude'],
                         'start_elevation': start['elevation'],
                         'end_latitude': end['latitude'],
                         'end_longitude': end['longitude'],
                         'end_elevation': end['elevation'],
                         'segment_length': distance,
                         'segment_elev_change': elevation_change
                         })
    with open(output_csv, mode='w', newline='') as csvfile:
        fieldnames = [
            'segment_number',
            'start_latitude', 'start_longitude', 'start_elevation',
            'end_latitude', 'end_longitude', 'end_elevation',
            'segment_length', 'segment_elev_change'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for segment in segments:
            writer.writerow(segment)

    print(f"Segments saved to: {output_csv}")


def coords_to_distance(lat1, lon1, lat2, lon2):
    # radius of the earth in m
    earth_radius = 6371000
        
    # distance between latitudes and longditudes in degrees
    latitude_distance = (lat2 - lat1)
    longitude_distance = (lon2 - lon1)

    # convert to distance in metres
    latitude_metres = ((2 * math.pi * earth_radius)/360) * latitude_distance
    longitude_metres = ((2 * math.pi * earth_radius)/360) * math.cos(lat1*math.pi/180) * longitude_distance

    # calculate the linear distance between the vectors
    linear_distance = math.sqrt(math.pow(latitude_metres, 2) + math.pow(longitude_metres, 2))
    return linear_distance


if __name__ == "__main__":
    main()

