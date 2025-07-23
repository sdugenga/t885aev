import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main():
    # vehicle design parameters from Julians spreadsheets etc.
    # this is just to generate power from the power equation
    parameters = {'max_velocity': convert_mph_ms(25),
                  'max_accel': 1,
                  'max_decel': 1,
                  'drag': 0.5,
                  'rolling_resistance': 0.03,
                  'mass': 1350,
                  'frontal_area': 2.646
                  }
    
    # load the data from a csv to a pandas dataframe
    dataframe = pd.read_csv("data/raw/uddscol.csv")

    # add a new column to the dataframe for speed capped at 25 mph
    dataframe['speed_mph_capped'] = dataframe['speed_mph'].clip(upper=25.0)
    # add another new column which converts the speeds to m/s
    dataframe['speed_ms'] = dataframe['speed_mph_capped'].apply(convert_mph_ms)
    # add another new column which gives the incremental distance per time step
    dataframe['incremental_distance'] = calculate_incremental_distance_m(dataframe['time_s'], dataframe['speed_ms'])
    # add column for cumulative distance covered
    dataframe['cumulative_distance'] = dataframe['incremental_distance'].cumsum()
    # add column for acceleration
    dataframe['acceleration_mss'] = calculate_acceleration(dataframe['time_s'], dataframe['speed_ms'])
    # add a columnn for power
    dataframe['power_W'] = calculate_power(dataframe['acceleration_mss'], dataframe['speed_ms'], parameters)
    # add a column for incremental energy
    dataframe['incremental_energy_J'] = calculate_incremental_energy(dataframe['time_s'], dataframe['power_W'])
    # add a column for cumulative energy
    dataframe['cumulative_energy_J'] = dataframe['incremental_energy_J'].cumsum()

    # Below plots a graph, but not ready for that yet
    '''
    # Plot the data
    plt.figure(figsize=(12, 6))  # make a bigger plot

    plt.plot(raw_data['time_s'], raw_data['speed_mph'], label='Uncapped Speed', color='blue')
    plt.plot(raw_data['time_s'], raw_data['speed_mph_capped'], label='Capped Speed', color='red')

    plt.xlabel('Time (s)')
    plt.ylabel('Speed (mph)')
    plt.title('Vehicle Speed: Uncapped vs. Capped at 25 mph')
    plt.legend()
    plt.grid(True)
    plt.savefig("plots/lane/udds_capped_compare.png", dpi=300)
    '''

    dataframe.to_csv("data/processed/udds_processed.csv")
    print(f"New file generated")


def convert_mph_ms(mph):
    metres_in_mile = 1609.344 # constant (source)
    seconds_in_hour = 3600 # s/h
    miles_per_second = mph/seconds_in_hour # miles/s
    metres_per_second = miles_per_second*metres_in_mile
    
    return metres_per_second


def calculate_incremental_distance_m(time_series, speed_series):
    time_differences = time_series.diff().fillna(0)
    incremental_distances = speed_series * time_differences
    return incremental_distances


def calculate_acceleration(time_series, speed_series):
    time_differences = time_series.diff().fillna(0)
    velocity_differences = speed_series.diff().fillna(0)
    acceleration = velocity_differences / time_differences
    return acceleration


def calculate_power(acceleration, velocity, parameters):
    # get the variables out of the parameters dict
    drag = parameters['drag']
    rolling_resistance = parameters['rolling_resistance']
    mass = parameters['mass']
    frontal_area = parameters['frontal_area']
    incline = 0 # set incline to zero for this
    
    power = 0.6125*frontal_area*drag*np.power(velocity, 3)+9.81*mass*velocity*(rolling_resistance+incline+0.107*acceleration)
    return power

def calculate_incremental_energy(time_series, power_series):
    time_differences = time_series.diff().fillna(0)
    incremental_energy = (time_differences * power_series).clip(lower=0)
    return incremental_energy


if __name__ == "__main__":
    main()