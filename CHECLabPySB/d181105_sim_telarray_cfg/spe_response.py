"""
Obtain the single photoelectron response for an SiPM. Can be used as an input
to sim_telarray after normalisation with Konrads script
"""
import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import numpy as np
from scipy.special import binom
from scipy.stats import norm
from IPython import embed
from matplotlib import pyplot as plt
import os


def sipm_enf(x, spe_sigma, opct, pap, dap):
    """
    SiPM formula from Gentile 2010
    http://adsabs.harvard.edu/abs/2010arXiv1006.3263G

    This implementation only considers the case for a 100% probability of a
    single inital fired microcell

    Parameters
    ----------
    x : ndarray
        X points to evaluate at
    spe_sigma : float
        Width of the single photoelectron peak
    opct : float
        Probability of optical crosstalk
    pap : float
        Probability of afterpulse
    dap : float
        Distance of afterpulse peak from main peak
    """
    n_peaks = 100
    N = np.arange(n_peaks)[:, None]
    K = np.arange(1, n_peaks)[:, None]

    # Probability of n fired microcells due to optical crosstalk
    pct = ((1 - opct) * np.power(opct, N - 1) * binom(N - 1, 0))[:, 0]

    sap = spe_sigma

    papk = np.power(1 - pap, N[:, 0])
    p0ap = pct * papk
    pap1 = pct * (1-papk) * papk

    pe_sigma = np.sqrt(K * spe_sigma ** 2)
    ap_sigma = np.sqrt(K * sap ** 2)

    signal = p0ap[K] * norm.pdf(x, K, pe_sigma)
    signal += pap1[K] * norm.pdf(x, K * (1.0-dap), ap_sigma)

    return signal.sum(0)


def main():
    description = ('Obtain the single photoelectron response for an SiPM. '
                   'Can be used as an input to sim_telarray after '
                   'normalisation with Konrads script')
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-o', '--output', dest='output_dir', action='store',
                        required=True,
                        help='Output directory for the files')
    parser.add_argument('--spe_sigma', dest='spe_sigma', action='store',
                        default=0.1, type=float,
                        help='Value for the standard deviation of the single '
                             'photoelectron peak')
    parser.add_argument('--opct', dest='opct', action='store', default=0.1,
                        type = float,
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
    spe_sigma = args.spe_sigma
    opct = args.opct
    pap = args.pap
    dap = args.dap

    print(
    """
    SPE Parameters: spe_sigma = {}
                    opct      = {}
                    pap       = {}
                    dap       = {}
    """.format(spe_sigma, opct, pap, dap)
    )

    x = np.linspace(0, 100, 1000)
    y = sipm_enf(x, spe_sigma, opct, pap, dap)
    gt = y > 1E-15
    x = x[gt]
    y = y[gt]

    # Resample
    x = np.linspace(x.min(), x.max(), 1000)
    y = sipm_enf(x, spe_sigma, opct, pap, dap)

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


if __name__ == '__main__':
    main()
