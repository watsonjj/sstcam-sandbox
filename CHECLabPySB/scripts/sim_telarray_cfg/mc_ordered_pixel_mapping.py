import pandas as pd
import numpy as np
from IPython import embed


def main():
    path = "/Users/Jason/Software/TargetCalib/source/dev/mapping_checs_V1-1-0.cfg"
    new_path = "/Users/Jason/Software/TargetCalib/source/dev/mapping_checs_V1-1-0mc.cfg"

    df = pd.read_csv(path, sep='\t')
    df_new = df.sort_values(['row', 'col'])
    df_new['pixel'] = np.arange(2048)

    sp_ordering = df_new.groupby('superpixel').min().sort_values('pixel').index.values
    lookup = np.argsort(sp_ordering)
    df_new['superpixel'] = lookup[df_new['superpixel'].values]

    slot_ordering = df_new.groupby('slot').min().sort_values('pixel').index.values
    lookup = np.argsort(slot_ordering)
    df_new['slot'] = lookup[df_new['slot'].values]

    for itm in range(32):
        lookup = np.argsort(df_new.loc[df_new['slot'] == itm]['pixel'].values)
        df_new.loc[df_new['slot'] == itm, 'tmpix'] = lookup

    # for name, group in df_new.groupby('slot'):
    #     group['tmpix']
    #
    # tmpix_ordering = df_new.groupby('slot').min().sort_values('pixel').index.values
    # lookup = np.argsort(tmpix_ordering)
    # df_new['tmpix'] = lookup[df_new['tmpix'].values]

    df_new.to_csv(new_path, sep='\t', float_format='%.7f', index=False)


if __name__ == '__main__':
    main()