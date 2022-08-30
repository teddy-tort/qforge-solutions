"""
Print a number with uncertainty with proper sig figs

@author: Teddy Tortorici
"""
import numpy as np

pm = "\u00B1"       # plus minus symbol unicode


def print_uncertainty(value: float, uncertainty: float, units: str = None) -> str:
    """
    print a value with its uncertainty
    :param value: The value of the number
    :param uncertainty: the uncertainty of that number
    :param units: optional units to tack on
    :return: the string that was printed
    """
    # put uncertainty in scientific notation -> uncertainty = unc_sci_not * 10^unc_sci_not_order
    unc_sci_not = uncertainty / 10 ** int(np.floor(np.log10(uncertainty)))
    unc_sci_not_order = int(np.log10(uncertainty/unc_sci_not))
    if unc_sci_not_order < 0:   # if uncertainty is a decimal
        sig_fig = abs(unc_sci_not_order)        # use this many sig figs past the decimal
        if unc_sci_not < 2:                     # however, if the uncertainty starts with "1", take one more sig fig
            sig_fig += 1
        to_print = f"{value:.{sig_fig}f} {pm:s} {uncertainty:.{sig_fig}f}"
    elif uncertainty < 2:       # if uncertainty is 1.x then we need to do something unique
        to_print = f"{value:.1f} {pm:s} {uncertainty:.1f}"
    else:                       # if uncertainty is a whole number greater than 1
        # value = int(np.round(value))
        if unc_sci_not < 2:
            value = int(np.round(value * 10 ** -(unc_sci_not_order-1)) * 10 ** (unc_sci_not_order-1))
            uncertainty = int(np.round(unc_sci_not * 10) * 10 ** (unc_sci_not_order - 1))
        else:
            value = int(np.round(value * 10 ** -unc_sci_not_order) * 10 ** unc_sci_not_order)
            uncertainty = int(np.round(unc_sci_not) * 10 ** unc_sci_not_order)
        to_print = f"{value:d} {pm:s} {uncertainty:d}"
    if units is not None:
        to_print = f"({to_print:s}) {units:s}"
    print(to_print)
    return to_print


if __name__ == "__main__":
    print_uncertainty(72, 2.852)
