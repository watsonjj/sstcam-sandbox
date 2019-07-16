"""
Obtain the single photoelectron response for an SiPM. Can be used as an input
to sim_telarray after normalisation with Konrads script
"""
import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
from scipy.stats import norm
from matplotlib import pyplot as plt
import os
import numpy as np


def sipm_enf(x, spe, spe_sigma, opct, pap, dap):
    """
    SiPM formula from Gentile 2010
    http://adsabs.harvard.edu/abs/2010arXiv1006.3263G

    This implementation only considers the case for a 100% probability of a
    single inital fired microcell

    Parameters
    ----------
    x : ndarray
        X points to evaluate at
    spe : float
        Position of the single photoelectron peak
    spe_sigma : float
        Width of the single photoelectron peak
    opct : float
        Probability of optical crosstalk
    pap : float
        Probability of afterpulse
    dap : float
        Distance of afterpulse peak from main peak
    """
    sap = spe_sigma  # Assume the sigma of afterpulses is the same

    pe_signal = np.zeros(x.size)

    # Loop over the possible total number of cells fired
    for k in range(1, 250):
        pk = (1-opct) * pow(opct, k-1)

        # Consider probability of afterpulses
        papk = pow(1 - pap, k)
        p0ap = pk * papk
        pap1 = pk * (1-papk) * papk

        # Combine spread of pedestal and pe (and afterpulse) peaks
        pe_sigma = np.sqrt(k * spe_sigma ** 2)
        ap_sigma = np.sqrt(k * sap ** 2)

        # Evaluate probability at each value of x
        pe_signal += (
                p0ap * norm.pdf(x, k * spe, pe_sigma) +
                pap1 * norm.pdf(x, k * spe * (1 - dap), ap_sigma)
        )

    return pe_signal


def call(output_dir, spe, spe_sigma, opct, pap, dap):
    print(
        f"SPE Parameters:\n"
        f"\tspe       = {spe}\n"
        f"\tspe_sigma = {spe_sigma}\n"
        f"\topct      = {opct}\n"
        f"\tpap       = {pap}\n"
        f"\tdap       = {dap}\n"
    )

    x = np.linspace(0, 100, 1000)
    y = sipm_enf(x, spe, spe_sigma, opct, pap, dap)
    gt = y > 1E-15
    x = x[gt]
    y = y[gt]

    # Resample
    x = np.linspace(x.min(), x.max(), 1000)
    y = sipm_enf(x, spe, spe_sigma, opct, pap, dap)

    if not os.path.exists(output_dir):
        print("Creating directory: {}".format(output_dir))
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, "checs_spe_spectrum.txt")
    np.savetxt(output_path, np.column_stack((x, y, y)))
    print("Created config : {}".format(output_path))

    output_path = os.path.join(output_dir, "checs_spe_spectrum.pdf")
    plt.semilogy(x, y)
    plt.savefig(output_path, bbox_inches='tight')
    print("Created figure : {}".format(output_path))

    fadc_amplitude = np.average(x, weights=y)
    print(f"FADC_AMPLITUDE = {fadc_amplitude}")


def main():
    description = ('Obtain the single photoelectron response for an SiPM. '
                   'Can be used as an input to sim_telarray after '
                   'normalisation with Konrads script')
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-o', '--output', dest='output_dir', action='store',
                        required=True,
                        help='Output directory for the files')
    parser.add_argument('--spe', dest='spe', action='store',
                        default=1, type=float,
                        help='Position of the single photoelectron peak')
    parser.add_argument('--spe_sigma', dest='spe_sigma', action='store',
                        default=0.1, type=float,
                        help='Standard deviation of the single '
                             'photoelectron peak')
    parser.add_argument('--opct', dest='opct', action='store',
                        default=0.1, type=float,
                        help='Value for optical crosstalk')
    parser.add_argument('--pap', dest='pap', action='store', default=0,
                        type=float,
                        help='Value for the probability of afterpulses')
    parser.add_argument('--dap', dest='dap', action='store', default=0,
                        type=float,
                        help='Value for the distance of the afterpulse peak '
                             'from main peak')
    args = parser.parse_args()

    output_dir = args.output_dir
    spe = args.spe
    spe_sigma = args.spe_sigma
    opct = args.opct
    pap = args.pap
    dap = args.dap

    call(output_dir, spe, spe_sigma, opct, pap, dap)


if __name__ == '__main__':
    main()
