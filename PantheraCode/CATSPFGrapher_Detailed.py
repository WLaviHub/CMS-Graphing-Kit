import json
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import sys
import os


JSON_FILE = "/home/pixels/Workspaces/Walker/CMS-Graphing-Kit/PantheraJSONs/statistics_Common_Assembly_Test_SecondPart_Fast.json"
PLOT_DIR = "/home/pixels/Workspaces/Walker/CMS-Graphing-Kit/PantheraPlots"
DATE = datetime.now().strftime("%-m-%-d-%y")
PLOT_FOLDER = f"{PLOT_DIR}/{DATE}_DetailedJsonPlots"
os.makedirs(PLOT_FOLDER, exist_ok=True)


#Enter modules you'd like to plot (Only TFPX 1x2 and 2x2 work for now)
MODULE_NAMES = [
    "SH0188", "SH0171", "SH0170", "SH0144", "SH0184",
    "SH0186", "SH0183", "SH0182", "SH0187", "SH0181",
    "SH0180", "SH0147", "SH0143", "SH0139", "SH0138",
]



def plot_iv(data, voltage=None):

    voltages = ["120", "100", "80", "25"]

    if voltage is None:

        print("\nAvailable IV voltages:")
        for i, v in enumerate(voltages, start=1):
            print(f"{i}. {v} V")
        print("5. All voltages")

        while True:
            selection = input("\nSelect voltage: ").strip()

            try:
                selection = int(selection)

                if selection == 5:
                    voltage = "all"
                    break

                voltage = voltages[selection - 1]
                break

            except (ValueError, IndexError):
                print("Invalid selection. Please enter 1, 2, 3, 4, or 5.")

    if voltage == "all":

        all_vals = {}
        all_negative_modules = {}

        for voltage in voltages:

            feature = f"IVCURVE_I_{voltage}"
            vals = []
            negative_modules = []

            for m in MODULE_NAMES:
                if m not in data:
                    continue

                try:
                    value = data[m]["actionable_summary"]["00_IVCurve_High"][feature]

                    if value < 0:
                        negative_modules.append(m)
                        continue

                    vals.append(value)

                except KeyError:
                    print(f"{m}: missing {feature}")

            all_vals[voltage] = vals
            all_negative_modules[voltage] = negative_modules

            if negative_modules:
                print(
                    f"\n{voltage} V - Modules: "
                    f"{', '.join(negative_modules)} "
                    f"were cut due to negative feature values."
                )

            print(
                f"{voltage} V - Found {len(vals)} module measurements."
            )

        if not any(all_vals.values()):
            print("No IV data found.")
            return

        max_value = max(
            max(vals)
            for vals in all_vals.values()
            if vals
        )

        bin_width = 0.05
        start = 0
        end = np.ceil(max_value / bin_width) * bin_width
        bins = np.arange(start, end + bin_width, bin_width)
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        axes = axes.flatten()

        for ax, voltage in zip(axes, voltages):

            vals = all_vals[voltage]

            if not vals:
                ax.set_title(f"Leakage Current ({voltage} V)")
                ax.text(
                    0.5,
                    0.5,
                    "No data available",
                    ha="center",
                    va="center",
                    transform=ax.transAxes
                )
                continue

            counts, _, _ = ax.hist(
                vals,
                bins=bins,
                edgecolor="black"
            )

            ax.set_ylim(0, max(counts) * 1.2)
            ax.set_xlim(0, max(bins) * 1.2)
            ax.set_xlabel(f"Leakage Current at {voltage} V (μA)")
            ax.set_ylabel("Modules")
            ax.yaxis.set_major_locator(
                ticker.MultipleLocator(1)
            )
            ax.set_title(f"Leakage Current ({voltage} V)")
            ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig(
            f"{PLOT_FOLDER}/IV_Combo.png",
            dpi=300
        )
        plt.close()

        return

    feature = f"IVCURVE_I_{voltage}"
    vals = []
    negative_modules = []

    for m in MODULE_NAMES:
        if m not in data:
            continue

        try:
            value = data[m]["actionable_summary"]["00_IVCurve_High"][feature]

            if value < 0:
                negative_modules.append(m)
                continue

            vals.append(value)

        except KeyError:
            print(f"{m}: missing {feature}")

    if negative_modules:
        print(
            f"Modules: {', '.join(negative_modules)} "
            f"were cut due to negative feature values."
        )

    if not vals:
        print("No IV data found.")
        return

    print(f"\nFound {len(vals)} module measurements.")

    bin_width = 0.05
    start = 0
    end = np.ceil(max(vals) / bin_width) * bin_width

    bins = np.arange(
        start,
        end + bin_width,
        bin_width
    )

    fig, ax = plt.subplots(
        figsize=(12, 8)
    )

    counts, bins, _ = ax.hist(
        vals,
        bins=bins,
        edgecolor="black"
    )

    ax.set_ylim(0, max(counts) * 1.2)
    ax.set_xlim(0, max(bins) * 1.2)
    ax.set_xlabel(f"Leakage Current at {voltage} V (μA)")
    ax.set_ylabel("Modules")
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.set_title(f"Leakage Current ({voltage} V)")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        f"{PLOT_FOLDER}/IV_{voltage}V.png",
        dpi=300
    )
    plt.close()


