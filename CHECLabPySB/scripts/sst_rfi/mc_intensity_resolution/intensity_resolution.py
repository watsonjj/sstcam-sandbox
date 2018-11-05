from CHECLabPySB import HDF5Writer, HDF5Reader
from CHECLabPySB.scripts.sst_rfi.mc_intensity_resolution import all_files
from tqdm import tqdm
from CHECLabPy.utils.resolutions import ChargeStatistics, ChargeResolution
from CHECLabPy.core.io import DL1Reader


def process(file):

    dl1_paths = file.dl1_paths
    pde = file.pde
    mc_calib_path = file.mc_calib_path
    output_path = file.intensity_resolution_path

    n_runs = len(dl1_paths)
    reader_list = [DL1Reader(p) for p in dl1_paths]
    mapping = reader_list[0].mapping
    n_pixels = reader_list[0].n_pixels
    n_rows = n_pixels * 1000

    with HDF5Reader(mc_calib_path) as reader:
        df = reader.read("data")
        mc_m = df['mc_m'].values

    cr = ChargeResolution(mc_true=True)
    cs = ChargeStatistics()

    desc0 = "Looping over files"
    for reader in tqdm(reader_list, total=n_runs, desc=desc0):
        pixel, charge, true = reader.select_columns(['pixel', 'charge', 'mc_true'], stop=n_rows)
        true_photons = true / pde
        measured = charge / mc_m[pixel]

        f = true > 0
        true_photons = true_photons[f]
        measured = measured[f]

        cr.add(pixel, true_photons, measured)
        cs.add(pixel, true_photons, measured)
        reader.store.close()
    df_cr_pixel, df_cr_camera = cr.finish()
    df_cs_pixel, df_cs_camera = cs.finish()

    with HDF5Writer(output_path) as writer:
        writer.write(
            charge_resolution_pixel=df_cr_pixel,
            charge_resolution_camera=df_cr_camera,
            charge_statistics_pixel=df_cs_pixel,
            charge_statistics_camera=df_cs_camera,
        )
        writer.write_mapping(mapping)
        writer.write_metadata(n_pixels=n_pixels)


def main():
    [process(f) for f in all_files]


if __name__ == '__main__':
    main()
