from CHECLabPy.core.io import HDF5Reader, HDF5Writer
from CHECLabPy.utils.files import sort_file_list
from glob import glob


def main():
    input_paths = glob("/Volumes/gct-jason/astri_onsky_archive/d2019-11-19_monitor/*_mon.h5")
    input_paths = sort_file_list(input_paths)
    output_path = "/Volumes/gct-jason/astri_onsky_archive/d2019-11-19_monitor/monitor.h5"

    n_files = len(input_paths)

    with HDF5Writer(output_path) as writer:
        for ipath, input_path in enumerate(input_paths):
            print("PROGRESS: Processing file {}/{}".format(ipath + 1, n_files))

            with HDF5Reader(input_path) as reader:
                keys = reader.dataframe_keys
                for key in keys:
                    df = reader.read(key)
                    df = df.rename(columns={"icomp": "iunit"})
                    writer.append(df, key=key)


if __name__ == '__main__':
    main()
