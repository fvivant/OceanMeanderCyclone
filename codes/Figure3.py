"""
Title: Figure 3
Description: Program to plot Figure 3 - Moisture supply and diabatic production over the warm side of a meander

This script generates a 2x2 figure showing water vapor budget components
and their relationship to thermodynamic forcing at different time snapshots.

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
import matplotlib.colors as mcolors
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


def meandre(x,
            phi,
            x0,
            ymax=400e3,
            lx=2000e3,
            nM=3):
    """Calculate meandering position based on sinusoidal meander formula.
    
    Represents the meridional position of the Gulf Stream meander as a function
    of zonal position following a cosine function with spatial damping.
    
    Parameters
    ----------
    x : ndarray
        Zonal coordinate (m)
    phi : float
        Phase offset for meander (rad)
    x0 : float
        Reference zonal position for meander origin (m)
    ymax : float, optional
        Maximum meridional amplitude (m, default 400e3)
    lx : float, optional
        Zonal wavelength of meander (m, default 2000e3)
    nM : int, optional
        Number of meander wavelengths to consider (default 3)
        
    Returns
    -------
    ndarray
        Meridional meander position at each x coordinate
    """
    ysst = ymax * np.cos((2 * np.pi * (x - x0) / lx + phi))
    ysst[(x - x0) / lx > nM / 2] = 0
    ysst[x < x0] = 0
    return ysst


def plot(field_1,
         field_2,
         field_3,
         field_4,
         U,
         V,
         MSLP_file,
         time,
         axis,
         color,
         name,
         xlabel,
         ylabel,
         showkey=False,
         args=None):
    """Plot function for Figure 3 panels
    
    Parameters
    ----------
    field_1 : xarray.Dataset
        Diabatic production field (GE) for filled contours
    field_2 : xarray.Dataset
        Latent heat flux field (LH) for secondary filled contours
    field_3 : xarray.Dataset
        Surface pressure field (PSFC) for contours
    field_4 : xarray.Dataset
        Vertically integrated water vapor content for contours
    U : xarray.Dataset
        Zonal component of water vapor flux (u-component)
    V : xarray.Dataset
        Meridional component of water vapor flux (v-component)
    MSLP_file : xarray.Dataset
        Mean sea level pressure file containing cyclone position (x_MSLP, y_MSLP)
    time : int
        Time index for data selection
    axis : matplotlib.axes.Axes
        Target axis for plotting
    color : str
        Color for title text
    name : str
        Panel label/title
    xlabel : str
        X-axis label
    ylabel : str
        Y-axis label
    showkey : bool, optional
        Whether to show vector legend (default False)
    args : dict, optional
        Configuration parameters including:
        - x_offset, unit: coordinate transformations
        - field_alpha, sstalpha: transparency values
        
    Returns
    -------
    tuple
        (cset1, cset2) - contourf objects for colorbar creation
    """

    xm, ym = MSLP_file.x_MSLP.isel(Time=time) * 1e-6, MSLP_file.y_MSLP.isel(
        Time=time) * 1e-6

    x_offset = args["x_offset"]
    unit = args["unit"]

    field_i = field_3.isel(Time=time).sel(
        x=slice((xm - 1) * 1e6, (xm + 1) *
                1e6)).sel(y=slice((ym - 1) * 1e6, (ym + 1) * 1e6))
    c = axis.contour(field_i.x * unit + x_offset,
                     field_i.y * unit,
                     field_i * 1e-2,
                     colors="k",
                     levels=[985, 990, 995, 996, 998, 1000],
                     linewidths=0.6,
                     alpha=1,
                     zorder=1)
    axis.clabel(c, fontsize=size-1)


    field_i = field_4.sel(
        x=slice((xm - 1) * 1e6, (xm + 1) *
                1e6)).sel(y=slice((ym - 1) * 1e6, (ym + 1) * 1e6))
    axis.contour(
                    field_i.x * unit + x_offset,
                    field_i.y * unit,
                    field_i,
                    colors="blueviolet",
                    linewidths=1.2,
                    levels=[14], 
                    alpha=1,
                    zorder=1)

    field_i = field_1
    divnorm = mcolors.TwoSlopeNorm(vcenter=10)
    cset1 = axis.contourf(field_i.x * unit + x_offset,
                          field_i.y * unit,
                          field_i.isel(Time=time),
                          cmap="RdBu_r",
                          levels=np.arange(50, 401, 50),
                          extend="max",
                          norm=divnorm,
                          alpha=1,
                          zorder=2)

    field_i = field_2
    cset2 = axis.contourf(field_i.x * unit + x_offset,
                          field_i.y * unit,
                          field_i.isel(Time=time),
                          cmap='GnBu',
                          levels=np.arange(100, 401, 50),
                        #   norm=divnorm,
                          extend="max",
                          alpha=0.75,
                          zorder=0.5)


    alphax = 6
    alphay = 6
    quiverscale = 7e3 #6 #4
    quiverwidth = 0.0035
    X, Y = np.meshgrid(U.x.data, U.y.data)

    q = axis.quiver(
        X[::alphax, ::alphay] * unit + x_offset,
        Y[::alphax, ::alphay] * unit,
        U.data[::alphax, ::alphay],
        V.data[::alphax, ::alphay],
        zorder=3,
        color="blueviolet",
        width=quiverwidth,
        scale=quiverscale,
    )

    if showkey:
        lkey = 400
        txq, tyq = 0.62, 0.95
        tt = axis.text(txq + 0.14,
                       tyq,
                       '______________________',
                       color='w',
                       weight="bold",
                       size=9,
                       horizontalalignment='center',
                       verticalalignment='center',
                       transform=axis.transAxes,
                       bbox=dict(boxstyle="round",
                                 fc="white",
                                 ec="black",
                                 pad=0.2))
        tt.set_zorder(3)
        qt = axis.quiverkey(q,
                            X=txq,
                            Y=tyq,
                            U=lkey,
                            label=str(lkey) + '~kg~m$^{-1}$~s$^{-1}$',
                            labelpos='E',
                            fontproperties={
                                'weight': 'bold',
                                'size': size-1
                            },
                            zorder=3)
        t = qt.text.set_zorder(3)

    axis.set_ylim( (ym - 1)/unit, (ym + 1)/unit )
    axis.set_xlim( (xm + x_offset*unit - 1)/unit , (xm + x_offset*unit + 1)/unit)

    axis.text(tx,
              ty,
              name,
              color=color,
              weight="bold",
              size=size,
              horizontalalignment='left',
              verticalalignment='top',
              transform=axis.transAxes,
              bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    return cset1, cset2


########################### MAIN #################################
if __name__ == "__main__":
    # Open Data from config ------------------
    
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
    xlabel = ['', "", "$x$ [$1000$ km]"]
    ylabel = ['$y$ [$1000$ km]', "$y$ [$1000$ km]", "$y$ [$1000$ km]"]

    wrfouts = [
        xr.open_dataset(path + rep[i] + names1[i]) for i in range(len(names1))
    ]

    rol = 1
    MSLP_files = [
        xr.open_dataset(path + rep[i] + DATA_FILES['MSLP']) for i in range(len(rep))
    ]

    lorenz_budgets = [
        xr.open_dataset(path + rep[i] + DATA_FILES['Lorenz_budget'])
        for i in range(len(rep))
    ]

    water_budgets = [
        xr.open_dataset(path + rep[i] + DATA_FILES['water_budget'])
        for i in range(len(rep))
    ]

    for j in range(len(MSLP_files)):
        MSLP_files[j]["Time"] = convert_time_to_hours(MSLP_files[j]["Time"])

    # =========================================================================
    # PLOTTING CONFIGURATION
    # =========================================================================

    cm = 1 / 2.54
    figsize = (17 * cm, 16 * cm)

    size = 8
    parameters = {
        'axes.labelsize': size,
        'axes.titlesize': size,
        "axes.labelsize": size,
        "xtick.labelsize": size,
        "ytick.labelsize": size
    }
    plt.rcParams.update(parameters)

    tx, ty = 0.03, 0.97
    lw = 1.5
    dcolor = 0.012
    p_levels = 700e2
    ip = 3


    parameters = {
        "field_alpha": 1,
        "size": size,
        "sstmin": 5,
        "sstmax": 22,
        "sstdlev": 1,
        "sstalpha": 0.8,
        "x_offset": 6e3,
        "unit": 1e-3,
    }

    # =========================================================================
    # CREATE FIGURE AND SUBPLOTS
    # =========================================================================
    print("="*70)
    print("Figure 3")
    print("="*70)
    
    fig = plt.figure(figsize=figsize)

    gs = gridspec.GridSpec(2, 2)
    gs.update(hspace=0.12)

    # =========================================================================
    # PANEL A: CTL at t=42h
    # =========================================================================
    time = 42

    ax1 = plt.subplot(gs[0, 0])
    j = 0

    # a mean velocity of 25 m/s is chosen to compute the relative moisture fluxes
    # as the instantaneous cyclone track speed is noisy
    ucyc = 25
    vcyc = 0

    FVAPx_rel = water_budgets[j].FVAPx_inp.isel(Time=time) - ucyc * water_budgets[j].QVAPOR_inp.isel(Time=time)
    FVAPy_rel = water_budgets[j].FVAPy_inp.isel(Time=time) - vcyc * water_budgets[j].QVAPOR_inp.isel(Time=time)

    # a rolling mean with a window of 10 grid points is applied on the vertically 
    # integrated water vapor content (QVAPOR_inp) to better represent cold and warm fronts
    rol = 10  
    
    cset1, cset2 = plot(lorenz_budgets[j].GE_intp,
                        wrfouts[j].LH,
                        wrfouts[j].PSFC,
                        water_budgets[j].QVAPOR_inp.isel(Time=time).rolling(x=rol, y=rol, center=True).mean(),
                        FVAPx_rel,
                        FVAPy_rel,
                        MSLP_files[j],
                        time,
                        ax1,
                        'k',
                        r"\textbf{a. " + names[j] + ", " + str(time) + " h}",
                        xlabel[j],
                        ylabel[j],
                        showkey=True,
                        args=parameters)

    ax1.hlines(0,
               -6 / parameters["unit"] + parameters["x_offset"],
               2 / parameters["unit"] + parameters["x_offset"],
               color=color[j],
               linewidth=1,
               alpha=1,
               linestyle="-.",
               zorder=0)

    ax1.set_ylabel("$y$ [km]")
    ax1.xaxis.set_minor_locator(ticker.FixedLocator([2250, 2750, 3250, 3750]))

    # =========================================================================
    # PANEL C: M10 at t=42h
    # =========================================================================
    
    ax1 = plt.subplot(gs[1, 0])
    j = 2


    FVAPx_rel = water_budgets[j].FVAPx_inp.isel(Time=time) - ucyc * water_budgets[j].QVAPOR_inp.isel(Time=time)
    FVAPy_rel = water_budgets[j].FVAPy_inp.isel(Time=time) - vcyc * water_budgets[j].QVAPOR_inp.isel(Time=time)

    cset1, cset2 = plot(lorenz_budgets[j].GE_intp,
                        wrfouts[j].LH,
                        wrfouts[j].PSFC,
                        water_budgets[j].QVAPOR_inp.isel(Time=time).rolling(x=rol, y=rol, center=True).mean(),
                        FVAPx_rel,
                        FVAPy_rel,
                        MSLP_files[j],
                        time,
                        ax1,
                        'k',
                        r"\textbf{c. " + names[j] + ", " + str(time) + " h}",
                        xlabel[j],
                        ylabel[j],
                        args=parameters)

    ax1.plot(
        wrfouts[j].LH.x * parameters["unit"] + parameters["x_offset"],
        meandre(
            wrfouts[j].LH.x + parameters["x_offset"], 3 * np.pi / 2, -5e6, ymax=500e3, lx=2000e3, nM=4)
        * parameters["unit"],
        c='k',
        linewidth=1,
        alpha=1,
        linestyle="-.",
        zorder=0)

    ax1.set_ylabel("$y$ [km]")
    ax1.set_xlabel("$x$ [km]")
    ax1.xaxis.set_minor_locator(ticker.FixedLocator([2250, 2750, 3250, 3750]))

    # =========================================================================
    # PANEL B: CTL at t=52h
    # =========================================================================
    time = 52
    
    ax1 = plt.subplot(gs[0, 1])
    j = 0

    FVAPx_rel = water_budgets[j].FVAPx_inp.isel(Time=time) - ucyc * water_budgets[j].QVAPOR_inp.isel(Time=time)
    FVAPy_rel = water_budgets[j].FVAPy_inp.isel(Time=time) - vcyc * water_budgets[j].QVAPOR_inp.isel(Time=time)

    cset1, cset2 = plot(lorenz_budgets[j].GE_intp,
                        wrfouts[j].LH,
                        wrfouts[j].PSFC,
                        water_budgets[j].QVAPOR_inp.isel(Time=time).rolling(x=rol, y=rol, center=True).mean(),
                        FVAPx_rel,
                        FVAPy_rel,
                        MSLP_files[j],
                        time,
                        ax1,
                        'k',
                        r"\textbf{b. " + names[j] + ", " + str(time) + " h}",
                        xlabel[j],
                        ylabel[j],
                        args=parameters)

    ax1.hlines(0,
               -6 / parameters["unit"] + parameters["x_offset"],
               2 / parameters["unit"] + parameters["x_offset"],
               color=color[j],
               linewidth=1,
               alpha=1,
               linestyle="-.",
               zorder=0)
    
    ax1.xaxis.set_minor_locator(ticker.FixedLocator([3250, 3750, 4250, 4750]))

    # =========================================================================
    # PANEL D: M10 at t=52h
    # =========================================================================
    
    ax1 = plt.subplot(gs[1, 1])
    j = 2

    FVAPx_rel = water_budgets[j].FVAPx_inp.isel(Time=time) - ucyc * water_budgets[j].QVAPOR_inp.isel(Time=time)
    FVAPy_rel = water_budgets[j].FVAPy_inp.isel(Time=time) - vcyc * water_budgets[j].QVAPOR_inp.isel(Time=time)
    
    parameters['xmax'] = -2e6 
    parameters['ymax'] = 1e6
    parameters['y1'] = -0.4e6
    parameters['y2'] = -0.15e6

    cset1, cset2 = plot(lorenz_budgets[j].GE_intp,
                        wrfouts[j].LH,
                        wrfouts[j].PSFC,
                        water_budgets[j].QVAPOR_inp.isel(Time=time).rolling(x=rol, y=rol, center=True).mean(),
                        FVAPx_rel,
                        FVAPy_rel,
                        MSLP_files[j],
                        time,
                        ax1,
                        'k',
                        r"\textbf{d. " + names[j] + ", " + str(time) + " h}",
                        xlabel[j],
                        ylabel[j],
                        args=parameters)

    ax1.plot(
        wrfouts[j].LH.x * parameters["unit"] + parameters["x_offset"],
        meandre(
            wrfouts[j].LH.x + parameters["x_offset"], 3 * np.pi / 2, -5e6, ymax=500e3, lx=2000e3, nM=4)
        * parameters["unit"],
        c='k',
        linewidth=1,
        alpha=1,
        linestyle="-.",
        zorder=0)


    ax1.set_xlabel("$x$ [km]")
    ax1.xaxis.set_minor_locator(ticker.FixedLocator([3250, 3750, 4250, 4750]))

    # =========================================================================
    # ADD COLORBARS
    # =========================================================================
    
    pos1 = plt.subplot(gs[1]).get_position()
    cax = fig.add_axes(
        [pos1.x0, pos1.y1 + dcolor, (pos1.x1 - pos1.x0) * 1, +dcolor])
    cbar2 = plt.colorbar(mappable=cset1,
                         cax=cax,
                         orientation="horizontal",
                         ticklocation='top',
                         extend='max')

    cbar2.set_label(r"Diabatic production [W~m$^{-2}$]",
                    labelpad=3.8)
    cbar2.ax.tick_params(labelsize=size)

    pos1 = plt.subplot(gs[0]).get_position()
    cax = fig.add_axes(
        [pos1.x0, pos1.y1 + dcolor, (pos1.x1 - pos1.x0) * 1, +dcolor])
    cbar = plt.colorbar(mappable=cset2,
                        cax=cax,
                        orientation="horizontal",
                        ticklocation='top',
                        extend='min')
    cbar.set_label("Surface latent heat flux [W~m$^{-2}$]", labelpad=3.8)
    cbar.ax.tick_params(labelsize=size)

    # =========================================================================
    # SAVE FIGURE
    # =========================================================================
    
    output_path = os.path.join(PLOT_OUTPUT_DIR, 'Figure3.jpg')
    
    plt.savefig(output_path,
                format="jpg",
                dpi=500,
                bbox_inches='tight')
    
    print(f"Figure saved to: {output_path}")
    plt.close()
