import numpy as np
from target_calib import CalculateRowColumnBlockPhase, GetCellIDTCArray
from CHECLabPySB import get_astri_2019, get_data
from os.path import join

# TODO:
#  - Possible results:
#     - Histogram of stddev of pedestal value
#     - Histogram of residuals
#     - Histogram of resduals to demonstrate how the correct value has changed
#     - Within each pixel (camera image and histogram)
#     - Global camera values
#  - Value changes between lab and led
#  - Stddev changes between lab and led
#  - Residual changes between lab and led
#  - Same for between led and BP
#  - lab hits vs LED hits vs BP hits
#  - Is value from LED or BP correct for internal trigger data?
#  - Pedestal values versus time (by comparing residuals with first pedestal applied)
#  - Python calib vs Online calib vs R1



def setup_cells(df):
    fci = df['fci'].values.astype(np.uint16)
    frow, fcolumn, fblockphase = CalculateRowColumnBlockPhase(fci)
    fblock = fcolumn * 8 + frow
    df['fblock'] = fblock
    df['fblockphase'] = fblockphase
    df['fbpisam'] = df['fblockphase'] + df['isam']

    cell = GetCellIDTCArray(fci, df['isam'].values)
    row, column, blockphase = CalculateRowColumnBlockPhase(cell)
    block = column * 8 + row
    df['cell'] = cell
    df['block'] = block
    df['blockphase'] = blockphase

    df['iblock'] = (df['isam'] + df['fblockphase']) // 32

    return df


class File:
    @property
    def name(self):
        return self.__class__.__name__

    @property
    def tcal(self):
        return get_data(f"d190730_pedestal/{self.name}/pedestal.tcal")

    @property
    def r1(self):
        return get_data(f"d190730_pedestal/{self.name}/r1.tio")

    @property
    def reduced_cell_info(self):
        return get_data(f"d190730_pedestal/{self.name}/reduced_cell_info.h5")

    @property
    def reduced_residuals(self):
        return get_data(f"d190730_pedestal/{self.name}/reduced_residuals.h5")


class Test(File):
    r0 = "/Users/Jason/Downloads/tempdata/Run06136_r0.tio"


class Lab_bright(File):
    r0 = get_astri_2019("d2019-04-23_nudges/bright_50pe/pedestal_r0.tio")


class Lab_spe0p5(File):
    r0 = get_astri_2019("d2019-04-23_nudges/spe_0.5pe/pedestal_r0.tio")


class Lab_spe0p8(File):
    r0 = get_astri_2019("d2019-04-23_nudges/spe_0.8pe/pedestal_r0.tio")


class Lab_spe1p1(File):
    r0 = get_astri_2019("d2019-04-23_nudges/spe_1.1pe/pedestal_r0.tio")


class Lab_spe1p7(File):
    r0 = get_astri_2019("d2019-04-23_nudges/spe_1.7pe/pedestal_r0.tio")


class Lab_spe2p4(File):
    r0 = get_astri_2019("d2019-04-23_nudges/spe_2.4pe/pedestal_r0.tio")


class d20190501_cosmicray(File):
    r0 = get_astri_2019("d2019-05-01_cosmicray/Run12803_r0.tio")


class d20190501_mrk501_0(File):
    r0 = get_astri_2019("d2019-05-01_mrk501/Run12806_r0.tio")


class d20190501_mrk501_1(File):
    r0 = get_astri_2019("d2019-05-01_mrk501/Run12817_r0.tio")


class d20190501_mrk501_2(File):
    r0 = get_astri_2019("d2019-05-01_mrk501/Run12823_r0.tio")


class d20190502_mrk421(File):
    r0 = get_astri_2019("d2019-05-02_mrk421/Run12921_r0.tio")


class d20190502_pedestal_0(File):
    r0 = get_astri_2019("d2019-05-02_pedestal/Run12926_r0.tio")


class d20190502_pedestal_1(File):
    r0 = get_astri_2019("d2019-05-02_pedestal/Run12927_r0.tio")


class d20190502_mrk501_0(File):
    r0 = get_astri_2019("d2019-05-02_mrk501/Run12930_r0.tio")


class d20190502_mrk501_1(File):
    r0 = get_astri_2019("d2019-05-02_mrk501/Run12935_r0.tio")


class d20190506_mrk501(File):
    r0 = get_astri_2019("d2019-05-06_mrk501/Run13053_r0.tio")


