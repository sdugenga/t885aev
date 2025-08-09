import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore

def main():
    '''
    route_a = pd.read_csv("data/results/route_a_energy.csv")
    route_b = pd.read_csv("data/results/route_b_energy.csv")
    route_c = pd.read_csv("data/results/route_c_energy.csv")
    output_file = "plots/cumulative_energy.png"

    plt.figure(figsize=(10,6))
    plt.plot(route_a['cumulative_length'], route_a['cumulative_energy'], label='Route A')
    plt.plot(route_b['cumulative_length'], route_b['cumulative_energy'], label='Route B')
    plt.plot(route_c['cumulative_length'], route_c['cumulative_energy'], label='Route C')

    plt.title('Cumulative Energy vs Distance')
    plt.xlabel('Distance (m)')
    plt.ylabel('Energy (J)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()
    '''

    # Load your stitched simulation data
    stitched_df = pd.read_csv("data/results/stitched_data.csv")

    # Load UDDS reference data
    udds_df = pd.read_csv("data/processed/udds_processed.csv")

    output_file = "plots/udds_vs_stitched_speed_time.png"

    # Ensure both have the same column names for plotting
    # (adjust these names to match your actual CSV headers)
    # For example: 'cumulative_distance' in meters, 'cumulative_energy' in Joules
    x_sim = stitched_df['time_s'] / 1000  # convert to km
    y_sim = stitched_df['speed_ms']

    x_udds = udds_df['time_s'] / 1000
    y_udds = udds_df['speed_ms']

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(x_sim, y_sim, label='Simulated Route', linewidth=2)
    plt.plot(x_udds, y_udds, label='UDDS Reference', linewidth=2, linestyle='--')

    plt.xlabel("Time Elapsed (s)")
    plt.ylabel("Velocity (m/s)")
    plt.title("Speed vs Time")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print(f"Output plot to {output_file}.")


if __name__ == "__main__":
    main()