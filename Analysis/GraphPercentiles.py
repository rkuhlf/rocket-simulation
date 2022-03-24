# TODO: Move this and several other things from analysis to visualization

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd


folder = "Analysis/LowerDragFlightMonteCarlo-Temporary"

def simulation_name_from_figures(row, target_folder=f"{folder}/MonteCarloFlightSimulations"):
    return f"{target_folder}/{int(row[0]) + 1}.csv"

def get_data_from_row(figures, row):
    df = pd.read_csv(simulation_name_from_figures(figures.iloc[row], f"{folder}/MonteCarloFlightSimulations"))
    # FIXME: Unit conversions should really be somewhere else
    df["altitude"] *= 3.28084
    df["velocity"] *= 3.28084
    df["acceleration"] *= 3.28084

    df["drag"] *= 0.22480894244319
    df["thrust"] *= 0.22480894244319

    df["CP"] /= 0.0254
    df["CG"] /= 0.0254
    df["custom CG"] /= 0.0254
    df["RASAero CP"] /= 0.0254

    diameter = 7 # in
    df["used stability"] = (df["CP"] - df["CG"]) / diameter
    df["accurate stability"] = (df["RASAero CP"] - df["custom CG"]) / diameter

    return df

if __name__ == "__main__":
    figures = pd.read_csv(f"{folder}/MonteCarloFlightData/finalOutput.csv")

    figures = figures.sort_values("Apogee")

    percentile5 = get_data_from_row(figures, 4)
    percentile17 = get_data_from_row(figures, 16)
    percentile50 = get_data_from_row(figures, 49)
    percentile83 = get_data_from_row(figures, 82)
    percentile95 = get_data_from_row(figures, 94)

    percentiles = [
        percentile5,
        percentile17,
        percentile50,
        percentile83,
        percentile95
    ]

    outlier_kwargs = {
        "linestyle": "dotted",
        "color": "#9ca1b6"
    }
    confident_kwargs = {
        "color": "#525666",
        "linestyle": "dashed",
    }
    percentile_kwargs = [
        {
            **outlier_kwargs,
            "label": "90%"
        },
        {
            **confident_kwargs,
            "label": "65%",
        },
        {
            "color": "#11191f",
            "label": "median"
        },
        confident_kwargs,
        outlier_kwargs,
    ]

    def plot_distribution(name, title="", axis_label=""):
        for i, percentile in enumerate(percentiles):
            plt.plot(percentile["time"], percentile[name], **percentile_kwargs[i])
        
        # plt.fill_between(, y3, y4, color='grey', alpha='0.5')

        x1 = percentile17["time"]
        x2 = percentile83["time"]
        y1 = percentile17[name]
        y2 = percentile83[name]

        plt.fill(
            np.append(x1, x2[::-1]),
            np.append(y1, y2[::-1]),
            color="#97a5c2",
            alpha=0.5
        )

        plt.xlabel("Time (s)")
        plt.ylabel(axis_label)
        plt.title(title)

        plt.legend()
        
        plt.tight_layout()
        plt.show()
    
    from Helpers.visualization import make_matplotlib_big
    make_matplotlib_big()

    plot_distribution("altitude", title="Distribution of Altitude", axis_label="Altitude (ft)")
    plot_distribution("velocity", title="Distribution of Velocity", axis_label="Velocity (ft/s)")
    plot_distribution("drag", title="Distribution of Drag", axis_label="Drag (lbs)")
    plot_distribution("thrust", title="Simulated Thrust Curves", axis_label="Thrust (lbs)")    
    # plot_distribution("used stability", title="OpenRocket Stability", axis_label="Used Stability (cal)")
    # plot_distribution("accurate stability", title="RASAero Stability", axis_label="Actual Stability (cal)")
    

    pass