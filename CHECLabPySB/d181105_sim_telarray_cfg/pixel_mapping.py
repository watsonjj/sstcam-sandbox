from CHECLabPySB import get_data
from CHECLabPy.utils.files import create_directory
import numpy as np
import pandas as pd
import os
from target_calib import Mapping


def create_new_mapping(input_path, output_path):
    """
    Create a TargetCalib Mapping file with the latest pixel positions,
    but the prod3 pixel ordering
    """
    create_directory(os.path.dirname(output_path))

    df = pd.read_csv(input_path, sep='\t')
    df_new = df.sort_values(['row', 'col'])
    df_new['pixel'] = np.arange(2048)

    sp_ordering = df_new.groupby('superpixel').min().sort_values('pixel').index.values
    lookup = np.argsort(sp_ordering)
    df_new['superpixel'] = lookup[df_new['superpixel'].values]

    slot_ordering = df_new.groupby('slot').min().sort_values('pixel').index.values
    lookup = np.argsort(slot_ordering)
    df_new['slot'] = lookup[df_new['slot'].values]

    for itm in range(32):
        lookup = np.argsort(df_new.loc[df_new['slot'] == itm]['pixel'].values)
        df_new.loc[df_new['slot'] == itm, 'tmpix'] = lookup

    df_new.to_csv(output_path, sep='\t', float_format='%.7f', index=False)


def create_new_camera_cfg(tc_cfg_path, output_path):
    """
    Create a new sim_telarray camera cfg file using a TargetCalib mapping file
    """
    create_directory(os.path.dirname(output_path))

    mapping = Mapping(tc_cfg_path)
    mappingsp = mapping.GetMappingSP()

    with open(output_path, 'w') as f:
        write_PixType(f)
        write_pixel_positions(f, mapping)
        # write_trigger_groups_original(f, mapping, mappingsp)
        write_trigger_groups_unique(f, mapping, mappingsp)


def write_PixType(file):
    pixtype = """# PixType format:
# Par.  1: pixel type (here always 1)
#       2: PMT type (must be 0)
#       3: cathode shape type
#       4: visible cathode diameter [cm]
#       5: funnel shape type (see above)
#       6: funnel diameter (flat-to-flat for hex.) [cm]
#       7: depth of funnel [cm]
#       8: a) funnel efficiency "filename",   b) funnel plate transparency
#       9: a) optional wavelength "filename", b) funnel wall reflectivity
# In case a) in column 8, columns 3+7 are not used. If in case a) the
# optional file name for the wavelength dependence is provided, the
# overall scale in the file provided as parameter 8 is ignored because
# it is rescaled such that the average over all mirrors is equal to
# the given wavelength dependent value.
#
# Shape types: 0: circ., 1: hex(flat x), 2: sq., 3: hex(flat y)
#
#Angular Dep currently all set to one for checks

# Note that pixel size is scale from the actual 6.125 mm at the focal length
# planned with GATE telescopes (228.3 cm) to the focal length of ASTRI (215 cm).
# Similarly scaled are the pixel positions.
PixType    1 0 2 0.620   2 0.620 0.0   "funnel_perfect.dat"

# Pixel format:
# Par.  1: pixel number (starting at 0)
#       2: pixel type (must be 1)
#       3: x position [cm]
#       4: y position [cm]
#       5: drawer/module number
#       6: board number in module
#       7: channel number n board
#       8: board Id number ('0x....')
#       9: pixel on (is on if parameter is missing)
#       10: relative QE or PDE (1 if unused)
#       11: relative gain (1 if unused)

"""
    file.write(pixtype)


def write_pixel_positions(file, mapping):
    qe_arr = np.load('checs_qe_variation.npy')
    gain_arr = np.load('checs_gain_variation.npy')

    for i in range(mapping.GetNPixels()):
        ipix = mapping.GetPixel(i)
        xpix = mapping.GetXPix(i) * 10 ** 2
        ypix = mapping.GetYPix(i) * 10 ** 2
        imod = mapping.GetSlot(i)
        ichan = mapping.GetTMPixel(i)
        l = "Pixel\t{} 1\t {:.2f}\t{:.2f}\t{} 0 {}\t0x00 1\t{:.5f}\t{:.5f}\n"
        lf = l.format(ipix, xpix, ypix, imod, ichan, qe_arr[i], gain_arr[i])
        file.write(lf)

    file.write('\n')


def write_trigger_groups_original(file, mapping, mappingsp):
    for i in range(mappingsp.GetNSuperPixels()):
        nei = mappingsp.GetNeighbours(i, True)
        neisort = []
        for inei in nei:
            neirow = mappingsp.GetRow(inei)
            neicol = mappingsp.GetColumn(inei)
            neisort.append((neicol, neirow))
        sort = sorted(range(len(neisort)), key=neisort.__getitem__)
        nei = [nei[isort] for isort in sort]
        file.write("MajorityTrigger * of ")
        for isp in [i, *nei]:
            con = list(mappingsp.GetContainedPixels(isp))
            rows = [mapping.GetRow(j) for j in con]
            cols = [mapping.GetColumn(j) for j in con]
            min_r = np.min(rows)
            min_c = np.min(cols)
            con_bl = con[np.where((rows == min_r) & (cols == min_c))[0][0]]
            con.remove(con_bl)
            file.write('{}[{},{},{}] '.format(con_bl, *con))
        file.write('\n')


def write_trigger_groups_unique(file, mapping, mappingsp):
    pairs = []
    for i in range(mappingsp.GetNSuperPixels()):
        nei = mappingsp.GetNeighbours(i, True)
        neisort = []
        for inei in nei:
            neirow = mappingsp.GetRow(inei)
            neicol = mappingsp.GetColumn(inei)
            neisort.append((neicol, neirow))
        sort = sorted(range(len(neisort)), key=neisort.__getitem__)
        nei = [nei[isort] for isort in sort]

        for n in nei:
            pair = sorted((i, n))
            if pair not in pairs:
                pairs.append(pair)

    for p in pairs:
        file.write("MajorityTrigger * of ")
        for isp in p:
            con = list(mappingsp.GetContainedPixels(isp))
            rows = [mapping.GetRow(j) for j in con]
            cols = [mapping.GetColumn(j) for j in con]
            min_r = np.min(rows)
            min_c = np.min(cols)
            con_bl = con[np.where((rows == min_r) & (cols == min_c))[0][0]]
            con.remove(con_bl)
            file.write('{}[{},{},{}] '.format(con_bl, *con))
        file.write('\n')


def main():
    input_path = "/Users/Jason/Software/TargetCalib/source/dev/mapping_checs_V1-1-0.cfg"
    output_path = get_data("d181105_sim_telarray_cfg/tc_mapping.cfg")
    create_new_mapping(input_path, output_path)

    input_path = get_data("d181105_sim_telarray_cfg/tc_mapping.cfg")
    output_path = get_data("d181105_sim_telarray_cfg/pixel_mapping.dat")
    create_new_camera_cfg(input_path, output_path)


if __name__ == '__main__':
    main()
