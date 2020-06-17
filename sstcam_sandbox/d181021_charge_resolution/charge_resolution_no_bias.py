from sstcam_sandbox import HDF5Writer, HDF5Reader
from sstcam_sandbox.d181021_charge_resolution import all_files
from tqdm import tqdm
from CHECLabPy.utils.files import open_runlist_dl1
from CHECLabPy.utils.resolutions import ChargeStatistics, ChargeResolution


def process(file):

    runlist_path = file.runlist_path
    charge_averages_path = file.charge_averages_path
    fw_path = file.fw_path
    ff_path = file.ff_path
    output_path = file.charge_resolution_path

    df_runs = open_runlist_dl1(runlist_path)
    df_runs['transmission'] = 1/df_runs['fw_atten']
    n_runs = df_runs.index.size
    mapping = df_runs.iloc[0]['reader'].mapping
    n_pixels = df_runs.iloc[0]['reader'].n_pixels

    with HDF5Reader(charge_averages_path) as reader:
        df_avg = reader.read("data")
        mapping = reader.read_mapping()
        metadata = reader.read_metadata()

    with HDF5Reader(fw_path) as reader:
        df = reader.read("data")
        fw_m = df['fw_m'].values
        fw_merr = df['fw_merr'].values

    with HDF5Reader(ff_path) as reader:
        df = reader.read("data")
        ff_m = df['ff_m'].values
        ff_c = df['ff_c'].values

    cr = ChargeResolution()
    cs = ChargeStatistics()

    desc0 = "Looping over files"
    it = enumerate(df_runs.iterrows())
    for i, (_, row) in tqdm(it, total=n_runs, desc=desc0):
        reader = row['reader']
        transmission = row['transmission']

        n_rows = n_pixels * 1000
        pixel, charge = reader.select_columns(['pixel', 'charge'], stop=n_rows)

        true = transmission * fw_m[pixel]

        avg = df_avg.loc[df_avg['transmission'] == transmission, 'mean'].values[pixel]
        avg_cal = (avg - ff_c[pixel]) / ff_m[pixel]
        correction = avg_cal - true

        measured = (charge - ff_c[pixel]) / ff_m[pixel]
        measured -= correction

        cr.add(pixel, true, measured)
        cs.add(pixel, true, measured)
        reader.store.close()
    df_cr_pixel, df_cr_camera = cr.finish()
    df_cs_pixel, df_cs_camera = cs.finish()

    def add_error(df):
        df['true_err'] = df['true'] / fw_m[df['pixel']] * fw_merr[df['pixel']]
    add_error(df_cr_pixel)

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
