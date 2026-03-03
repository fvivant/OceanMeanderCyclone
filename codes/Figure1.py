"""
Title: Figure 1
Description: Program to plot Figure 1 - Cyclone development over ocean meanders of varying size

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
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import cmocean
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
    """
    Plot a single panel with SST background, SLP field, and cyclone track.

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
    cset1 : matplotlib.contourf.ContourSet
        SLP field contourf object (for colorbar).
    cset2 : matplotlib.contourf.ContourSet
        SST contourf object (for colorbar).
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

    # Plot SLP field at forecast time (time2)
    xm = MSLP_file.x_MSLP.isel(Time=time2)
    # here we select a subset of the SLP field around the cyclone
    # to avoid plotting upstream and downstream anomalies
    field_i = field.isel(Time=time2).sel(x=slice(xm - 1e6, xm + 1e6))
    cset1 = axis.contourf(field_i.x * unit + x_offset,
                          field_i.y * unit,
                          field_i,
                          cmap=cmocean.cm.gray,
                          levels=np.arange(field_min, field_max + field_dlev,
                                         field_dlev),
                          extend="min",
                          alpha=field_alpha)

    # Plot SLP field at time2-24h
    xm = MSLP_file.x_MSLP.isel(Time=time2 - 24)
    field_i = field.isel(Time=time2 - 24).sel(x=slice(xm - 1e6, xm + 1e6))
    axis.contourf(field_i.x * unit + x_offset,
                  field_i.y * unit,
                  field_i,
                  cmap=cmocean.cm.gray,
                  levels=np.arange(field_min, field_max + field_dlev,
                                 field_dlev),
                  extend="min",
                  alpha=field_alpha)

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
                 linewidths=1.2)

    # Set axis limits and labels
    axis.set_ylim(-1.2/unit, 1.2/unit)
    axis.set_xlim(-6.5/unit + x_offset, 1/unit + x_offset)
    axis.set_xlabel(xlabel, labelpad=1)
    axis.set_ylabel(ylabel, labelpad=1)

    # Set minor tick locations
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
    print("Figure 1")
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

    rol = 1  # Rolling window parameter
    MSLP_files = [
        xr.open_dataset(path + rep[i] + DATA_FILES['MSLP']) for i in range(len(rep))
    ]

    # Extract SLP anomaly field and convert units (Pa to hPa)
    field_label = "SLP anomaly [hPa]"
    fields = [MSLP_files[i].eddy_SLPin * 1e-2 for i in range(len(rep))]

    # Convert time dimension from absolute time to hours since start
    for j in range(len(fields)):
        fields[j]["Time"] = (fields[j]["Time"] - fields[j]["Time"][0]
                             ).astype('timedelta64[s]') / 3600
        MSLP_files[j]["Time"] = (
            MSLP_files[j]["Time"] -
            MSLP_files[j]["Time"][0]).astype('timedelta64[s]') / 3600

    # =========================================================================
    # FIGURE CONFIGURATION
    # =========================================================================

    # Convert figure size from cm to inches
    cm = 1 / 2.54
    figsize = (17 * cm, 17 * cm)

    # Font size for all text elements
    size = 8
    parameters = {
        'axes.labelsize': size,
        'axes.titlesize': size,
        'xtick.labelsize': size,
        'ytick.labelsize': size,
    }
    plt.rcParams.update(parameters)

    # Text annotation and colorbar parameters
    tx, ty = 0.015, 0.95  # Text position (relative to axes)
    dcolor = 0.015  # Colorbar spacing

    # Plot parameters
    parameters = {
        "field_alpha": 1,        # SLP field transparency
        "field_label": field_label,
        "size": size,
        "sstmin": 5,             # Min SST for colormap (°C)
        "sstmax": 22,            # Max SST for colormap (°C)
        "sstdlev": 1,            # SST contour level spacing
        "sstalpha": 0.8,         # SST transparency
        "x_offset": 6e3,         # X-coordinate offset (m)
        "unit": 1e-3,            # Conversion factor to km
    }
    x_offset = parameters["x_offset"]
    unit = parameters["unit"]

    # Time indices for visualization
    time1, time2 = 1, 72  # Initial time and forecast time (hours)

    # Compute SLP anomaly range across all simulations
    maxi = max([fields[j].isel(Time=time2).max()
                for j in range(len(fields))]).values
    mini = min([fields[j].isel(Time=time2).min()
                for j in range(len(fields))]).values

    # Set SLP contour levels (hPa)
    parameters["field_min"] = np.round(mini)
    parameters["field_max"] = -3  # Fixed maximum for consistency
    parameters["field_dlev"] = 1  # Contour level spacing


    # =========================================================================
    # CREATE FIGURE AND SUBPLOTS
    # =========================================================================

    fig = plt.figure(figsize=figsize)

    # Create 3x1 grid layout
    gs = gridspec.GridSpec(3, 1)
    gs.update(hspace=0.15)  # Vertical spacing between panels

    # PANEL 1: Control simulation (CTL)
    ax1 = plt.subplot(gs[0])
    plt.setp(ax1.get_xticklabels(), visible=False)
    j = 0

    # Plot panel
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
    timei = 48  # Time index for domain box
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

    # PANEL 2: M5
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

    # PANEL 3: M10
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
    # ADD COLORBARS
    # =========================================================================

    # Get position of first panel for colorbar placement
    pos1 = plt.subplot(gs[0]).get_position()

    # SST colorbar (right side)
    cax = fig.add_axes([
        pos1.x0 + (pos1.x1 - pos1.x0) * 0.52, pos1.y1 + dcolor,
        (pos1.x1 - pos1.x0) * 0.48, dcolor
    ])
    cbar2 = plt.colorbar(mappable=cset2,
                         cax=cax,
                         orientation="horizontal",
                         ticklocation='top',
                         extend='max')
    cbar2.set_label("SST [°C]", labelpad=3.5)
    cbar2.ax.tick_params(labelsize=size)

    # SLP anomaly colorbar (left side)
    cax = fig.add_axes([
        pos1.x0, pos1.y1 + dcolor, (pos1.x1 - pos1.x0) * 0.48, dcolor
    ])
    cbar = plt.colorbar(mappable=cset1,
                        cax=cax,
                        orientation="horizontal",
                        ticklocation='top',
                        extend='min',
                        ticks=[-20, -15, -10, -5])
    cbar.set_label("SLP anomaly [hPa]", labelpad=3.5)
    cbar.ax.tick_params(labelsize=size)


    # =========================================================================
    # SAVE AND CLOSE
    # =========================================================================

    # Save figure as high-resolution JPG
    output_path = (PLOT_OUTPUT_DIR+'Figure1.jpg')
    plt.savefig(output_path,
                format="jpg",
                dpi=500,
                bbox_inches='tight')
    print(f"Figure saved to: {output_path}")

    plt.close()
