from sstcam_sandbox import get_checs, get_data
from TargetCalibSB.vped import VpedCalibrator


def process(first_half_path, second_half_path, output_path):
    vped_calibrator = VpedCalibrator()
    vped_calibrator.read_ascii(first_half_path, second_half_path)
    vped_calibrator.save(output_path)


def main():
    first_half_path = get_checs("d181203_erlangen/vped/VPED_TF_0-31_13deg.txt")
    second_half_path = get_checs("d181203_erlangen/vped/VPED_TF_32-63_13deg.txt")
    output_path = get_data("d191122_dc_tf/vped/VPED_13deg.h5")
    process(first_half_path, second_half_path, output_path)

    first_half_path = get_checs("d181203_erlangen/vped/VPED_TF_0-31_23deg.txt")
    second_half_path = get_checs("d181203_erlangen/vped/VPED_TF_32-63_23deg.txt")
    output_path = get_data("d191122_dc_tf/vped/VPED_23deg.h5")
    process(first_half_path, second_half_path, output_path)

    first_half_path = get_checs("d181203_erlangen/vped/VPED_TF_0-31_33deg.txt")
    second_half_path = get_checs("d181203_erlangen/vped/VPED_TF_32-63_33deg.txt")
    output_path = get_data("d191122_dc_tf/vped/VPED_33deg.h5")
    process(first_half_path, second_half_path, output_path)

    first_half_path = get_checs("d181203_erlangen/vped/VPED_TF_0-31_43deg.txt")
    second_half_path = get_checs("d181203_erlangen/vped/VPED_TF_32-63_43deg.txt")
    output_path = get_data("d191122_dc_tf/vped/VPED_43deg.h5")
    process(first_half_path, second_half_path, output_path)


if __name__ == '__main__':
    main()
