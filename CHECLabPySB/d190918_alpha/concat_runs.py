from CHECLabPySB import get_astri_2019, get_data
from CHECLabPy.core.io import HDF5Reader, HDF5Writer
from CHECLabPy.utils.files import sort_file_list
from glob import glob


def main():
    output_path = get_data(f"d190918_alpha/onsky_hillas.h5")
    path_list = [
        glob(get_astri_2019("d2019-05-01_mrk501/*_hillas.h5")),
        glob(get_astri_2019("d2019-05-02_PG1553+113/*_hillas.h5")),
        glob(get_astri_2019("d2019-05-02_mrk421/*_hillas.h5")),
        glob(get_astri_2019("d2019-05-02_mrk501/*_hillas.h5")),
        glob(get_astri_2019("d2019-05-06_mrk501/*_hillas.h5")),
        glob(get_astri_2019("d2019-05-09_mrk421/*_hillas.h5")),
        glob(get_astri_2019("d2019-06-12_mrk421_moonlight/*_hillas.h5")),
        glob(get_astri_2019("d2019-06-12_mrk501/*_hillas.h5")),
        glob(get_astri_2019("d2019-06-12_mrk501_moonlight/*_hillas.h5")),
    ]

    with HDF5Writer(output_path) as writer:
        for iinv, hillas_paths in enumerate(path_list):
            hillas_paths = sort_file_list(hillas_paths)

            for ifile, input_path in enumerate(hillas_paths):
                with HDF5Reader(input_path) as reader:
                    if ifile == 0:
                        writer.add_mapping(reader.get_mapping())
                        writer.add_metadata(**reader.get_metadata())

                    df = reader.read("data")
                    df_pointing = reader.read("pointing")
                    df_source = reader.read("source")
                    source_name = reader.get_metadata("source")['source_name']

                    df['iinv'] = iinv
                    df['ifile'] = ifile
                    df['source_ra'] = df_source['source_ra'].values
                    df['source_dec'] = df_source['source_dec'].values
                    df['altitude_raw'] = df_pointing['altitude_raw'].values
                    df['altitude_cor'] = df_pointing['altitude_cor'].values
                    df['azimuth_raw'] = df_pointing['azimuth_raw'].values
                    df['azimuth_cor'] = df_pointing['azimuth_cor'].values
                    df['source_name'] = source_name

                    writer.append(df, 'data')


if __name__ == '__main__':
    main()
