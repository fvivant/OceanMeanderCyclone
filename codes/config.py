"""
Configuration File for Figure Generation

This module contains all configurable parameters for the figure generation scripts.
Modify these settings to adapt the code to your environment and data.

Author: Félix Vivant
Institution: Laboratoire de Météorologie Dynamique - IPSL, ENS Paris
Date: 2026-02-27
"""


# =============================================================================
# DATA PATHS - Extracted data
# =============================================================================
# DATA_BASE_DIR = "/lustre/fshomisc/home/rech/genlmd01/uyc88aq/WORK/1_paperstage/0_github/OceanMeanderCyclone/data"
# OUTPUT_PATH = "./output/"  # Relative path for GitHub portability

# # =============================================================================
# # EXTRACTED DATA FILES
# # =============================================================================

DATA_BASE_DIR = "./data/" # Data available in the zenodo repository
PLOT_OUTPUT_DIR = "your/desired/output/directory/"  # Update this to your desired output directory


SIMULATIONS = {
    'main': {  # Figures 1-4
        'CTL': {
            'folder': 'CTL/',
        },
        'M5': {
            'folder': 'M5/',
        },
        'M10': {
            'folder': 'M10/',
        },
    },
    'cold': {  # Supplementary Figure 5
        'M5_cold': {
            'folder': 'M5_cold/',
        },
        'M10_cold': {
            'folder': 'M10_cold/',
        },
    },
    'spatial': {  # Supplementary Figure 4 (North/South)
        'CTL_N': {
            'folder': 'CTL_100km_N/',

        },
        'M5_N': {
            'folder': 'M5_100km_N/',

        },
        'M10_N': {
            'folder': 'M10_100km_N/',

        },
        'CTL_S': {
            'folder': 'CTL_100km_S/',

        },
        'M5_S': {
            'folder': 'M5_100km_S/',

        },
        'M10_S': {
            'folder': 'M10_100km_S/',

        },
    },
}

# File names
DATA_FILES = {
    "wrfinput": "wrfinput.nc",
    "MSLP": "MSLP.nc",
    "wrfout": "wrfout.nc",
    "Lorenz_budget": "Lorenz_budget.nc",
    "Lorenz_budget_CycDom": "Lorenz_budget_CycDom.nc",
    "water_budget": "water_budget.nc",
    "water_budget_CycDom": "water_budget_CycDom.nc",
}

