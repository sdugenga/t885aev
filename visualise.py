import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore

def main():
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

    print(f"Output plot to {output_file}.")


if __name__ == "__main__":
    main()