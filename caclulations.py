"""
Useful Calculations

author: Teddy Tortorici
"""

import numpy as np

h = 4.136               # eV fs
hbar = h / (2*np.pi)    # eV fs
c = 299.792             # nm/fs


def photon_energy(wavelenth: float) -> float:
    """returns photon energy in eV for a given wavelenth in nm"""
    return h * c / wavelenth


def convert_spherical(vector) -> np.ndarray:
    """Convert cartesian coordinates to spherical
    Input should be a list, tuple, or array of length 3"""
    x = vector[0]
    y = vector[1]
    z = vector[2]
    r = np.sqrt(x**2 + y**2 + z**2)
    polar = np.arccos(z / r)
    azimuthal = np.arctan(y / x)
    return np.array([r, polar, azimuthal])


def heisenberg_pair(uncertainty: float, variable: str) -> tuple:
    """Find the uncrtainty of a variable's uncertainty pair. Units are:
    nm for length,
    eV/c for momentum,
    eV for energy,
    fs for time
    """
    variable = variable.lower()
    conv = 1.
    if variable == 'c' or 'pos' in variable:
        pair = 'momentum'
        conv = c
    elif variable == 'p' or 'mom' in variable:
        pair = 'position'
        conv = c
    elif variable == 'e' or 'ene' in variable:
        pair = 'time'
    elif variable == 't' or 'tim' in variable:
        pair = 'energy'
    else:
        raise ValueError(f"Invalid variable name: {variable}.")
    uncertainty_pair = conv * hbar / (2. * uncertainty)
    return uncertainty_pair, pair
