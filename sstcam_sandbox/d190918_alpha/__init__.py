
CUTS_GHOST = (
    "(baseline_mean < 11.88)"
    "&(charge_median < 11)"
    "&(size_tm_20 < 24.5)"
    "&(size_tm_40 < 14.5)"
)
CUTS_ONOFF_SOFT = CUTS_GHOST + (
    "&(tduration < 25)"
    "&(leakage2_intensity < 0.1)"
    "&(width < 0.2)"
    "&(length < 0.9)"
    "&(width*length/log(intensity) < 0.015)"
    "&(abs(skewness) < 2.1)"
)
CUTS_ONOFF_HARSH = CUTS_GHOST + (
    "&(tduration < 5)"
    "&(tgradient_error < 70)"
    "&(leakage2_intensity < 0.005)"
    "&(width*length/log(intensity) < 0.0045)"
)
CUTS_WOBBLE = CUTS_GHOST + (
    "&(tduration < 25)"
    "&(leakage1_intensity < 0.7)"
    "&(leakage2_intensity < 0.9)"
    "&(width < 0.2)"
    "&(width*length/log(intensity) < 0.015)"
    "&(abs(skewness) < 2.1)"
)
REGION_SIZE = 5.63



# CUTS_GHOST = (
#     "(baseline_mean < 11.88)"
#     "&(charge_median < 11)"
#     "&(size_tm_20 < 24.5)"
#     "&(size_tm_40 < 14.5)"
# )
# CUTS_ONOFF_SOFT = CUTS_GHOST + (
#     "&(tduration < 25)"
#     "&(leakage2_intensity < 0.1)"
#     "&(width < 0.2)"
#     "&(length < 0.9)"
#     "&(width*length/log(intensity) < 0.015)"
#     "&(abs(skewness) < 2.1)"
# )
# CUTS_ONOFF_HARSH = CUTS_GHOST + (
#     "&(tduration < 5)"
#     "&(tgradient_error < 70)"
#     "&(leakage2_intensity < 0.005)"
#     "&(width*length/log(intensity) < 0.0045)"
# )
# CUTS_WOBBLE = CUTS_GHOST + (
#     "&(tduration < 40)"
#     "&(leakage1_intensity < 0.7)"
#     "&(leakage2_intensity < 0.9)"
#     "&(width < 0.2)"
#     "&(width*length/log(intensity) < 0.015)"
#     "&(abs(skewness) < 2.1)"
# )
# REGION_SIZE = 5.63
