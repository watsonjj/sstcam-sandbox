import argparse
from CHECLabPy.core.io import HDF5Writer
import numpy as np
import pandas as pd
from tqdm import tqdm
from subprocess import check_output
from datetime import datetime
import pytz


TZ = pytz.timezone("Europe/Berlin")


def get_datetime(string):
    return TZ.localize(
        datetime.strptime(string, "%Y-%m-%d %H:%M:%S:%f"),
        is_dst=None
    ).astimezone(pytz.utc).replace(tzinfo=None)


def get_number_lines(path):
    return int(check_output(f"wc -l {path}", shell=True).split()[0])


def main():
    parser = argparse.ArgumentParser(
        description='Process a monitor file into a HDF5 pandas dataframe',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-f', '--file', dest='input_path',
        help='path to the monitor file'
    )
    parser.add_argument(
        '-o', '--output', dest='output_path',
        help='path to store the output file'
    )
    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path

    n_lines = get_number_lines(input_path)
    with HDF5Writer(output_path) as writer:
        with open(input_path) as file:
            iev = 0
            for line in tqdm(file, desc="Reading lines", total=n_lines):
                if line and line != '\n':
                    try:
                        if "Monitoring Event Done" in line:
                            iev += 1
                            continue
                        elif "EventBuildingReport" in line:
                            continue
                        elif "Counter" in line:
                            continue
                        elif line.startswith('\t') or line.startswith(' '):
                            continue
                        elif line.startswith("Number"):
                            continue
                        elif line.startswith("Start"):
                            continue

                        data = line.replace('\n', '').replace('\t', " ").rstrip()
                        data = data.replace(": TM IS NOT CONTACTABLE", " nan")
                        data = data.split(" ")

                        t_cpu = get_datetime(f"{data[0]} {data[1]}")

                        device = data[2]
                        measurement = data[3]
                        key = device + "_" + measurement

                        if (device == "TM") and (len(data) == 6):
                            icomp = np.array(data[4], dtype=np.int)
                            value = float(data[5])
                        elif (device == "TM") and (len(data) == 21):
                            icomp = np.arange(16) + int(data[4]) * 16
                            value = np.array(data[5:], dtype=np.float)
                        elif (device == "BP") and (len(data) == 36):
                            icomp = np.arange(32)
                            value = np.array(data[4:], dtype=np.float)
                        elif len(data) == 5:
                            icomp = np.array(0, dtype=np.int)
                            value = float(data[4])
                        elif len(data) == 4:
                            continue
                        else:
                            raise ValueError()

                        entry = dict(
                            iev=iev, t_cpu=t_cpu, icomp=icomp, value=value
                        )
                        entry = pd.DataFrame(entry, index=np.arange(icomp.size))
                        writer.append(entry, key=key, expectedrows=n_lines)

                    except:
                        pass
                    # except ValueError:
                    #     print("ValueError from line: {}".format(line))
                    # except IndexError:
                    #     print("IndexError from line: {}".format(line))


if __name__ == '__main__':
    main()
