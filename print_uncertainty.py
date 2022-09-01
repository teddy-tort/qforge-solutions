"""
Print a number with uncertainty with proper sig figs

@author: Teddy Tortorici
"""
import numpy as np


def print_unc(value: float, uncertainty: float, units: str = None, sci_not: bool = False) -> str:
    """
    Print a number and its uncertainty with the proper amount of significant digits.
    :param value: the value of the number you are printing.
    :param uncertainty: the value of the uncertainty of the above value.
    :param units: optionally can pass in a string to tack on for the units of the number.
    :param sci_not: optionally can make this value True to put the number in scientific notation.
    :return: as well as printing, it will return the string value in case you'd like to store it and use it elsewhere
    """
    pm = "\u00B1"  # unicode for plus minus symbol

    if sci_not:
        superscript = ["\u2070", "\u00B9", "\u00B2", "\u00B3", "\u2074",
                       "\u2075", "\u2076", "\u2077", "\u2078", "\u2079"]
        divide_by = 10 ** int(np.floor(np.log10(value)))
        val_sci_not = value / divide_by
        val_sci_not_order = tuple(str(int(np.log10(value / val_sci_not))))
        unc_sci_not = uncertainty / divide_by
        unc_sci_not_sci_not = unc_sci_not / 10 ** int(np.floor(np.log10(unc_sci_not)))
        unc_sci_not_sci_not_order = int(np.log10(unc_sci_not / unc_sci_not_sci_not))
        if unc_sci_not_sci_not_order < 0:
            sig_fig = abs(unc_sci_not_sci_not_order)
            if unc_sci_not_sci_not < 2:
                sig_fig += 1
            print_string = f"({val_sci_not:.{sig_fig}f} {pm:s} {unc_sci_not:.{sig_fig}f}) * 10"
            for digit in val_sci_not_order:
                if digit == "-":
                    print_string += "\u207B"
                else:
                    print_string += superscript[int(digit)]
        if units is not None:
            print_string += " " + units

    else:
        # put uncertainty into scientific notation -> uncertainty = unc_sci_not * 10^unc_sci_not_order
        unc_sci_not = uncertainty / 10 ** int(np.floor(np.log10(uncertainty)))
        unc_sci_not_order = int(np.log10(uncertainty / unc_sci_not))
        if unc_sci_not_order < 0:  # if the uncertainty is a decimal, we have to treat the print a particular way.
            # the number of sig-figs will match the order of magnitude of the uncertainty
            sig_fig = abs(unc_sci_not_order)
            if unc_sci_not < 2:  # except if the first digit is 1, then we have one extra sig-fig
                sig_fig += 1
            print_string = f"{value:.{sig_fig}f} {pm:s} {uncertainty:.{sig_fig}f}"

        elif uncertainty < 2:  # if uncertainty is 1.x, the we need to print 1 sig fig passed the decimal
            print_string = f"{value:.1f} {pm:s} {uncertainty:.1f}"

        else:  # if uncertainty is a whole number, we have to truncate somewhere on the left side of the decimal
            if unc_sci_not < 2:  # if uncertainty starts with 1.
                value = int(np.round(value * 10 ** -(unc_sci_not_order - 1)) * 10 ** (unc_sci_not_order - 1))
                uncertainty = int(np.round(unc_sci_not * 10) * 10 ** (unc_sci_not_order - 1))
            else:
                value = int(np.round(value * 10 ** -unc_sci_not_order) * 10 ** unc_sci_not_order)
                uncertainty = int(np.round(unc_sci_not) * 10 ** unc_sci_not_order)
            print_string = f"{value:d} {pm:s} {uncertainty:d}"
        if units is not None:
            print_string = f"({print_string:s}) {units:s}"
    print(print_string)
    return print_string


if __name__ == "__main__":
    print_unc(0.001, 0.000004, units="m", sci_not=True)
