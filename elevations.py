import csv
import requests

def main():
    input_csv = "data/raw/route_c.csv"
    output_csv = "data/elevations/route_c_elev.csv"

    api_url = "https://api.open-elevation.com/api/v1/lookup"

    coordinates = []
    with open(input_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            coordinates.append({'latitude': lat, 'longitude': lon})

    payload = {"locations": coordinates}

    response = requests.post(api_url, json=payload)
    response.raise_for_status()
    results = response.json()['results']

    with open(output_csv, mode='w', newline='') as csvfile:
        fieldnames = ['latitude', 'longitude', 'elevation']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for coord, result in zip(coordinates, results):
            writer.writerow({
                'latitude': coord['latitude'],
                'longitude': coord['longitude'],
                'elevation': result['elevation']
            })

    print(f"New file written: {output_csv}")

    
if __name__ == "__main__":
    main()