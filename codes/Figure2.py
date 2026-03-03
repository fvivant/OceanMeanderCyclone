"""
Title: Figure 2
Description: Program to plot Figure 2 - Cyclone energetic response to ocean meanders

This script generates a 2x2 figure showing:
- Panel a: Eddy kinetic energy (EKE) and MSLP evolution
- Panel b: Diabatic production (GE) and Sea Surface Temperature
- Panel c: Conversion from Available Eddy Potential Energy (CE)
- Panel d: Baroclinic production (CA)

Author: Félix Vivant  
Institution: Laboratoire de Météorologie Dynamique - IPSL, ENS Paris  
Date: 2026-02-27  

Dependencies:  
- Python 3.8+
- Libraries: NumPy, xarray, matplotlib, xWRF
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

    print("=" * 70)
    print("Figure 2: Energy Budget Analysis")
    print("=" * 70)

    # =========================================================================
    # LOAD DATA
    # =========================================================================

    # Get simulation paths from config
    sims_config = SIMULATIONS['main']
    sim_names = ['CTL', 'M5', 'M10']
    
    # Build paths from config
    path = DATA_BASE_DIR
    rep = [sims_config[sim]['folder'] for sim in sim_names]

    color = ["k", "#0072B2", "#E69F00"]  
    style = ['-', '-', '-']
    names = sim_names

    # Rolling window parameter
    rol = 1
    
    # Load MSLP diagnostic files
    MSLP_files = [
        xr.open_dataset(path + rep[i] + DATA_FILES['MSLP']) for i in range(len(rep))
    ]

    # Load Lorenz energy budget data
    lorenz_budgets = [
        xr.open_dataset(path + rep[i] + DATA_FILES['Lorenz_budget_CycDom'])
        for i in range(len(rep))
    ]

    # Extract energy budget components
    EKE_box = [lorenz_budgets[i].EKE for i in range(len(rep))]
    GE_box = [lorenz_budgets[i].GE for i in range(len(rep))]  # Diabatic production
    CE_box = [lorenz_budgets[i].CE for i in range(len(rep))]  # Conversion from EAPE
    CA_box = [lorenz_budgets[i].CA for i in range(len(rep))]  # Baroclinic production

    # =========================================================================
    # FIGURE CONFIGURATION
    # =========================================================================

    # Convert figure size from cm to inches
    cm = 1 / 2.54
    figsize = (17 * cm, 11.5 * cm)

    # Font size for all text elements
    size = 8
    parameters = {
        'axes.labelsize': size,
        'axes.titlesize': size,
        'xtick.labelsize': size,
        'ytick.labelsize': size,
    }
    plt.rcParams.update(parameters)

    # Text and plot parameters
    tx, ty = 0.04, 0.94  # Text position (relative to axes)
    lw = 1.2  # Line width
    titlepad = 4.7  # Title padding
    l2 = [0, 1, 2]  # Index list for simulations


    # =========================================================================
    # CREATE FIGURE AND SUBPLOTS
    # =========================================================================

    fig = plt.figure(figsize=figsize)

    # Create 2x2 grid layout
    gs = gridspec.GridSpec(2, 2)
    gs.update(wspace=0.42, hspace=0.17)  # Spacing between panels

    # =========================================================================
    # PANEL A: Eddy Kinetic Energy (EKE) and MSLP
    # =========================================================================
    ax1 = plt.subplot(gs[0, 0])
    plt.setp(ax1.get_xticklabels(), visible=False)

    ax2 = ax1.twinx()
    plt.setp(ax2.get_xticklabels(), visible=False)
    ax2.text(
        tx,
        ty,
        r'\textbf{a}',
        zorder=1,
        #   weight="bold",
        size=size,
        horizontalalignment='center',
        verticalalignment='center',
        transform=ax1.transAxes,
        bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    for j in l2:
        # Convert time to hours since start
        EKE_box[j]["Time"] = convert_time_to_hours(EKE_box[j]["Time"])
        (EKE_box[j] * 1e-5).plot(ax=ax1,
                                 label=names[j],
                                 color=color[j],
                                 linestyle=style[j],
                                 linewidth=lw,
                                 alpha=1)
        # Convert MSLP time
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
    ax1.set_xlabel(" ")
    ax1.xaxis.set_minor_locator(ticker.FixedLocator([10, 30, 50, 70, 90, 110]))
    ax1.set_xticks([0, 20, 40, 60, 80, 100, 120])
    ax1.set_ylim(0, 4.5)
    ax2.set_ylabel("$\mathrm{SLP}_c$ [hPa]", labelpad=1)
    ax2.set_xlabel("")

    # =========================================================================
    # PANEL B: Diabatic Production (GE) and SST
    # =========================================================================
    ax1 = plt.subplot(gs[0, 1], sharex=ax1)
    plt.setp(ax1.get_xticklabels(), visible=False)

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
        # Convert time to hours since start
        GE_box[j]["Time"] = convert_time_to_hours(GE_box[j]["Time"])
        (GE_box[j][:]).plot(ax=ax1,
                            label=names[j],
                            color=color[j],
                            linestyle=style[j],
                            linewidth=lw,
                            alpha=1)

        # Plot SST anomaly
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
    ax1.set_xlabel(" ")
    ax1.set_ylim(0, 7.3)
    ax1.set_yticks([0, 1, 2, 3, 4, 5, 6, 7])

    # =========================================================================
    # PANEL C: Conversion from Available Potential Energy (CE)
    # =========================================================================
    ax1 = plt.subplot(gs[1, 0], sharex=ax1, sharey=ax1)
    ax1.text(
        tx,
        ty,
        r'\textbf{c}',
        size=size,
        ha='center',
        va='center',
        transform=ax1.transAxes,
        bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    # Convert time to hours since start and plot conversion energy data
    for j in l2:
        CE_box[j]["Time"] = convert_time_to_hours(CE_box[j]["Time"])
        (CE_box[j][:]).plot(ax=ax1,
                            label=names[j],
                            color=color[j],
                            linestyle=style[j],
                            linewidth=lw,
                            alpha=1)

    ax1.set_ylabel("$C_E$ [W~m$^{-2}$]")
    ax1.set_title("Conversion from $A_E$ to $K_E$", pad=titlepad)
    ax1.set_xlabel("Time [h]")

    # =========================================================================
    # PANEL D: Baroclinic Production (CA)
    # =========================================================================
    ax1 = plt.subplot(gs[1, 1], sharex=ax1, sharey=ax1)
    ax1.text(
        tx,
        ty,
        r'\textbf{d}',
        size=size,
        ha='center',
        va='center',
        transform=ax1.transAxes,
        bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    # Convert time to hours since start and plot baroclinic production energy data
    for j in l2:
        CA_box[j]["Time"] = convert_time_to_hours(CA_box[j]["Time"])
        (CA_box[j][:]).plot(ax=ax1,
                            label=names[j],
                            color=color[j],
                            linestyle=style[j],
                            linewidth=lw,
                            alpha=1)

    ax1.set_ylabel("$C_A$ [W~m$^{-2}$]")
    ax1.set_title("Baroclinic production", pad=titlepad)
    ax1.set_xlabel("Time [h]")

    # =========================================================================
    # SAVE FIGURE
    # =========================================================================
    
    output_path = os.path.join(PLOT_OUTPUT_DIR, 'Figure2.jpg')
    plt.savefig(output_path,
                format="jpg",
                dpi=500,
                bbox_inches='tight')
    
    print(f"Figure saved to: {output_path}")
    plt.close()