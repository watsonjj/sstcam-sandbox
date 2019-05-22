import pandas as pd
from CHECLabPy.core.io import HDF5Reader, HDF5Writer

path = "/Users/Jason/Software/CHECLabPySB/CHECLabPySB/d190506_astri_publicity/events.txt"
output_path = path.replace(".txt", "_hillas.h5")


with HDF5Writer(output_path) as writer:
    df = pd.read_csv(path, sep='\t')
    ifile = 0
    for _, row in df.iterrows():
        path = row['path']
        iev = row['iev']

        with HDF5Reader(path) as reader:
            df = reader.read("data")
            df = df.loc[df['iev'] == iev]

            if ifile == 0:
                writer.add_mapping(reader.get_mapping())
                writer.add_metadata(**reader.get_metadata())

            keys = ['data', 'pointing', 'mc', 'mcheader']
            for key in keys:
                if key not in reader.dataframe_keys:
                    continue
                df = reader.read(key)
                df = df.loc[df['iev'] == iev]
                writer.append(df, key=key)
        ifile += 1