def plot_disconnected_bumps(data):
    test = "10_OpenBumpTest"
    thresh = 600

    features = ["CROSSTALK_N_DISCONNECTEDBUMPS_12", "CROSSTALK_N_DISCONNECTEDBUMPS_13",]

    has_sh = any(m.startswith("SH") for m in MODULE_NAMES)
    if has_sh:
        features = ["CROSSTALK_N_DISCONNECTEDBUMPS_12", "CROSSTALK_N_DISCONNECTEDBUMPS_13",
                    "CROSSTALK_N_DISCONNECTEDBUMPS_14", "CROSSTALK_N_DISCONNECTEDBUMPS_15"]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for ax, feature in zip(axes, features):
        labels = []
        vals = []

        for m in MODULE_NAMES:
            if m not in data:
                continue

            try:
                vals.append(
                    data[m]["actionable_summary"][test][feature]
                )
                labels.append(m)

            except KeyError:
                if feature.endswith("_14") or feature.endswith("_15"):
                    continue

                print(f"{m}: missing {feature}")

        chip = feature[-2:]
        ax.bar(labels, vals)
        vals = [1 if v == 0 else v for v in vals]
        ax.axhline(
            thresh,
            color="red",
            linestyle="--",
            label=f"Threshold ({thresh})"
        )
        ax.set_yscale("log")
        ax.set_ylim(1, 1500)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=90, fontsize=8)
        ax.set_xlabel("Module")
        ax.set_ylabel("Disconnected Bumps")
        ax.set_title(f"Disconnected Bumps (Chip {chip})")
        ax.grid(axis="y", alpha=0.3)
        ax.legend(loc="upper right", bbox_to_anchor=(1, 1.1))

    plt.tight_layout()
    plt.savefig(f"{PLOT_FOLDER}/DisconnectedBumps.png", dpi=300, bbox_inches="tight")
    plt.close()


def plot_masked_pixels(data, threshold = None):

    thresholds = {
        "2000": "06_NoiseScan_Th2000",
        "1200": "11_NoiseScan_Th1200",
        "1000": "16_NoiseScan_Th1000",
        "950": "20_NoiseScan_Th950",
        "900": "22_NoiseScan_Th900",
        "850": "24_NoiseScan_Th850"
    }

    threshold_list = list(thresholds.keys())

    if threshold is None:
        print("\nAvailable thresholds:")
        for i, threshold in enumerate(threshold_list, start=1):
            print(f"{i}. {threshold}")

        while True:
            selection = input("\nSelect threshold: ").strip()

            try:
                threshold = threshold_list[int(selection) - 1]
                break

            except (ValueError, IndexError):
                print(
                    f"Invalid selection. Please enter a number from "
                    f"1 to {len(threshold_list)}."
                )

    test = thresholds[threshold]

    features = ["NOISE_NUM_MASKED_PIXELS_12", "NOISE_NUM_MASKED_PIXELS_13"]


    has_sh = any(m.startswith("SH") for m in MODULE_NAMES)

    if has_sh:
        features = [
            "NOISE_NUM_MASKED_PIXELS_12", "NOISE_NUM_MASKED_PIXELS_13",
            "NOISE_NUM_MASKED_PIXELS_14", "NOISE_NUM_MASKED_PIXELS_15"]

    chip_pixels = 432 * 336
    fail = 0.01 * chip_pixels
    warn = 0.005 * chip_pixels

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for ax, feature in zip(axes, features):
        labels = []
        vals = []

        for module in MODULE_NAMES:
            if module not in data:
                continue

            try:
                vals.append(
                    data[module]["actionable_summary"][test][feature]
                )
                labels.append(module)

            except KeyError:
                print(f"{module}: missing {feature}")

        chip = feature[-2:]
        ax.bar(labels, vals)
        ax.set_yscale("log")
        ax.set_ylim(1, 2000)
        ax.axhline(
            fail,
            color="red",
            linestyle="--",
            label=f"FAIL 1.0% ({fail:.0f}px)"
        )
        ax.axhline(
            warn,
            color="orange",
            linestyle=":",
            label=f"WARN 0.5% ({warn:.0f}px)"
        )
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(
            labels,
            rotation=90,
            fontsize=8
        )
        ax.set_xlabel("Module")
        ax.set_ylabel("Masked Pixels")
        ax.set_title(f"Masked Pixels (Threshold {threshold}, Chip {chip})")
        ax.grid(axis="y", alpha=0.3)
        ax.legend(loc="upper right", bbox_to_anchor=(1, 1.2))

    plt.tight_layout()
    plt.savefig(
        f"{PLOT_FOLDER}/MaskedPixels_Th{threshold}.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()


with open(JSON_FILE) as f:
    data=json.load(f)

missing=[m for m in MODULE_NAMES if m not in data]
if missing:
    print("The following modules were not found:")
    print(", ".join(missing))
    if input("Do you still want to proceed? (y/n): ").strip().lower()!="y":
        sys.exit()

print("Available tests:")
print("1. IV Curve")
print("2. Disconnected Bumps")
print("3. Masked Pixels")
print("4. All tests")

sel = input("Enter the number corresponding to the desired test: ").strip()

if sel == "1":
    plot_iv(data)

elif sel == "2":
    plot_disconnected_bumps(data)

elif sel == "3":
    plot_masked_pixels(data)

elif sel == "4":

    for voltage in ["120", "100", "80", "25"]:
        plot_iv(data, voltage)

    plot_iv(data, "all")

    plot_disconnected_bumps(data)

    for threshold in ["2000", "1200", "1000", "950", "900", "850"]:
        plot_masked_pixels(data, threshold)

else:
    print("Invalid selection. Exiting.")
    sys.exit()
