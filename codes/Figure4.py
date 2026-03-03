"""
Title: Figure 4
Description: Program to plot Figure 4 - Hovmoller Diagram and deep tropospheric response

This script generates a 4-panel figure showing vertical profiles over time:
- Panels a-c: Contours of EKE, water vapor flux, and diabatic production for each simulation
- Panel d: Sea surface temperature evolution with peak markers

Author: Félix Vivant  
Institution: Laboratoire de Météorologie Dynamique - IPSL, ENS Paris  
Date: 2026-02-27  

Dependencies:  
- Python 3.8+
- Libraries: NumPy, xarray, xWRF, matplotlib, cmocean
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.gridspec as gridspec
import os
import sys

# Add parent directory to path to import config
from config import DATA_BASE_DIR, SIMULATIONS, DATA_FILES, PLOT_OUTPUT_DIR

# Configure matplotlib to use LaTeX rendering
plt.rcParams.update({"text.usetex": True})

# =============================================================================
# FUNCTION
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
    print("Figure 4")
    print("="*70)

    # Get simulation paths from config
    sims_config = SIMULATIONS['main']
    sim_names = ['CTL', 'M5', 'M10']
    
    # Build paths from config
    path = DATA_BASE_DIR
    rep = [sims_config[sim]['folder'] for sim in sim_names]
    names1 = [DATA_FILES['wrfout']] * len(rep)

    color = ["k", "#0072B2", "#E69F00"]
    style = ['-', '-', '-']
    names = sim_names

    rol = 1
    SSTs = [
        xr.open_dataset(path + rep[i] + DATA_FILES['MSLP']) for i in range(len(rep))
    ]

    lorenz_budgets = [
        xr.open_dataset(path + rep[i] + DATA_FILES['Lorenz_budget_CycDom'])
        for i in range(len(rep))
    ]
    water_budgets = [
        xr.open_dataset(path + rep[i] + DATA_FILES['water_budget_CycDom'])
        for i in range(len(rep))
    ]

    g = 9.81  # multiply by g to get J/kg or W/kg
    EKE_box = [lorenz_budgets[i].EKE_p * g
               for i in range(len(rep))]  # Kinetic energy
    GE_box = [lorenz_budgets[i].GE_p * g
              for i in range(len(rep))]  # Diabatic production
    FVAP_box = [water_budgets[i].FVAPz_p
                for i in range(len(rep))]  # Vertical vapor flux rho.w.qv = -omega.qv/g

    SSTs = [
        xr.open_dataset(path + rep[i] + DATA_FILES['MSLP']).underSST - 273 for i in range(len(rep))
    ]

    cm = 1 / 2.54
    figsize = (17 * cm, 17 * cm)

    fig = plt.figure(figsize=figsize)

    gs = gridspec.GridSpec(4, 1, height_ratios=[3, 3, 3, 1.5])
    gs.update(wspace=0.4, hspace=0.12)

    size = 8
    parameters = {
        'axes.labelsize': size,
        'axes.titlesize': size,
        "axes.labelsize": size,
        "xtick.labelsize": size,
        "ytick.labelsize": size
    }
    plt.rcParams.update(parameters)

    l2 = [0, 2, 3]

    tx, ty = 0.018, 0.94
    lw = 1.5
    dcolor = 0.015
    levels_KE = np.arange(0, 100, 15)
    levels_GE = np.arange(-1.8, 1.95, 0.1)
    levels_FVAP = np.arange(0.75, 1.6, 0.25) * 1e-5
    linewidths = 0.7
    linewidths2 = 0.7
    labelpad = 5
    xlim = (0, None)
    cmap = "RdBu_r"
    dt_sst = 0

    # =========================================================================
    # PANEL A: CTL Simulation
    # =========================================================================
    
    j = 0
    ax1 = plt.subplot(gs[0, 0])
    plt.setp(ax1.get_xticklabels(), visible=False)
    ax1.text(
        tx,
        ty,
        r"\textbf{" + "a. " + names[j] + "}",
        #  weight="bold",
        size=size,
        color=color[0],
        horizontalalignment='left',
        verticalalignment='top',
        transform=ax1.transAxes,
        bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    #---------------------------------------------------------------
    fields = EKE_box
    fields[j]["Time"] = convert_time_to_hours(fields[j]["Time"])
    fields[j]["p"] = fields[j]["p"] * 1e-2

    c1 = (fields[j]).plot.contour(
        x="Time",
        y="p",
        ax=ax1,
        colors='k',  #cmocean.cm.matter,
        alpha=1,
        levels=levels_KE,
        linewidths=linewidths)
    ax1.clabel(c1, inline=1, fontsize=7)
    leg1, _ = c1.legend_elements()

    #---------------------------------------------------------------
    fields = FVAP_box
    fields[j]["Time"] = convert_time_to_hours(fields[j]["Time"])
    fields[j]["p"] = fields[j]["p"] * 1e-2

    c2 = (fields[j]).plot.contour(
        x="Time",
        y="p",
        ax=ax1,
        colors="darkcyan",  #cmocean.cm.matter,
        alpha=1,
        levels=levels_FVAP,
        linewidths=linewidths2,
        linestyles='-.')
    ax1.clabel(c2, inline=1, fontsize=7)
    leg2, _ = c2.legend_elements()

    #---------------------------------------------------------------
    fields = GE_box
    fields[j]["Time"] = convert_time_to_hours(fields[j]["Time"])
    fields[j]["p"] = fields[j]["p"] * 1e-2
    c = (fields[j] * 1e3).plot.contourf(
        x="Time",
        y="p",
        ax=ax1,
        cmap=cmap,  #cmap = 'seismic', 
        alpha=1,
        levels=levels_GE,
        add_colorbar=False,
        extend='both')

    pos1 = ax1.get_position()
    cax = fig.add_axes([
        pos1.x0, pos1.y1 + dcolor - 0.004, (pos1.x1 - pos1.x0) / 1.9,
        +dcolor - 0.004
    ])

    cbar = plt.colorbar(mappable=c,
                        cax=cax,
                        orientation="horizontal",
                        ticklocation='top',
                        ticks=[-1.5, -1, -0.5, 0, 0.5, 1, 1.5],
                        aspect=35)
    cbar.set_label("Diabatic production, $\overline{g_e}^\mathrm{cyc}$ [$10^{-3}$~W~kg$^{-1}$]",
                   labelpad=labelpad)

    ax1.set_xlabel(" ")
    ax1.set_ylabel("$p$ [hPa]")
    ax1.set_title(" ")
    ax1.set_xlim(xlim)
    ax1.set_ylim(950, 150)
    ax1.set_yticks([950, 800, 600, 400, 200])

    legend = ax1.legend([leg1[0], leg2[0]], [
        'Eddy kinetic energy, $\overline{k_e}^\mathrm{cyc}$ [J~kg$^{-1}$]',
        'Vertical water vapor flux [$10^{-5}$ kg~m$^{-2}$~s$^{-1}$]'
    ],
                        bbox_to_anchor=(1, 1.34),
                        ncols=1,
                        fontsize=size-1,
                        edgecolor='black')

    legend.get_frame().set_alpha(None)

    # =========================================================================
    # PANEL B: M5 Simulation
    # =========================================================================
    
    j = 1
    ax1 = plt.subplot(gs[1, 0], sharex=ax1, sharey=ax1)
    plt.setp(ax1.get_xticklabels(), visible=False)
    ax1.text(
        tx,
        ty,
        r"\textbf{" + "b. " + names[j] + "}",
        size=size,
        color='k',
        horizontalalignment='left',
        verticalalignment='top',
        transform=ax1.transAxes,
        bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    #---------------------------------------------------------------
    fields = EKE_box
    fields[j]["Time"] = convert_time_to_hours(fields[j]["Time"])
    fields[j]["p"] = fields[j]["p"] * 1e-2

    c = (fields[j]).plot.contour(
        x="Time",
        y="p",
        ax=ax1,
        colors='k',
        alpha=1,
        levels=levels_KE,
        linewidths=linewidths)
    ax1.clabel(c, inline=1, fontsize=7)
    leg3, _ = c.legend_elements()

    #---------------------------------------------------------------
    fields = FVAP_box
    fields[j]["Time"] = convert_time_to_hours(fields[j]["Time"])
    fields[j]["p"] = fields[j]["p"] * 1e-2

    c = (fields[j]).plot.contour(x="Time",
                                 y="p",
                                 ax=ax1,
                                 colors="darkcyan",
                                 alpha=1,
                                 levels=levels_FVAP,
                                 linewidths=linewidths2,
                                 linestyles='-.')
    ax1.clabel(c, inline=1, fontsize=7)
    leg3, _ = c.legend_elements()

    #---------------------------------------------------------------
    fields = GE_box
    fields[j]["Time"] = convert_time_to_hours(fields[j]["Time"])
    fields[j]["p"] = fields[j]["p"] * 1e-2

    (fields[j] * 1e3).plot.contourf(
        x="Time",
        y="p",
        ax=ax1,
        cmap=cmap,
        alpha=1,
        levels=levels_GE,
        add_colorbar=False)

    s_peaks = np.array([18, 31, 43, 58]) + dt_sst
    ax1.scatter(s_peaks,
                np.ones(len(s_peaks)) * fields[j].p.isel(p=0).data,
                color=color[1],
                marker='*',
                clip_on=False)

    ax1.set_xlabel(" ")
    ax1.set_ylabel("$p$ [hPa]")
    ax1.set_title(" ")
    ax1.set_ylim(950, 150)

    # =========================================================================
    # PANEL C: M10 Simulation
    # =========================================================================
    
    j = 2
    ax1 = plt.subplot(gs[2, 0], sharex=ax1, sharey=ax1)
    plt.setp(ax1.get_xticklabels(), visible=False)
    ax1.text(tx,
             ty,
             r"\textbf{" + "c. " + names[j] + "}",
             size=size,
             color='k',
             horizontalalignment='left',
             verticalalignment='top',
             transform=ax1.transAxes,
             bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    #---------------------------------------------------------------
    fields = EKE_box
    fields[j]["Time"] = convert_time_to_hours(fields[j]["Time"])
    fields[j]["p"] = fields[j]["p"] * 1e-2

    c = (fields[j]).plot.contour(x="Time",
                                 y="p",
                                 ax=ax1,
                                 colors='k',
                                 alpha=1,
                                 levels=levels_KE,
                                 linewidths=linewidths)
    ax1.clabel(c, inline=1, fontsize=7)
    leg3, _ = c.legend_elements()

    #---------------------------------------------------------------
    fields = FVAP_box
    fields[j]["Time"] = convert_time_to_hours(fields[j]["Time"])
    fields[j]["p"] = fields[j]["p"] * 1e-2

    c = (fields[j]).plot.contour(x="Time",
                                 y="p",
                                 ax=ax1,
                                 colors="darkcyan",
                                 alpha=1,
                                 levels=levels_FVAP,
                                 linewidths=linewidths2,
                                 linestyles='-.')
    ax1.clabel(c, inline=1, fontsize=7)
    leg3, _ = c.legend_elements()

    #---------------------------------------------------------------
    fields = GE_box
    fields[j]["Time"] = convert_time_to_hours(fields[j]["Time"])
    fields[j]["p"] = fields[j]["p"] * 1e-2

    (fields[j] * 1e3).plot.contourf(x="Time",
                                    y="p",
                                    ax=ax1,
                                    cmap=cmap,
                                    alpha=1,
                                    levels=levels_GE,
                                    add_colorbar=False)

    l_peaks = np.array([22, 47]) + dt_sst
    ax1.scatter(l_peaks,
                np.ones(len(l_peaks)) * fields[j].p.isel(p=0).data,
                color=color[2],
                marker='*',
                clip_on=False)

    ax1.set_xlabel(" ")
    ax1.set_ylabel("$p$ [hPa]")
    ax1.set_title(" ")
    ax1.set_ylim(950, 150)

    # =========================================================================
    # PANEL D: Sea Surface Temperature Evolution
    # =========================================================================
    
    ax1 = plt.subplot(gs[3, 0], sharex=ax1)
    ax1.text(
        tx,
        ty - 0.05,
        r"\textbf{" + "d. SSTs}",
        size=size,
        horizontalalignment='left',
        verticalalignment='top',
        transform=ax1.transAxes,
        bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    for j in range(len(color)):
        SSTs[j]["Time"] = convert_time_to_hours(SSTs[j]["Time"]) + dt_sst
        (SSTs[j]).plot(ax=ax1,
                       c=color[j],
                       label=names[j],
                       linestyle='-',
                       linewidth=1.2)

    ax1.scatter(s_peaks,
                SSTs[1].isel(Time=s_peaks - dt_sst),
                color=color[1],
                marker='*')
    ax1.scatter(l_peaks,
                SSTs[2].isel(Time=l_peaks - dt_sst),
                color=color[2],
                marker='*')

    ax1.set_xlabel("Time [h]")
    ax1.set_ylabel("SST [°C]")
    ax1.set_title(" ")
    ax1.legend(prop={'size': size}, loc="upper right", edgecolor='black')
    ax1.set_xticks(np.arange(0, 121, 10))
    ax1.set_yticks([5, 10, 15, 20])

    # =========================================================================
    # SAVE FIGURE
    # =========================================================================
    
    output_path = os.path.join(PLOT_OUTPUT_DIR, 'Figure4.jpg')
    
    plt.savefig(output_path,
                format="jpg",
                dpi=500,
                bbox_inches='tight')
    
    print(f"Saving figure to: {output_path}")

    plt.close()
