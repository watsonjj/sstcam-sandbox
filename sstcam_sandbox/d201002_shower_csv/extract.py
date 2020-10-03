from glob import glob
from os.path import dirname, join
import tables
import numpy as np
import pandas as pd
from tqdm import tqdm


def process(paths, output_path):
    df_list = []
    for path in tqdm(paths):
        with tables.open_file(path) as file:
            layout = file.root.configuration.instrument.subarray.layout
            shower = file.root.simulation.event.subarray.shower

            df_layout = pd.DataFrame(layout.read()).set_index('tel_id')
            df_shower = pd.DataFrame(shower.read()).set_index(['obs_id', 'event_id'])

            parameters = file.root.simulation.event.telescope.parameters
            for param in parameters:
                df_param = pd.DataFrame(param.read()).set_index(['obs_id', 'event_id'])
                df_telescope = pd.merge(df_shower, df_param, left_index=True, right_index=True)
                itel = int(df_telescope.iloc[0]['tel_id'])
                telescope = df_layout.loc[itel]
                sep_x = telescope.pos_x - df_telescope['true_core_x']
                sep_y = telescope.pos_y - df_telescope['true_core_y']
                impact_distance = np.sqrt(sep_x**2 + sep_y**2)
                df_telescope['true_impact_distance'] = impact_distance
                df_list.append(df_telescope.reset_index())
    df = pd.concat(df_list, ignore_index=True)
    df = df.sort_values(['obs_id', 'event_id', 'tel_id'])
    df = df.reindex(sorted(df.columns), axis=1)
    df.to_csv(output_path)
    print(f"{df.index.size} events")


def main():
    paths = glob("/Users/Jason/Downloads/tempdata/d200616_prod4/gamma/*_dl1.h5")
    output_path = join(dirname(paths[0]), "gamma.csv")
    process(paths, output_path)

    paths = glob("/Users/Jason/Downloads/tempdata/d200616_prod4/proton/*_dl1.h5")
    output_path = join(dirname(paths[0]), "proton.csv")
    process(paths, output_path)


if __name__ == '__main__':
    main()
