from sstcam_sandbox.d190730_pedestal import all_files
import argparse
from subprocess import call
from os.path import exists


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry', dest='dry', action="store_true")
    args = parser.parse_args()
    dry = args.dry

    for ped_file in all_files:
        r0_path = ped_file.r0
        r1_path = ped_file.r1
        ped_path = ped_file.tcal
        shell_path = ped_path.replace(".tcal", ".sh")
        generate_ped = f"apply_calibration -i {r0_path} -p {ped_path} -o {r1_path} -n 2000\n"

        if not exists(r0_path):
            raise FileNotFoundError(f"Missing R0 file: {r0_path}")

        with open(shell_path, 'w') as file:
            file.write("source $HOME/.bash_profile\n")
            file.write("source activate cta\n")
            file.write("export NUMBA_NUM_THREADS=6\n")
            file.write(generate_ped)
            file.write(f"if [ -f {ped_path} ]; then\n")
            file.write(f"\trm -f {shell_path}\n")
            file.write("fi\n")
        call("chmod +x {}".format(shell_path), shell=True)

        cmd = "qsub -cwd -V -P short {}".format(shell_path)
        print(cmd)
        if not dry:
            call(cmd, shell=True)


if __name__ == '__main__':
    main()
