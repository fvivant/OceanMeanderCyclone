"""
Title: Supplementary Figure 5
Description: Program to plot Supplementary Figure 5 - Sensitivity to an opposite SST configuration

This script generates a 1x2 figure comparing energy budget analysis (EKE and diabatic production) 
for an opposite ocean meander configurations across three simulations (CTL, M5c, M10c).

Author: Félix Vivant  
Institution: Laboratoire de Météorologie Dynamique - IPSL, ENS Paris  
Date: 2026-02-27  

Dependencies:  
- Python 3.8+
- Libraries: NumPy, xarray, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import os
import sys

# Add parent directory to path to import config
from config import DATA_BASE_DIR, SIMULATIONS, DATA_FILES, PLOT_OUTPUT_DIR

# Configure matplotlib to use LaTeX rendering
plt.rcParams.update({"text.usetex": True})

# =============================================================================
# FUNCTIONS
# =============================================================================
def convert_time_to_hours(time_coord):
    """Convert xarray time coordinate to hours since start.
    
    Parameters
    ----------
    time_coord : xarray.DataArray
        Time coordinate array
        
    Returns
    -------
    xarray.DataArray
        Time in hours since the first timestamp
    """
    return (time_coord - time_coord[0]).astype('timedelta64[s]') / 3600



# =============================================================================
# MAIN EXECUTION
# =============================================================================
if __name__ == "__main__":

    print("="*70)
    print("Supplementary Figure 5")
    print("="*70)

    # =========================================================================
    # LOAD DATA
    # =========================================================================
    # Get simulation paths from config - CTL from main, M5/M10 from cold
    path = DATA_BASE_DIR
    
    # CTL from main configuration, M5/M10 from cold configuration
    rep = [
        SIMULATIONS['main']['CTL']['folder'],
        SIMULATIONS['cold']['M5_cold']['folder'],
        SIMULATIONS['cold']['M10_cold']['folder'],
    ]
    
    color = ["k", "#0072B2", "#E69F00"]
    style = ['-', '-', '-']
    names = ['CTL', "M5c", "M10c"]

    rol = 1
    MSLP_files = [
        xr.open_dataset(path + rep[i] + DATA_FILES['MSLP']) for i in range(len(rep))
    ]

    lorenz_budgets = [
        xr.open_dataset(path + rep[i] + DATA_FILES['Lorenz_budget_CycDom'])
        for i in range(len(rep))
    ]

    EKE_box = [lorenz_budgets[i].EKE for i in range(len(rep))]
    GE_box = [lorenz_budgets[i].GE for i in range(len(rep))]

    # =========================================================================
    # FIGURE CONFIGURATION
    # =========================================================================
    cm = 1 / 2.54
    figsize = (17 * cm, 5.5 * cm)

    size = 8
    parameters = {
        'axes.labelsize': size,
        'axes.titlesize': size,
        "axes.labelsize": size,
        "xtick.labelsize": size,
        "ytick.labelsize": size
    }
    plt.rcParams.update(parameters)

    l2 = [0, 1, 2]
    tx, ty = 0.04, 0.94
    lw = 1.2
    titlepad = 4.7

    # =========================================================================
    # CREATE FIGURE
    # =========================================================================
    fig = plt.figure(figsize=figsize)

    gs = gridspec.GridSpec(1, 2)
    gs.update(wspace=0.42, hspace=0.17)

    # =========================================================================
    # PANEL A: EKE and MSLP
    # =========================================================================
    ax1 = plt.subplot(gs[0])

    ax2 = ax1.twinx()
    ax2.text(
        tx,
        ty,
        r'\textbf{a}',
        zorder=1,
        size=size,
        ha='center',
        va='center',
        transform=ax1.transAxes,
        bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    for j in l2:
        EKE_box[j]["Time"] = convert_time_to_hours(EKE_box[j]["Time"])
        (EKE_box[j] * 1e-5).plot(ax=ax1,
                                 label=names[j],
                                 color=color[j],
                                 linestyle=style[j],
                                 linewidth=lw,
                                 alpha=1)
        MSLP_files[j]["Time"] = convert_time_to_hours(MSLP_files[j]["Time"])
        (MSLP_files[j].MSLP * 1e-2).plot(ax=ax2,
                                         label=names[j],
                                         color=color[j],
                                         linestyle='-.',
                                         linewidth=lw,
                                         alpha=1,
                                         zorder=0)

    ax1.legend(prop={'size': size}, loc="center left")
    ax1.set_ylabel("$K_E$ [$10^{5}$~J~m$^{-2}$]")
    ax1.set_title("Eddy kinetic energy", pad=titlepad)
    ax1.set_xlabel("Time [h]")
    ax1.xaxis.set_minor_locator(ticker.FixedLocator([10, 30, 50, 70, 90, 110]))
    ax1.set_xticks([0, 20, 40, 60, 80, 100, 120])
    ax1.set_ylim(0, 4.5)
    ax2.set_ylabel("$\mathrm{SLP}_c$ [hPa]", labelpad=1)
    ax2.set_xlabel("")

    # =========================================================================
    # PANEL B: GE and SST
    # =========================================================================
    ax1 = plt.subplot(gs[1], sharex=ax1)

    ax1.text(
        tx,
        ty,
        r'\textbf{b}',
        size=size,
        ha='center',
        va='center',
        transform=ax1.transAxes,
        bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    ax2 = ax1.twinx()
    plt.setp(ax2.get_xticklabels(), visible=False)

    for j in l2:
        GE_box[j]["Time"] = convert_time_to_hours(GE_box[j]["Time"])
        (GE_box[j][:]).plot(ax=ax1,
                            label=names[j],
                            color=color[j],
                            linestyle=style[j],
                            linewidth=lw,
                            alpha=1)

        (MSLP_files[j].underSST - 273).plot(ax=ax2,
                                            color=color[j],
                                            linewidth=1,
                                            alpha=1,
                                            linestyle="-.")

    ax2.set_ylabel("SST [°C]")
    ax2.set_xlabel("")
    ax2.set_ylim(-25, 22)
    ax2.set_yticks([5, 10, 15, 20])
    ax2.yaxis.set_label_coords(1.11, 0.8)

    ax1.set_ylabel("$G_E$ [W~m$^{-2}$]")
    ax1.set_title("Diabatic production", pad=titlepad)
    ax1.set_xlabel("Time [h]")
    ax1.set_ylim(0, 7.3)
    ax1.set_yticks([0, 1, 2, 3, 4, 5, 6, 7])

    # =========================================================================
    # SAVE FIGURE
    # =========================================================================
    output_path = os.path.join(PLOT_OUTPUT_DIR, 'SuppFigure5.jpg')
    plt.savefig(output_path, format="jpg", dpi=500, bbox_inches='tight')

    print(f"Saving figure to: {output_path}")
    plt.close()