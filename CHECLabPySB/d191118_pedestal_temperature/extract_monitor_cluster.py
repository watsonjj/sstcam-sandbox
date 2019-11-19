import argparse
from subprocess import call
from os.path import join, abspath, dirname
from glob import glob


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry', dest='dry', action="store_true")
    args = parser.parse_args()
    dry = args.dry

    base = "/lfs/l2/chec/checs/data/astri_onsky_archive"
    paths = glob(join(base, "d2019-11-19_monitor/*.mon"))

    extract_monitor_path = join(abspath(dirname(__file__)), "extract_monitor.py")

    extract_monitor = f"python {extract_monitor_path} -f {{}} -o {{}}\n"
    correct_permissions = "getfacl -d . | setfacl --set-file=- {}\n"

    for path in paths:
        shell_path = path.replace(".mon", ".sh")
        h5_path = path.replace(".mon", "_mon.h5")

        with open(shell_path, 'w') as file:
            file.write("source $HOME/.bash_profile\n")
            file.write("source activate cta\n")
            file.write("export NUMBA_NUM_THREADS=6\n")
            file.write(extract_monitor.format(path, h5_path))
            file.write(correct_permissions.format(h5_path))
            file.write(f"if [ -f {h5_path} ]; then\n")
            file.write(f"\trm -f {shell_path}\n")
            file.write("fi\n")
        call("chmod +x {}".format(shell_path), shell=True)

        cmd = "qsub -cwd -V -q lfc.q {}".format(shell_path)
        print(cmd)
        if not dry:
            call(cmd, shell=True)


if __name__ == '__main__':
    main()
