from sstcam_sandbox import get_plot
from CHECLabPy.plotting.setup import Plotter
from CHECOnsky.utils.astri_database import ASTRISQLQuerier
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.colors as mcolors


class Uptime(Plotter):
    def plot(self, sql, start, end, title):
        start_day = start.floor("D")
        end_day = end.ceil("D")

        df = sql.get_table_between_datetimes(
            "TCU_ELACTPOS", start_day, end_day
        )
        df = df.set_index('timestamp')
        df = df.resample('1h').count()

        idx = pd.date_range(start_day, end_day, freq='h')

        df_c = df.loc[start_day:end_day].reindex(idx, fill_value=0)
        date = df_c.resample('d').count().index
        time = pd.date_range("2019-10-09 00:00", "2019-10-10 00:00", freq='h')
        count = df_c.iloc[:-1]['value'].values.reshape(
            (date.size - 1, time.size - 1))
        count_3 = count.copy()
        count_3[count == 0] = 0
        count_3[(count > 0) & (count < count.max())] = 1
        count_3[count == count.max()] = 2

        weeks = mdates.WeekdayLocator(byweekday=mdates.MO)
        hours = mdates.HourLocator()
        hours_fmt = mdates.DateFormatter('%H:%M')
        cmap = mcolors.LinearSegmentedColormap.from_list("", [
            "red", "yellow", "green"
        ])

        self.ax.pcolor(
            date, time, count_3.T, cmap=cmap, edgecolors='k', linewidths=0.5
        )
        self.fig.autofmt_xdate()
        self.ax.xaxis.set_major_locator(weeks)
        self.ax.yaxis.set_major_locator(hours)
        self.ax.yaxis.set_major_formatter(hours_fmt)
        self.ax.yaxis.set_tick_params(direction='out', which='both')
        self.ax.yaxis.set_tick_params(which='minor', left=False, right=False)
        self.ax.xaxis.set_tick_params(direction='out', which='both')
        self.ax.xaxis.set_tick_params(which='minor', left=False, right=False)
        self.ax.set_title(title)


def main():
    sql = ASTRISQLQuerier()

    p_uptime = Uptime()

    start = pd.Timestamp("2019-04-29 00:00")
    end = pd.Timestamp("2019-05-13 00:00")
    p_uptime.plot(sql, start, end, None)

    start = pd.Timestamp("2019-06-10 00:00")
    end = pd.Timestamp("2019-06-16 00:00")
    p_uptime.plot(sql, start, end, "ASTRI Pointing Database Uptime")

    p_uptime.save(get_plot("d191009_astri_db_uptime/campaign_all.pdf"))


if __name__ == '__main__':
    main()
