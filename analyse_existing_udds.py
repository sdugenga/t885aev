import pandas as pd

def main():
    # load the data from a csv to a pandas dataframe
    dataframe = pd.read_csv("data/processed/udds_processed.csv")

    # variable for max acceleration if necessary
    max_acceleration = 1 # m/s/s

    # filter data for those rows that exceed the max accel
    exceeds_max_accel = dataframe[dataframe['acceleration_mss'] > max_acceleration]

    # filter the data for those rows which have non zero accel
    non_zero_accel = dataframe[dataframe['acceleration_mss'].abs() != 0]

    count_exceeded = len(exceeds_max_accel)
    count_non_zero = len(non_zero_accel)

    print(f"There are {count_non_zero} rows where acceleration is non zero")
    print(f"There are {count_exceeded} rows where max acceleration is exceeded:")
    print(exceeds_max_accel)


if __name__ == "__main__":
    main()