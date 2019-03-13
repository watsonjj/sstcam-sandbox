#include <math.h>
#include <iostream>


double poisson(int k, double lambda_)
/*
    Obtain the poisson PMF, using a definition that is mathematically
    equivalent but numerically stable to avoid arithmetic overflow.

    The result is the probability of observing k events for an average number
    of events per interval, lambda_.

    Source: https://en.wikipedia.org/wiki/Poisson_distribution
*/
{
    return exp(k * log(lambda_) - lambda_ - lgamma(k+1));
}


double normal_pdf(double x, double m, double s)
/*
    Obtain the normal PDF.

    The result is the probability of obseving a value at a position x, for a
    normal distribution described by a mean m and a standard deviation s.

    Source: https://stackoverflow.com/questions/10847007/using-the-gaussian-probability-density-function-in-c
*/
{
    static const double inv_sqrt_2pi = 0.3989422804014327;
    double a = (x - m) / s;
    return inv_sqrt_2pi / s * exp(-0.5f * a * a);
}


double binom(unsigned long n, unsigned long k) {
/*
    Obtain the binomial coefficient, using a definition that is mathematically
    equivalent but numerically stable to avoid arithmetic overflow.

    The result of this method is "n choose k", the number of ways choose an
    (unordered) subset of k elements from a fixed set of n elements.

    Source: https://en.wikipedia.org/wiki/Binomial_coefficient
*/
  return exp(lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1));
}


extern "C" void mapm(const double* x, double* s, size_t n, double norm, double eped, double eped_sigma, double spe, double spe_sigma, double lambda_)
{
    double p, pe_sigma;
    size_t k; //  Number of PMT avalanches
    bool found = false; // Found the values for which the probability is significant

    // Initialise the array to contain the pedestal peak, if it is significant
    double p_ped = exp(-lambda_);
    if (p_ped > 1e-5) {
        for (size_t i = 0; i < n; ++i) {
            s[i] = norm * p_ped * normal_pdf(x[i], eped, eped_sigma);
        }
    } else { // Set array to zero if pedestal peak is not significant
        for (size_t i = 0; i < n; ++i) {
            s[i] = 0.;
        }
    }

    // Loop over the possible total number of avalanches
    for (k = 1; k < 250; ++k) {
        p = poisson(k, lambda_); // Probability to get k avalanches

        // Skip this value of k if the resulting probability of getting k
        // total cells fired is very low
        if (!found && (p < 1e-5)) continue;
        if (found && p < 1e-5) break;
        found = true; // If line is reached, then significant peaks found

        // Combine spread of pedestal and pe peaks
        pe_sigma = sqrt(k * spe_sigma * spe_sigma + eped_sigma * eped_sigma);

        // Evaluate probability at each value of x
        for (size_t i = 0; i < n; ++i) {
            s[i] += norm * p * normal_pdf(x[i], eped + k * spe, pe_sigma);
        }
    }
}

extern "C" void sipm(const double* x, double* s, size_t n, double norm, double eped, double eped_sigma, double spe, double spe_sigma, double lambda_, double opct, double pap, double dap)
{
    double pj, pk, papk, p0ap, p1ap, ap_sigma, pe_sigma;
    double sap = spe_sigma; // Assume the sigma of afterpulses is the same
    size_t k; // Total number of cells fired
    size_t j; // Initial number of cells fired (before optical crosstalk)
    bool found = false; // Found the values for which the probability is significant

    // Initialise the array to contain the pedestal peak, if it is significant
    double p_ped = exp(-lambda_);
    if (p_ped > 1e-5) {
        for (size_t i = 0; i < n; ++i) {
            s[i] = norm * p_ped * normal_pdf(x[i], eped, eped_sigma);
        }
    } else { // Set array to zero if pedestal peak is not significant
        for (size_t i = 0; i < n; ++i) {
            s[i] = 0.;
        }
    }

    // Loop over the possible total number of cells fired
    for (k = 1; k < 250; ++k) {

        // Loop over the possible initial number of cells fired. Sum the
        // probability from the possible combinations which result in a
        // total of k fired cells to get the total probability of k fired cells
        pk = 0;
        for (j = 1; j <= k; ++j) {
            pj = poisson(j, lambda_); // Probability to get j initial fired cells
            if (pj < 1e-5) continue; // Skip if probability insignificant
            // Consider the contribution from optical crosstalk to give
            // additional fired cells
            pk += pj * pow(1-opct, j) * pow(opct, k-j) * binom(k-1, j-1);
        }
//        printf("%d %e\n", k, pk);

        // Skip this value of k if the resulting probability of getting k
        // total cells fired is very low
        if (!found && (pk < 1e-5)) continue;
        if (found && pk < 1e-5) break;
        found = true; // If line is reached, then significant peaks found

        // Consider probability of afterpulses
        papk = pow(1 - pap, k);
        p0ap = pk * papk; // Zero afterpulses
        p1ap = pk * (1-papk) * papk; // One afterpulse

        // Combine spread of pedestal and pe (and afterpulse) peaks
        pe_sigma = sqrt(k * spe_sigma * spe_sigma + eped_sigma * eped_sigma);
        ap_sigma = sqrt(k * sap * sap + eped_sigma * eped_sigma);

        // Evaluate probability at each value of x
        for (size_t i = 0; i < n; ++i) {
            s[i] += norm * p0ap * normal_pdf(x[i], eped + k * spe, pe_sigma);
            s[i] += norm * p1ap * normal_pdf(x[i], eped + k * spe * (1.0-dap), ap_sigma);
        }
    }
}
