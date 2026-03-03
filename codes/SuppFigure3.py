"""
Title: Supplementary Figure 3
Description: Program to plot Supplementary Figure 3 - Upstream and Downstream Cyclone Development

This script generates a 3-panel figure comparing cyclone development across three simulations (CTL, M5, M10),
showing SST background, SLP anomalies, and cyclone tracking.

Author: Félix Vivant  
Institution: Laboratoire de Météorologie Dynamique - IPSL, ENS Paris  
Date: 2026-02-27  

Dependencies:  
- Python 3.8+
- Libraries: NumPy, xarray, matplotlib, cmocean
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import cmocean
import matplotlib.ticker as ticker
import os
import sys

# Add parent directory to path to import config
from config import DATA_BASE_DIR, SIMULATIONS, DATA_FILES, PLOT_OUTPUT_DIR

# Configure matplotlib to use LaTeX rendering
plt.rcParams.update({"text.usetex": True})

# =============================================================================
# PLOTTING FUNCTION
# =============================================================================


def plot(SST, field, MSLP_file, time, time2, axis, color, name, xlabel,
         ylabel, args=None):
    """Plot a single panel with SST background, SLP field, and cyclone track.

    Parameters
    ----------
    SST : xarray.DataArray
        Sea surface temperature data (in Kelvin).
    field : xarray.DataArray
        SLP anomaly field (in Pa).
    MSLP_file : xarray.Dataset
        MSLP tracking data with cyclone positions.
    time : int
        Time index for background SST field.
    time2 : int
        Time index for foreground SLP field.
    axis : matplotlib.axes.Axes
        Axes object to plot on.
    color : str
        Color for cyclone track line.
    name : str
        Panel label (e.g., 'a. CTL').
    xlabel : str
        X-axis label.
    ylabel : str
        Y-axis label.
    args : dict
        Configuration parameters including field_min, field_max, field_dlev,
        field_alpha, sstmin, sstmax, sstdlev, sstalpha, size, x_offset, unit.

    Returns
    -------
    tuple
        (cset1, cset2) - contour objects for colorbar creation
    """
    # Extract parameters from args dictionary
    field_max = args["field_max"]
    field_min = args["field_min"]
    field_dlev = args["field_dlev"]
    field_alpha = args["field_alpha"]
    sstmax = args["sstmax"]
    sstmin = args["sstmin"]
    sstdlev = args["sstdlev"]
    sstalpha = args["sstalpha"]
    size = args["size"]
    x_offset = args["x_offset"]
    unit = args["unit"]

    # Plot SST background (convert from K to °C)
    cset2 = axis.contourf(SST.x * unit + x_offset,
                          SST.y * unit,
                          (SST.isel(Time=time) - 273.15),
                          cmap="coolwarm",
                          alpha=sstalpha,
                          levels=np.arange(sstmin, sstmax + sstdlev, sstdlev),
                          extend='max')

    # Plot contour lines of SLP at background time
    field_i = field.isel(Time=time)
    axis.contour(
        field.x * unit + x_offset,
        field.y * unit,
        field_i,
        colors="k",
        levels=[-1.5, -1, -0.5],
        linewidths=1.2,
        alpha=1)

    # Plot SLP field contours at forecast time (time2)
    field_i = field.isel(Time=time2)
    cset1 = axis.contour(field_i.x * unit + x_offset,
                         field_i.y * unit,
                         field_i,
                         colors='k',
                         levels=np.arange(field_min, field_max + field_dlev,
                                        field_dlev),
                         extend="both",
                         alpha=field_alpha,
                         linewidths=0.8)

    # Plot cyclone track
    axis.plot(MSLP_file.x_MSLP.data * unit + x_offset,
              MSLP_file.y_MSLP.data * unit,
              c=color,
              linewidth=1.6,
              alpha=1)

    # Plot cyclone position markers at specific times
    axis.scatter(MSLP_file.x_MSLP.isel(Time=[24, 48, 72, 96]).data * unit + x_offset,
                 MSLP_file.y_MSLP.isel(Time=[24, 48, 72, 96]).data * unit,
                 facecolors='none',
                 edgecolors=color,
                 s=30,
                 linewidths=1.2,
                 zorder=2)

    # Set axis limits and labels
    axis.set_ylim(-1/unit, 1.4/unit)
    axis.set_xlim(-4/unit + x_offset, 3/unit + x_offset)
    axis.set_xlabel(xlabel, labelpad=1)
    axis.set_ylabel(ylabel, labelpad=1)
    axis.xaxis.set_minor_locator(
        ticker.FixedLocator(np.array([-5.5, -4.5, -3.5, -2.5, -1.5, -0.5, 0.5]) /
                           unit + x_offset))
    axis.yaxis.set_minor_locator(ticker.FixedLocator([-0.5, 0.5]))

    # Add text label with panel identifier
    axis.text(tx, ty, name, color=color, weight="bold", size=size,
              ha='left', va='top',
              transform=axis.transAxes,
              bbox=dict(boxstyle="round", facecolor="white",
                       edgecolor="black", pad=0.2))

    return cset1, cset2


# =============================================================================
# MAIN EXECUTION
# =============================================================================
if __name__ == "__main__":

    print("="*70)
    print("Supplementary Figure 3")
    print("="*70)

    # =========================================================================
    # LOAD DATA
    # =========================================================================
    # Get simulation paths from config
    sims_config = SIMULATIONS['main']
    sim_names = ['CTL', 'M5', 'M10']
    
    # Build paths from config
    path = DATA_BASE_DIR
    rep = [sims_config[sim]['folder'] for sim in sim_names]
    names1 = [DATA_FILES['wrfout']] * len(rep)

    # Visualization parameters
    color = ["k", "#0072B2", "#E69F00"]
    names = [r'\textbf{a. CTL}', r"\textbf{b. M5}", r"\textbf{c. M10}"]
    xlabel = ['', "", "$x$ [km]"]
    ylabel = ['$y$ [km]', "$y$ [km]", "$y$ [km]"]

    # Load WRF output and MSLP diagnostic files
    wrfouts = [
        xr.open_dataset(path + rep[i] + names1[i]) for i in range(len(names1))
    ]

    rol = 1
    MSLP_files = [
        xr.open_dataset(path + rep[i] + DATA_FILES['MSLP']) for i in range(len(rep))
    ]

    # Compute SLP anomaly
    field_label = "SLP anomaly [hPa]"
    fields = [(wrfouts[i].PSFC - wrfouts[i].PSFC.mean(dim="x")) * 1e-2 for i in range(len(rep))]

    # Convert time coordinates to hours since start
    for j in range(len(fields)):
        fields[j]["Time"] = (fields[j]["Time"] - fields[j]["Time"][0]
                             ).astype('timedelta64[s]') / 3600
        MSLP_files[j]["Time"] = (
            MSLP_files[j]["Time"] -
            MSLP_files[j]["Time"][0]).astype('timedelta64[s]') / 3600

    # =========================================================================
    # FIGURE CONFIGURATION
    # =========================================================================
    cm = 1 / 2.54
    figsize = (17 * cm, 17 * cm)

    size = 8
    parameters = {
        'axes.labelsize': size,
        'axes.titlesize': size,
        "axes.labelsize": size,
        "xtick.labelsize": size,
        "ytick.labelsize": size
    }
    plt.rcParams.update(parameters)

    tx, ty = 0.015, 0.95
    lw = 1.5
    dcolor = 0.015

    parameters = {
        "field_alpha": 1,
        "field_label": field_label,
        "size": size,
        "sstmin": 5,
        "sstmax": 22,
        "sstdlev": 1,
        "sstalpha": 0.8,
        "x_offset": 6e3,
        "unit": 1e-3,
    }
    x_offset = parameters["x_offset"]
    unit = parameters["unit"]

    # =========================================================================
    # COMPUTE FIELD LIMITS
    # =========================================================================
    time1, time2 = 1, 72

    maxi = max([fields[j].isel(Time=time2).max()
                for j in range(len(fields))]).values
    mini = min([fields[j].isel(Time=time2).min()
                for j in range(len(fields))]).values

    parameters["field_min"] = -22
    parameters["field_max"] = 3
    parameters["field_dlev"] = 1

    # =========================================================================
    # CREATE FIGURE
    # =========================================================================
    fig = plt.figure(figsize=figsize)

    gs = gridspec.GridSpec(3, 1)
    gs.update(hspace=0.1)

    # =========================================================================
    # PANEL A: CTL Simulation
    # =========================================================================
    ax1 = plt.subplot(gs[0])
    plt.setp(ax1.get_xticklabels(), visible=False)
    j = 0

    cset1, cset2 = plot(wrfouts[j].SST,
                        fields[j],
                        MSLP_files[j],
                        time1,
                        time2,
                        ax1,
                        color[j],
                        names[j],
                        xlabel[j],
                        ylabel[j],
                        args=parameters)

        # Add cyclone domain box (for first panel only)
    timei = 72  # Time index for domain box
    xm_box = MSLP_files[j].x_MSLP.isel(Time=timei).values * unit + x_offset
    ym_box = MSLP_files[j].y_MSLP.isel(Time=timei).values * unit
    box_width = 1e6 * unit  # half width actually --> 2000 km box

    # Draw domain box as a rectangle
    rect = mpatches.Rectangle(
        (xm_box - box_width, ym_box - box_width),  # (x, y) bottom-left corner
        width=2 * box_width,
        height=2 * box_width,
        linewidth=1.6,
        edgecolor='k',
        facecolor='none',
        linestyle='-.'
    )
    ax1.add_patch(rect)

    # =========================================================================
    # PANEL B: M5 Simulation
    # =========================================================================
    ax1 = plt.subplot(gs[1])
    plt.setp(ax1.get_xticklabels(), visible=False)
    j = 1

    cset1, cset2 = plot(wrfouts[j].SST,
                        fields[j],
                        MSLP_files[j],
                        time1,
                        time2,
                        ax1,
                        color[j],
                        names[j],
                        xlabel[j],
                        ylabel[j],
                        args=parameters)

    # =========================================================================
    # PANEL C: M10 Simulation
    # =========================================================================
    ax1 = plt.subplot(gs[2])
    j = 2

    cset1, cset2 = plot(wrfouts[j].SST,
                        fields[j],
                        MSLP_files[j],
                        time1,
                        time2,
                        ax1,
                        color[j],
                        names[j],
                        xlabel[j],
                        ylabel[j],
                        args=parameters)

    # =========================================================================
    # ADD COLORBAR
    # =========================================================================
    pos1 = plt.subplot(gs[0]).get_position()
    cax = fig.add_axes([
        pos1.x0 + (pos1.x1 - pos1.x0) * 0.52, pos1.y1 + dcolor,
        (pos1.x1 - pos1.x0) * 0.48, +dcolor
    ])
    cbar2 = plt.colorbar(mappable=cset2,
                         cax=cax,
                         orientation="horizontal",
                         ticklocation='top',
                         extend='max')
    cbar2.set_label("SST [°C]", labelpad=3.5)
    cbar2.ax.tick_params(labelsize=size)

    # =========================================================================
    # SAVE FIGURE
    # =========================================================================
    output_path = os.path.join(PLOT_OUTPUT_DIR, 'SuppFigure3.jpg')
    plt.savefig(output_path, format="jpg", dpi=500, bbox_inches='tight')

    print(f"Saving figure to: {output_path}")
    plt.close()
