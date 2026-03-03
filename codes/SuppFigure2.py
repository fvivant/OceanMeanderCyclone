
"""
Title: Supplementary Figure 2
Description: Program to plot Supplementary Figure 2 - Idealized initial atmospheric state

This script generates a vertical profile showing mean zonal wind, potential temperature,
pressure perturbation, and wind perturbation fields.

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
import cmocean
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors
import os
import sys

# Add parent directory to path to import config
from config import DATA_BASE_DIR, SIMULATIONS, DATA_FILES, PLOT_OUTPUT_DIR

# Configure matplotlib to use LaTeX rendering
plt.rcParams.update({"text.usetex": True})

# =============================================================================
# FUNCTIONS
# =============================================================================
def ZSTAR(y, yjet=0, Zjet=8, Ztrop=10, Ly=1e3):
    """Calculate tropopause height as a function of latitude.
    
    Parameters
    ----------
    y : ndarray
        Meridional coordinate (km)
    yjet : float, optional
        Jet center position (km, default 0)
    Zjet : float, optional
        Tropopause height at jet center (km, default 8)
    Ztrop : float, optional
        Reference tropopause height (km, default 10)
    Ly : float, optional
        Meridional scale (km, default 1e3)
        
    Returns
    -------
    ndarray
        Tropopause height variation
    """
    B = 2 * Ly / 5
    trop = abs(Zjet - Ztrop) * np.tanh((yjet - y) / B)
    return trop


def p_prime_BUI2021(z, y, x, dp=-2e2, Zp=0e3, Hp=6e3, Rp=500e3):
    """Calculate pressure perturbation following Bui 2021 formulation.
    
    Computes a localized pressure perturbation centered at (y=0, x=0) with
    vertical structure, used for idealized perturbation experiments.
    
    Parameters
    ----------
    z : ndarray
        Vertical coordinate (m), shape must match y and x
    y : ndarray
        Meridional coordinate (m), shape must match z and x
    x : ndarray
        Zonal coordinate (m), shape must match z and y
    dp : float, optional
        Pressure perturbation amplitude (Pa, default -2e2)
    Zp : float, optional
        Vertical center of perturbation (m, default 0)
    Hp : float, optional
        Vertical half-width of perturbation (m, default 6e3)
    Rp : float, optional
        Horizontal radius of perturbation (m, default 500e3)
        
    Returns
    -------
    ndarray
        Pressure perturbation field (Pa), same shape as input
    """
    R2 = (x**2 + y**2) / Rp**2
    p_prime = np.zeros(np.shape(z))
    condi1 = np.logical_and(R2 < 1, z - Zp < Hp)
    condi = np.logical_and(condi1, -Hp < z - Zp)
    p_prime[condi] = (dp * np.cos(np.pi * (z[condi] - Zp) / (2 * Hp))**2 *
                      (1 - R2[condi])**3)
    return p_prime


# =============================================================================
# MAIN EXECUTION
# =============================================================================
if __name__ == "__main__":
    print("="*70)
    print("Supplementary Figure 2")
    print("="*70)

    # =========================================================================
    # LOAD DATA
    # =========================================================================
    # Get CTL simulation path from config
    sims_config = SIMULATIONS['main']
    ctl_folder = sims_config['CTL']['folder']
    
    path = os.path.join(DATA_BASE_DIR, ctl_folder)

    wrfin = xr.open_dataset(path + DATA_FILES['wrfinput']).isel(Time=0)

    # =========================================================================
    # FIGURE CONFIGURATION
    # =========================================================================
    cm = 1 / 2.54
    figsize = (12 * cm, 12 * cm)

    sfac = 12 / 9

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
    fig, ax = plt.subplots(figsize=figsize)
    dcolor = 0.02
    sec = 500

    # Destagger vertical coordinate
    Z_stag = (wrfin["PH"] + wrfin["PHB"]).isel(west_east=sec) / 9.81
    Z = 0.5 * (Z_stag.data[:-1] + Z_stag.data[1:])

    P = (wrfin["P"] + wrfin["PB"]).isel(west_east=sec)
    Rt = 6378e3
    y = ((wrfin["XLAT"] - 45) * np.pi * Rt / 180).isel(west_east=sec)
    Y, Z_2D = np.meshgrid(y.data, np.ones(np.shape(Z)[0]))

    # Destagger zonal wind
    U = 0.5 * (wrfin["U"].isel(west_east_stag=sec) + wrfin["U"].isel(west_east_stag=sec+1))
    theta = wrfin["T"].isel(west_east=sec).data

    # Calculate perturbations
    sec2 = 100
    Pp2 = p_prime_BUI2021(Z, Y, 0)
    Up = 0.5 * (wrfin["U"].isel(west_east_stag=sec2) + wrfin["U"].isel(west_east_stag=sec2+1)) - U

    # =========================================================================
    # PLOT FIELDS
    # =========================================================================
    cset1 = ax.contourf(Y * 1e-3, Z * 1e-3, U, levels=np.arange(5, 51, 5),
                        cmap="YlOrRd", extend='max')
    ax.plot(y * 1e-3, ZSTAR(y * 1e-3) + 8, color="b", linewidth=1.2 * sfac,
            linestyle='-.')

    # Potential temperature contours
    levels2 = np.arange(290, 571, 10)
    ax.contour(Y * 1e-3, Z * 1e-3, theta + 300, levels=levels2,
               linewidths=0.5 * sfac, colors="k", alpha=1)

    # Pressure perturbation contours
    levels4 = [-1.5, -1, -0.5]
    ax.contour(Y * 1e-3, Z * 1e-3, Pp2 * 1e-2, levels=levels4,
               linewidths=0.8 * sfac, colors="g", alpha=1)

    # Wind perturbation contours
    ax.contour(Y * 1e-3, Z * 1e-3, Up, levels=[-5, -4, -3, -2, 2, 3, 4, 5],
               linewidths=0.6 * sfac, colors="blue", alpha=1)

    # =========================================================================
    # ADD COLORBAR
    # =========================================================================
    pos1 = ax.get_position()
    cax = fig.add_axes([pos1.x0, pos1.y1 + dcolor, pos1.x1 - pos1.x0, dcolor])
    cbar2 = plt.colorbar(mappable=cset1, cax=cax, orientation="horizontal",
                         ticklocation='top', extend='max')
    cbar2.set_label("$\\overline{u}$ [m~s$^{-1}$]", labelpad=3.5)
    cbar2.ax.tick_params(labelsize=size)

    # =========================================================================
    # AXES SETTINGS
    # =========================================================================
    ax.set_ylim((0, 20))
    ax.set_xlim((-1000, 1000))
    ax.set_xlabel("$y$ [km]")
    ax.set_ylabel("$z$ [km]")

    # =========================================================================
    # SAVE FIGURE
    # =========================================================================
    output_path = os.path.join(PLOT_OUTPUT_DIR, 'SuppFigure2.jpg')
    plt.savefig(output_path, format="jpg", dpi=500, bbox_inches='tight')
    
    print(f"Saving figure to: {output_path}")
    plt.close()
