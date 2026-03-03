"""
Title: Supplementary Figure 1
Description: Program to plot Supplementary Figure 1 - Idealized SST fronts

This script generates a 2-panel figure showing:
- Panel a: Sea surface temperature as a function of distance from meander center
- Panel b: Meander geometry for three ocean configurations (CTL, M5, M10)

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
import os
import sys

# Add parent directory to path to import config
from config import DATA_BASE_DIR, SIMULATIONS, DATA_FILES, PLOT_OUTPUT_DIR

# Configure matplotlib to use LaTeX rendering
plt.rcParams.update({"text.usetex": True})

# =============================================================================
# FUNCTIONS
# =============================================================================
def ystar(x, lsst, xsst=-5e6, dxsst=4e6):
    """Calculate meridional position of ocean meander center.
    
    Computes the meridional displacement of a sinusoidal meander as a function
    of zonal position, with spatial damping outside the meander region.
    
    Parameters
    ----------
    x : ndarray
        Zonal coordinate (m)
    lsst : float
        Zonal wavelength of meander (m)
    xsst : float, optional
        Reference zonal position (m, default -5e6)
    dxsst : float, optional
        Zonal extent of meander region (m, default 4e6)
        
    Returns
    -------
    ndarray
        Meridional meander position at each x coordinate
    """
    ysst = 0.5 * lsst * np.sin((np.pi * (x - xsst) / lsst))
    ysst[x > xsst + dxsst] = 0
    ysst[x < xsst] = 0
    return ysst


def sst(y, ssteq=21, dsst=15, gsst=3e-5):
    """Calculate sea surface temperature as a function of meander-relative position.
    
    Models the SST profile across the Gulf Stream meander using a hyperbolic
    tangent function, with maximum temperature at the meander center.
    
    Parameters
    ----------
    y : ndarray
        Meridional distance from meander center (m)
    ssteq : float, optional
        Equilibrium SST at meander center (°C, default 21)
    dsst : float, optional
        SST amplitude across meander (°C, default 15)
    gsst : float, optional
        SST gradient parameter (default 3e-5)
        
    Returns
    -------
    ndarray
        Sea surface temperature in °C
    """
    arg_phi = 2 * (gsst / dsst) * y
    return ssteq - 0.5 * dsst * (1 + np.tanh(arg_phi))


plt.rcParams.update({"text.usetex": True})


# =============================================================================
# MAIN EXECUTION
# =============================================================================
if __name__ == "__main__":

    print("="*70)
    print("Supplementary Figure 1")
    print("="*70)

    # Get CTL simulation path from config
    sims_config = SIMULATIONS['main']
    ctl_folder = sims_config['CTL']['folder']
    
    path = os.path.join(DATA_BASE_DIR, ctl_folder)

    wrfin = xr.open_dataset(path + DATA_FILES['wrfinput']).isel(Time=0)

    cm = 1 / 2.54
    figsize = (12 * cm, 12 * cm)

    size = 8
    parameters = {
        'axes.labelsize': size,
        'axes.titlesize': size,
        "axes.labelsize": size,
        "xtick.labelsize": size,
        "ytick.labelsize": size
    }
    plt.rcParams.update(parameters)

    # =========================================================================
    # CREATE FIGURE
    # =========================================================================
    fig = plt.figure(figsize=figsize)

    gs = gridspec.GridSpec(2, 1)
    gs.update(hspace=0.3)
    
    # =========================================================================
    # PANEL A: SST Profile
    # =========================================================================
    ax1 = plt.subplot(gs[0])
    tx, ty = 0.04, 0.87
    ax1.text(
        tx,
        ty,
        r'\textbf{a}',
        zorder=1,
        size=size,
        horizontalalignment='center',
        verticalalignment='center',
        transform=ax1.transAxes,
        bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    y = np.linspace(-1e6, 1e6, 50)
    ax1.plot(y * 1e-3, sst(y), c='k', linewidth=1.5)
    ax1.set_yticks([5, 10, 15, 20])
    ax1.set_ylabel("SST [°C]")
    ax1.set_xlabel("$y-y^*(x)$ [km]")

    # =========================================================================
    # PANEL B: Meander Geometry
    # =========================================================================
    ax2 = plt.subplot(gs[1])
    ax2.text(
        tx,
        ty,
        r'\textbf{b}',
        zorder=1,
        size=size,
        horizontalalignment='center',
        verticalalignment='center',
        transform=ax2.transAxes,
        bbox=dict(boxstyle="round", fc="white", ec="black", pad=0.2))

    x = np.linspace(0e6, 7e6, 500)
    ax2.hlines(0, 0, 7e3, linewidth=1, color="k", label="$y^*_\mathrm{CTL}$")
    ax2.plot(x * 1e-3, ystar(x, 500e3, xsst=1e6, dxsst=4e6) * 1e-3,
             linewidth=1.2, c="#0072B2", label="$y^*_\mathrm{M5}$")
    ax2.plot(x * 1e-3, ystar(x, 1000e3, xsst=1e6, dxsst=4e6) * 1e-3,
             linewidth=1.2, c="#E69F00", label="$y^*_\mathrm{M10}$")
    ax2.legend(prop={'size': size}, loc="lower right")
    ax2.set_ylim(-1000, 1000)
    ax2.set_ylabel("$y$ [km]")
    ax2.set_xlabel("$x$ [km]")

    # =========================================================================
    # SAVE FIGURE
    # =========================================================================
    output_path = os.path.join(PLOT_OUTPUT_DIR, 'SuppFigure1.jpg')
    plt.savefig(output_path,
                format="jpg",
                dpi=500,
                bbox_inches='tight')
    
    print(f"Saving figure to: {output_path}")
    plt.close()
