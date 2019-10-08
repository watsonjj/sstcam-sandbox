from CHECLabPySB import get_astri_2019
from glob import glob
from subprocess import call


def process(name, file_lists):
    script = "/Users/Jason/Software/CHECOnsky/CHECOnsky/scripts_analysis/add_pointing_to_hillas.py"
    db_path = get_astri_2019("astri_db.h5")
    paths = " ".join([item for sublist in file_lists for item in sublist])
    cmd = f"python {script} -f {paths} -d {db_path} -s {name}"
    if name is None:
        cmd = f"python {script} -f {paths} -d {db_path}"
    call(cmd, shell=True)


def main():
    name = "mrk501"
    file_lists = [
        glob(get_astri_2019("d2019-05-01_mrk501/*_hillas.h5")),
        glob(get_astri_2019("d2019-05-02_mrk501/*_hillas.h5")),
        glob(get_astri_2019("d2019-05-06_mrk501/*_hillas.h5")),
        glob(get_astri_2019("d2019-06-12_mrk501/*_hillas.h5")),
        glob(get_astri_2019("d2019-06-12_mrk501_moonlight/*_hillas.h5")),
    ]
    process(name, file_lists)

    name = "mrk421"
    file_lists = [
        glob(get_astri_2019("d2019-05-02_mrk421/*_hillas.h5")),
        glob(get_astri_2019("d2019-05-09_mrk421/*_hillas.h5")),
        glob(get_astri_2019("d2019-06-12_mrk421_moonlight/*_hillas.h5")),
    ]
    process(name, file_lists)

    name = "PG1553+113"
    file_lists = [
        glob(get_astri_2019("d2019-05-02_PG1553+113/*_hillas.h5")),
    ]
    process(name, file_lists)

    # name = None
    # file_lists = [
    #     get_astri_2019("d2019-05-15_simulations/electron.h5"),
    #     get_astri_2019("d2019-05-15_simulations/proton.h5"),
    #     get_astri_2019("d2019-05-15_simulations/gamma_0deg.h5"),
    #     get_astri_2019("d2019-05-15_simulations/gamma_1deg.h5"),
    #     get_astri_2019("d2019-05-15_simulations/gamma_diffuse.h5"),
    #     get_astri_2019("d2019-05-15_simulations/muon.h5"),
    # ]
    # process(name, file_lists)


if __name__ == '__main__':
    main()
