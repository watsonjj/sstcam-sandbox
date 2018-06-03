import os
import numpy as np
import pandas as pd
from CHECLabPy.plotting.resolutions import ChargeResolutionPlotter, \
    ChargeResolutionWRRPlotter, ChargeMeanPlotter


def main():
    poi = 1920

    paths = dict(
        withped="/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_withped/charge_res_0.h5",
        poly="/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/charge_res_0.h5",
        none="/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_none/charge_res_0.h5",
        withped_wb="/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_withped/charge_res_wb.h5",
        poly_wb="/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/charge_res_wb.h5",
        none_wb="/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_none/charge_res_wb.h5",
    )

    labels = dict(
        withped="TF With Pedestal",
        poly="TF Polynomial Regression",
        none="Pedestal Only",
        withped_wb="TF With Pedestal, Without bias",
        poly_wb="TF Polynomial Regression, Without bias",
        none_wb="Pedestal Only, Without bias",
    )

    stores = {key: pd.HDFStore(path) for key, path in paths.items()}

    output_dir = "/Volumes/gct-jason/data_checs/dynamicrange_180514"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Created directory: {}".format(output_dir))

    keys = [
        "withped",
        "poly",
        "none",
        # "withped_wb",
        # "poly_wb",
        # "none_wb"
    ]
    p_cr = ChargeResolutionPlotter()
    for key in keys:
        store = stores[key]
        label = labels[key]
        p_cr.set_store(store)
        # p_cr.plot_camera(label + " (camera)")
        p_cr.plot_pixel(poi, label + " (pixel {})".format(poi))
    true = np.geomspace(0.1, 2000, 1000)
    p_cr.plot_goal(true)
    p_cr.plot_requirement(true)
    p_cr.plot_poisson(true)
    p_cr.plot_opct_file()
    p_cr.add_legend()
    p_cr.save(os.path.join(output_dir, "charge_res.pdf"))

    keys = [
        "withped",
        "poly",
        "none",
        # "withped_wb",
        # "poly_wb",
        # "none_wb"
    ]
    p_crwrr = ChargeResolutionWRRPlotter()
    for key in keys:
        store = stores[key]
        label = labels[key]
        p_crwrr.set_store(store)
        p_crwrr.plot_camera(label + " (camera)")
        # p_crwrr.plot_pixel(poi, label + " (pixel {})".format(poi))
    true = np.geomspace(0.1, 2000, 1000)
    p_crwrr.plot_goal(true)
    p_crwrr.plot_requirement(true)
    p_crwrr.plot_poisson(true)
    p_crwrr.add_legend("lower right")
    p_crwrr.save(os.path.join(output_dir, "charge_res_wrr.pdf"))

    keys = [
        "withped",
        "poly",
        "none",
        # "withped_wb",
        # "poly_wb",
        # "none_wb"
    ]
    p_mean = ChargeMeanPlotter()
    for key in keys:
        store = stores[key]
        label = labels[key]
        p_mean.set_store(store)
        # p_mean.plot_camera(label + " (camera)")
        p_mean.plot_pixel(poi, label + " (pixel {})".format(poi))
    p_mean.plot_opct_file()
    p_mean.add_legend("best")
    p_mean.save(os.path.join(output_dir, "charge_mean.pdf"))


if __name__ == '__main__':
    main()
