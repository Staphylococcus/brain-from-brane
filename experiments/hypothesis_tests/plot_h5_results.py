#!/usr/bin/env python3
"""
Generates plots for the H5 experiment results (CV vs. Defect Count).
"""

import matplotlib.pyplot as plt
import numpy as np # For potential future use, like cleaner array handling

def plot_h5_results():
    """Plots the CV vs. Defect Count for point and line defects from H5."""

    # Data from H5 experiment run (Defect Count, CV)
    # (Defect Type,Defect Count,Mean Exec Time (ms),CV)
    baseline_data = {
        "count": 0,
        "cv": 0.001469
    }

    point_defect_data = {
        "counts": [0, 1, 2, 3, 4, 5, 7, 10, 15, 20, 25, 50, 100, 125, 250],
        "cvs": [
            baseline_data["cv"], # CV for 0 defects
            0.003862,  # 1
            0.003111,  # 2
            0.004922,  # 3
            0.002808,  # 4
            0.008802,  # 5
            0.014612,  # 7
            0.006415,  # 10
            0.005031,  # 15
            0.001965,  # 20
            0.001869,  # 25
            0.008700,  # 50
            0.026460,  # 100
            0.001535,  # 125
            0.004217   # 250
        ]
    }

    line_defect_data = {
        "counts": [0, 1, 2, 3, 4, 5, 7, 10, 15, 20],
        "cvs": [
            baseline_data["cv"], # CV for 0 defects
            0.012528,  # 1
            0.001870,  # 2
            0.007122,  # 3
            0.015754,  # 4
            0.005227,  # 5
            0.005669,  # 7
            0.008953,  # 10
            0.003803,  # 15
            0.004788   # 20
        ]
    }

    plt.figure(figsize=(12, 7))

    # Plot Point Defects
    plt.plot(point_defect_data["counts"], point_defect_data["cvs"], marker='o', linestyle='-', label='Point Defects')

    # Plot Line Defects
    plt.plot(line_defect_data["counts"], line_defect_data["cvs"], marker='s', linestyle='--', label='Line Defects')

    plt.xlabel("Number of Defects (Count)")
    plt.ylabel("Coefficient of Variation (CV) of Execution Time")
    plt.title("H5: CV vs. Number of Defects (Point vs. Line)")
    
    # Use a log scale for X-axis if defect counts span many orders, but for now linear is fine
    # to see the low-count region clearly. Can adjust if needed.
    # plt.xscale('symlog') # Allows 0, good for defect counts if we had higher ranges
    # plt.yscale('log') # If CVs span many orders, but current values are fairly close

    # Highlight specific points of interest for line defects
    interesting_line_counts = [1, 4]
    for lc in interesting_line_counts:
        if lc in line_defect_data["counts"]:
            idx = line_defect_data["counts"].index(lc)
            plt.plot(lc, line_defect_data["cvs"][idx], marker='X', markersize=10, color='red', linestyle='none')
            plt.text(lc, line_defect_data["cvs"][idx] + 0.001, f'{line_defect_data["cvs"][idx]:.4f}', color='red')

    # Highlight point defect at count 100
    if 100 in point_defect_data["counts"]:
        idx = point_defect_data["counts"].index(100)
        plt.plot(100, point_defect_data["cvs"][idx], marker='P', markersize=10, color='purple', linestyle='none')
        plt.text(100, point_defect_data["cvs"][idx] + 0.001, f'{point_defect_data["cvs"][idx]:.4f}', color='purple')


    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.7)
    plt.tight_layout()

    # Save the plot
    plot_filename = "h5_cv_vs_defect_count.png"
    plt.savefig(plot_filename)
    print(f"Plot saved to {plot_filename}")

    # Display the plot (optional, works in some environments)
    # plt.show() 

if __name__ == "__main__":
    plot_h5_results() 