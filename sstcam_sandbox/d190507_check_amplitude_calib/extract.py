import pandas as pd
from glob import glob
from sstcam_sandbox import get_astri_2019, get_data
from CHECLabPy.core.io import TIOReader, HDF5Writer
from CHECOnsky.calib import get_nudge_and_temperature_from_reader
import re


def main():
    paths = glob(get_astri_2019("*/*_r1.tio"))
    pattern = re.compile(r"(?:.+?)/d(.+?)/Run(\d+?)_r1.tio")
    d_list = []
    for path in paths:
        reader = TIOReader(path)
        wfs = reader[0]
        nudge, temperature = get_nudge_and_temperature_from_reader(reader)

        regexp = re.search(pattern, path)
        investigation = regexp.group(1)
        run_id = regexp.group(2)

        d_list.append(dict(
            investigation=investigation,
            run_id=run_id,
            t_cpu=wfs.t_cpu,
            nudge=nudge,
            temperature=temperature
        ))

    df = pd.DataFrame(d_list)
    with HDF5Writer(get_data("d190507_check_amplitude_calib/data.h5")) as w:
        w.write(data=df)


if __name__ == '__main__':
    main()
