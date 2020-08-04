from TargetCalibSB.tf import TFDC, TFACCrossCorrelation
from TargetCalibSB.vped import VpedCalibrator


def get_dc_tf(dc_tf_path, vped_calibration_path):
    tf = TFDC.from_file(dc_tf_path)
    vped_calibrator = VpedCalibrator()
    vped_calibrator.load(vped_calibration_path)
    tf.finish_generation(vped_calibrator)
    return tf


def get_ac_tf(ac_tf_path):
    tf = TFACCrossCorrelation.from_tcal(ac_tf_path)
    tf.finish_generation()
    return tf


def get_ac_cc_tf(ac_cc_tf_path):
    tf = TFACCrossCorrelation.from_file(ac_cc_tf_path)
    tf.finish_generation()
    return tf
