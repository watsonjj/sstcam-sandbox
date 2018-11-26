from subprocess import call
import os
from CHECLabPySB.scripts.d181123_tf_cell_check import TF_Storage, \
    TF_Sampling, all_files


def process(file, tf):
    r0_path = file.r0_path
    r1_name = os.path.basename(r0_path).replace("_r0", "_r1")
    r1_path = os.path.join(tf.r1_dir, r1_name)
    ped_path = file.ped_path
    tf_path = tf.path

    output_dir = os.path.dirname(r1_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    apply_calibration = "apply_calibration -i {} -p {} -t {} -o {}"
    cmd = apply_calibration.format(r0_path, ped_path, tf_path, r1_path)
    print(cmd)
    call(cmd, shell=True)


def main():
    for f in all_files:
        process(f, TF_Sampling())
        process(f, TF_Storage())


if __name__ == '__main__':
    main()
