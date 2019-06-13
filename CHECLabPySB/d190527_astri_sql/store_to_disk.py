from CHECLabPySB.d190527_astri_sql.sqlquerier import SQLQuerier
from CHECLabPySB import get_astri_2019
from CHECLabPy.core.io import HDF5Writer
import pandas as pd
from tqdm import tqdm
from IPython import embed


def main():
    sql = SQLQuerier()
    start = pd.Timestamp("2019-04-29 00:00")
    end = pd.Timestamp("2019-05-13 00:00")

    # path = get_astri_2019("astri_database_d190429-d190513.h5")
    path = "astri_database_d190429-d190513.h5"
    with HDF5Writer(path) as w:
        table_names = set(sql.get_all_tables()) - {'logbook'}
        for table_name in tqdm(table_names):
            print(table_name)
            table = sql.get_table_between_datetimes(table_name, start, end)
            w.write(**{table_name: table})


if __name__ == '__main__':
    main()
