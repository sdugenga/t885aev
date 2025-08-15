import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore

def main():
    ### BELOW IS FOR ROUTE LEVEL ###
    '''
    
    route_a = pd.read_csv("data/results/route_a_detailed.csv")
    route_b = pd.read_csv("data/results/route_b_detailed.csv")
    route_c = pd.read_csv("data/results/route_c_detailed.csv")
    output_file = "plots/route/energy_distance_detailed.png"

    plt.figure(figsize=(10,6))
    plt.plot(route_a['cumulative_distance'] / 1000, route_a['cumulative_energy_J'] / 3600000, label='Route A')
    plt.plot(route_b['cumulative_distance'] / 1000, route_b['cumulative_energy_J']  / 3600000, label='Route B')
    plt.plot(route_c['cumulative_distance'] / 1000, route_c['cumulative_energy_J']  / 3600000, label='Route C')

    plt.title('Comparison of three routes using energy used over distance travelled')
    plt.xlabel('Distance (km)')
    plt.ylabel('Energy (kWh)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()
    

    ### BELOW IS FOR LANE LEVEL ###

    '''
    # Load your stitched simulation data
    stitched_df = pd.read_csv("data/results/stitched_data.csv")

    # Load UDDS reference data
    udds_df = pd.read_csv("data/processed/udds_processed.csv")

    output_file = "plots/lane/udds_vs_stitched_energy_distance.png"

    # Ensure both have the same column names for plotting
    # (adjust these names to match your actual CSV headers)
    # For example: 'cumulative_distance' in meters, 'cumulative_energy' in Joules
    x_sim = stitched_df['cumulative_distance'] / 1000  # convert to km
    y_sim = stitched_df['cumulative_energy']

    x_udds = udds_df['cumulative_distance'] / 1000
    y_udds = udds_df['cumulative_energy_J']

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(x_sim, y_sim, label='Simulated Route', linewidth=2)
    plt.plot(x_udds, y_udds, label='UDDS Reference', linewidth=2, linestyle='--')

    plt.xlabel("Distance (km)")
    plt.ylabel("Energy (kWh)")
    plt.title("Comparing simulation against UDDS journey by energy over distance")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print(f"Output plot to {output_file}.")


if __name__ == "__main__":
    main()