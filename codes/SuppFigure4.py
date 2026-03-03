"""
Title: Supplementary Figure 4
Description: Program to plot Supplementary Figure 4 - Sensitivity to a northward and southward shift of 100 km

This script generates a 2x2 figure comparing energy budget analysis (EKE and diabatic production) 
for two spatial configurations (North and South variants) across three simulations (CTL, M5, M10).

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
    print("Supplementary Figure 4")
    print("="*70)

    # =========================================================================
    # LOAD DATA 
    # =========================================================================
    # Get simulation paths from config - spatial configurations
    sims_config = SIMULATIONS['spatial']
    
    # Configuration setup
    path = DATA_BASE_DIR
    color = ["k", "#0072B2", "#E69F00"]
    style = ["-", "-", "-"]
    
    # North configuration
    sim_names_north = ['CTL_N', 'M5_N', 'M10_N']
    names_north = ['CTL+100km', "M5+100km", "M10+100km"]
    rep_north = [sims_config[sim]['folder'] for sim in sim_names_north]
    
    # South configuration
    sim_names_south = ['CTL_S', 'M5_S', 'M10_S']
    names_south = ['CTL-100km', "M5-100km", "M10-100km"]
    rep_south = [sims_config[sim]['folder'] for sim in sim_names_south]

    # Load north configuration data
    MSLP_files_north = [
        xr.open_dataset(path + rep_north[i] + DATA_FILES['MSLP']) for i in range(len(rep_north))
    ]

    lorenz_budgets_north = [
        xr.open_dataset(path + rep_north[i] + DATA_FILES['Lorenz_budget_CycDom'])
        for i in range(len(rep_north))
    ]

    EKE_box_north = [lorenz_budgets_north[i].EKE for i in range(len(rep_north))]
    GE_box_north = [lorenz_budgets_north[i].GE for i in range(len(rep_north))]

    # Load south configuration data
    MSLP_files_south = [
        xr.open_dataset(path + rep_south[i] + DATA_FILES['MSLP']) for i in range(len(rep_south))
    ]

    lorenz_budgets_south = [
        xr.open_dataset(path + rep_south[i] + DATA_FILES['Lorenz_budget_CycDom'])
        for i in range(len(rep_south))
    ]

    EKE_box_south = [lorenz_budgets_south[i].EKE for i in range(len(rep_south))]
    GE_box_south = [lorenz_budgets_south[i].GE for i in range(len(rep_south))]

    # =========================================================================
    # FIGURE CONFIGURATION
    # =========================================================================
    cm = 1 / 2.54
    figsize = (17 * cm, 11.5 * cm)

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

    gs = gridspec.GridSpec(2, 2)
    gs.update(wspace=0.42, hspace=0.17)

    # =========================================================================
    # PANEL A: North - EKE and MSLP
    # =========================================================================
    ax1 = plt.subplot(gs[0, 0])
    plt.setp(ax1.get_xticklabels(), visible=False)

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
        EKE_box_north[j]["Time"] = convert_time_to_hours(EKE_box_north[j]["Time"])
        (EKE_box_north[j] * 1e-5).plot(ax=ax1,
                                       label=names_north[j],
                                       color=color[j],
                                       linestyle=style[j],
                                       linewidth=lw,
                                       alpha=1)
        MSLP_files_north[j]["Time"] = convert_time_to_hours(MSLP_files_north[j]["Time"])
        (MSLP_files_north[j].MSLP * 1e-2).plot(ax=ax2,
                                               label=names_north[j],
                                               color=color[j],
                                               linestyle='-.',
                                               linewidth=lw,
                                               alpha=1,
                                               zorder=0)

    ax1.legend(prop={'size': size-2.5}, loc="center left")
    ax1.set_ylabel("$K_E$ [$10^{5}$~J~m$^{-2}$]")
    ax1.set_title("Eddy kinetic energy (North)", pad=titlepad)
    ax1.set_xlabel("")
    ax1.xaxis.set_minor_locator(ticker.FixedLocator([10, 30, 50, 70, 90, 110]))
    ax1.set_xticks([0, 20, 40, 60, 80, 100, 120])
    ax1.set_ylim(0, 4.5)
    ax2.set_ylabel("$\mathrm{SLP}_c$ [hPa]", labelpad=1)
    ax2.set_xlabel("")

    # =========================================================================
    # PANEL B: North - GE and SST
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
        GE_box_north[j]["Time"] = convert_time_to_hours(GE_box_north[j]["Time"])
        (GE_box_north[j][:]).plot(ax=ax1,
                                  label=names_north[j],
                                  color=color[j],
                                  linestyle=style[j],
                                  linewidth=lw,
                                  alpha=1)

        (MSLP_files_north[j].underSST - 273).plot(ax=ax2,
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
    ax1.set_title("Diabatic production (North)", pad=titlepad)
    ax1.set_xlabel("")
    ax1.set_ylim(0, 7.3)
    ax1.set_yticks([0, 1, 2, 3, 4, 5, 6, 7])

    # =========================================================================
    # PANEL C: South - EKE and MSLP
    # =========================================================================
    ax1 = plt.subplot(gs[1, 0])

    ax2 = ax1.twinx()
    ax2.text(
        tx,
        ty,
        r'\textbf{c}',
        zorder=1,
        size=size,
        ha='center',
        va='center',
        transform=ax1.transAxes,
        bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    for j in l2:
        EKE_box_south[j]["Time"] = convert_time_to_hours(EKE_box_south[j]["Time"])
        (EKE_box_south[j] * 1e-5).plot(ax=ax1,
                                       label=names_south[j],
                                       color=color[j],
                                       linestyle=style[j],
                                       linewidth=lw,
                                       alpha=1)
        MSLP_files_south[j]["Time"] = convert_time_to_hours(MSLP_files_south[j]["Time"])
        (MSLP_files_south[j].MSLP * 1e-2).plot(ax=ax2,
                                               label=names_south[j],
                                               color=color[j],
                                               linestyle='-.',
                                               linewidth=lw,
                                               alpha=1,
                                               zorder=0)

    ax1.legend(prop={'size': size-2.5}, loc="center left")
    ax1.set_ylabel("$K_E$ [$10^{5}$~J~m$^{-2}$]")
    ax1.set_title("Eddy kinetic energy (South)", pad=titlepad)
    ax1.set_xlabel("Time [h]")
    ax1.xaxis.set_minor_locator(ticker.FixedLocator([10, 30, 50, 70, 90, 110]))
    ax1.set_xticks([0, 20, 40, 60, 80, 100, 120])
    ax1.set_ylim(0, 4.5)
    ax2.set_ylabel("$\mathrm{SLP}_c$ [hPa]", labelpad=1)
    ax2.set_xlabel("")

    # =========================================================================
    # PANEL D: South - GE and SST
    # =========================================================================
    ax1 = plt.subplot(gs[1, 1], sharex=ax1)

    ax1.text(
        tx,
        ty,
        r'\textbf{d}',
        size=size,
        ha='center',
        va='center',
        transform=ax1.transAxes,
        bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    ax2 = ax1.twinx()
    plt.setp(ax2.get_xticklabels(), visible=False)

    for j in l2:
        GE_box_south[j]["Time"] = convert_time_to_hours(GE_box_south[j]["Time"])
        (GE_box_south[j][:]).plot(ax=ax1,
                                  label=names_south[j],
                                  color=color[j],
                                  linestyle=style[j],
                                  linewidth=lw,
                                  alpha=1)

        (MSLP_files_south[j].underSST - 273).plot(ax=ax2,
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
    ax1.set_title("Diabatic production (South)", pad=titlepad)
    ax1.set_xlabel("Time [h]")
    ax1.set_ylim(0, 7.3)
    ax1.set_yticks([0, 1, 2, 3, 4, 5, 6, 7])

    # =========================================================================
    # SAVE FIGURE
    # =========================================================================
    output_path = os.path.join(PLOT_OUTPUT_DIR, 'SuppFigure4.jpg')
    plt.savefig(output_path, format="jpg", dpi=500, bbox_inches='tight')

    print(f"Figure saved to: {output_path}")
    plt.close()