class d20190507_cosmicray_0(File):
    r0 = get_astri_2019("d2019-05-07_cosmicray/Run13096_r0.tio")


class d20190507_cosmicray_1(File):
    r0 = get_astri_2019("d2019-05-07_cosmicray/Run13128_r0.tio")


class d20190508_cosmicray_0(File):
    r0 = get_astri_2019("d2019-05-08_cosmicray/Run13249_r0.tio")


class d20190508_cosmicray_1(File):
    r0 = get_astri_2019("d2019-05-08_cosmicray/Run13311_r0.tio")


class d20190508_ledflashers_dynrange(File):
    r0 = get_astri_2019("d2019-05-08_ledflashers_dynrange/Run13261_r0.tio")


class d20190509_ledflashers_altscans(File):
    r0 = get_astri_2019("d2019-05-09_ledflashers_altscans/Run13323_r0.tio")


class d20190509_mrk421(File):
    r0 = get_astri_2019("d2019-05-09_mrk421/Run13317_r0.tio")


class d20190611_ledflashers_reference_scans(File):
    r0 = get_astri_2019("d2019-06-11_ledflashers_reference_scans/Run13498_r0.tio")


class d20190611_lookback(File):
    r0 = get_astri_2019("d2019-06-11_lookback/Run13425_r0.tio")


class d20190611_ledflashers_dynrange(File):
    r0 = get_astri_2019("d2019-06-11_ledflashers_dynrange/Run13548_r0.tio")


class d20190612_mrk421_moonlight(File):
    r0 = get_astri_2019("d2019-06-12_mrk421_moonlight/Run13636_r0.tio")


class d20190612_mrk501(File):
    r0 = get_astri_2019("d2019-06-12_mrk501/Run13680_r0.tio")


class d20190612_mrk501_moonlight(File):
    r0 = get_astri_2019("d2019-06-12_mrk501_moonlight/Run13639_r0.tio")


class d20190612_muon(File):
    r0 = get_astri_2019("d2019-06-12_muon/Run13695_r0.tio")


class d20190614_pedestal_0(File):
    r0 = get_astri_2019("d2019-06-14_pedestal/Run13794_r0.tio")


class d20190614_pedestal_1(File):
    r0 = get_astri_2019("d2019-06-14_pedestal/Run13795_r0.tio")


class d20190614_pedestal_2(File):
    r0 = get_astri_2019("d2019-06-14_pedestal/Run13798_r0.tio")


class d20190614_pedestal_3(File):
    r0 = get_astri_2019("d2019-06-14_pedestal/Run13799_r0.tio")


class d20190614_pedestal_4(File):
    r0 = get_astri_2019("d2019-06-14_pedestal/Run13800_r0.tio")


all_files = [
    Lab_bright(),
    Lab_spe0p5(),
    Lab_spe0p8(),
    Lab_spe1p1(),
    Lab_spe1p7(),
    Lab_spe2p4(),
    d20190501_cosmicray(),
    d20190501_mrk501_0(),
    d20190501_mrk501_1(),
    d20190501_mrk501_2(),
    d20190502_mrk421(),
    d20190502_pedestal_0(),
    d20190502_pedestal_1(),
    d20190502_mrk501_0(),
    d20190502_mrk501_1(),
    d20190506_mrk501(),
    d20190507_cosmicray_0(),
    d20190507_cosmicray_1(),
    d20190508_cosmicray_0(),
    d20190508_cosmicray_1(),
    d20190508_ledflashers_dynrange(),
    d20190509_ledflashers_altscans(),
    d20190509_mrk421(),
    d20190611_ledflashers_reference_scans(),
    d20190611_lookback(),
    d20190611_ledflashers_dynrange(),
    d20190612_mrk421_moonlight(),
    d20190612_mrk501(),
    d20190612_mrk501_moonlight(),
    d20190612_muon(),
    d20190614_pedestal_0(),
    d20190614_pedestal_1(),
    d20190614_pedestal_2(),
    d20190614_pedestal_3(),
    d20190614_pedestal_4(),
]


method_comparison = [
    Lab_bright(),
    d20190502_mrk421(),
    d20190614_pedestal_0(),
    d20190614_pedestal_1(),
    d20190614_pedestal_2(),
    d20190614_pedestal_3(),
    d20190614_pedestal_4(),
]
