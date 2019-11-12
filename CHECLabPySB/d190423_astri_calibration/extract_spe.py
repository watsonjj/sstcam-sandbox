from CHECLabPySB import get_astri_2019
from os.path import join, abspath, dirname
import pandas as pd
import subprocess


DIR = abspath(dirname(__file__))
DATA = get_astri_2019("d2019-04-23_nudges")


def main():
    spe_config = join(DIR, "spe_config.yml")
    df_spe = pd.read_csv(join(DIR, "spe_runlist.txt"), sep='\t')
    for _, row in df_spe.iterrows():
        nudge = row['nudge']
        spe_paths = [
            join(DATA, f"spe_0.5pe/{row['spe_0.5pe']}"),
            join(DATA, f"spe_0.8pe/{row['spe_0.8pe']}"),
            join(DATA, f"spe_1.1pe/{row['spe_1.1pe']}"),
            join(DATA, f"spe_1.7pe/{row['spe_1.7pe']}"),
            join(DATA, f"spe_2.4pe/{row['spe_2.4pe']}"),
        ]
        spe_paths_str = " ".join(spe_paths)
        output_path = join(DATA, f"spe_{nudge:+d}.h5")
        cmd = (
            f"extract_spe -f {spe_paths_str} -C charge_cc "
            f"-c {spe_config} -o {output_path}"
        )
        print(cmd)
        subprocess.call(cmd)


if __name__ == '__main__':
    main()
