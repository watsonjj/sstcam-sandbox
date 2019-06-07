import MySQLdb
import numpy as np
import pandas as pd


def convert_timestamp_to_uuidv1(timestamp):
    return (int(timestamp.timestamp()) * 10**7) + 0x01b21dd213814000


def convert_uuidv1_array_to_timestamp(uuidv1):
    return pd.to_datetime((uuidv1 - 0x01b21dd213814000) / 10**7, unit='s')


class SQLQuerier:
    def __init__(self):
        self.db = MySQLdb.connect(
            host="slntmcdb.astrivpn.com",
            user="ASTRI",
            passwd="ASTRIteam2014",
            db="monitoring"
        )
        self.cursor = self.db.cursor()

    def get_all_tables(self):
        self.cursor.execute("show tables;")
        return [t[0] for t in self.cursor.fetchall()]

    def get_table_between_datetimes(self, table, start, end):
        start_uuidv1 = convert_timestamp_to_uuidv1(start)
        end_uuidv1 = convert_timestamp_to_uuidv1(end)

        self.cursor.execute(
            f"SELECT *  FROM {table} "
            f"WHERE (timetag BETWEEN {start_uuidv1} AND {end_uuidv1});"
        )
        ret = self.cursor.fetchall()
        if not ret:
            return pd.DataFrame(columns=['timestamp', 'value'])
        uuidv1, value = np.array(ret).T
        timestamp = convert_uuidv1_array_to_timestamp(
            uuidv1.astype(np.uint64)
        )
        try:
            value = value.astype(np.float64)
        except ValueError:
            pass
        return pd.DataFrame(dict(timestamp=timestamp, value=value))
