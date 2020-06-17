import argparse
from subprocess import call
import pandas as pd
from os.path import dirname, join


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry', dest='dry', action="store_true")
    args = parser.parse_args()
    dry = args.dry

    base = "/lfs/l2/chec/userspace/jasonjw/Data/astri_onsky_archive"
    runlist_paths = [
        join(base, "d2019-04-30_cosmicray/runlist.txt"),
        join(base, "d2019-05-01_cosmicray/runlist.txt"),
        join(base, "d2019-05-01_mrk501/runlist.txt"),
        join(base, "d2019-05-02_PG1553+113/runlist.txt"),
        join(base, "d2019-05-02_mrk421/runlist.txt"),
        join(base, "d2019-05-02_mrk501/runlist.txt"),
        join(base, "d2019-05-06_mrk501/runlist.txt"),
        join(base, "d2019-05-07_cosmicray/runlist.txt"),
        join(base, "d2019-05-08_cosmicray/runlist.txt"),
        # join(base, "d2019-05-08_ledflashers_dynrange/runlist.txt"),
        # join(base, "d2019-05-08_mrk501_drift/runlist.txt"),
        # join(base, "d2019-05-08_slowsignal/runlist.txt"),
        # join(base, "d2019-05-09_ledflashers_altscans/runlist.txt"),
        join(base, "d2019-05-09_mrk421/runlist.txt"),
    ]

    extract_dl1 = "extract_dl1_onsky -f {}\n"
    extract_hillas = "extract_hillas -f {}\n"
    correct_permissions = "getfacl -d . | setfacl --set-file=- {}\n"

    for runlist_path in runlist_paths:
        df_runlist = pd.read_csv(runlist_path, sep='\t')
        directory = dirname(runlist_path)
        for _, row in df_runlist.iterrows():
            run = row['run']
            shell_path = join(directory, f"Run{run:05d}.sh")
            r1_path = shell_path.replace(".sh", "_r1.tio")
            dl1_path = r1_path.replace("_r1.tio", "_dl1.h5")
            hillas_path = dl1_path.replace("_dl1.h5", "_hillas.h5")

            with open(shell_path, 'w') as file:
                file.write("source $HOME/.bash_profile\n")
                file.write("source activate cta\n")
                file.write("export NUMBA_NUM_THREADS=6\n")
                file.write(extract_dl1.format(r1_path))
                file.write(extract_hillas.format(dl1_path))
                file.write(correct_permissions.format(dl1_path))
                file.write(correct_permissions.format(hillas_path))
                file.write(f"if [ -f {hillas_path} ]; then\n")
                file.write(f"\trm -f {shell_path}\n")
                file.write("fi\n")
            call("chmod +x {}".format(shell_path), shell=True)

            cmd = "qsub -cwd -V -q lfc.q {}".format(shell_path)
            print(cmd)
            if not dry:
                call(cmd, shell=True)


if __name__ == '__main__':
    main()
