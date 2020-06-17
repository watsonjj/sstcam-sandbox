from sstcam_sandbox import get_checs


class Dataset:
    def __init__(self, **kwargs):
        self.poi = 888


class MC(Dataset):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dl1_paths = [
            # get_checs("d190312_spectra_fitting/mc/run43490_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43491_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43492_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43493_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43494_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43495_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43496_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43497_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43498_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43499_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43500_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43501_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43502_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43503_dl1.h5"),
            # get_checs("d190312_spectra_fitting/mc/run43504_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43505_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43506_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43507_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43508_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43509_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43510_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43511_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43512_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43513_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43514_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43515_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43516_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43517_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43518_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43519_dl1.h5"),
            get_checs("d190312_spectra_fitting/mc/run43520_dl1.h5"),
        ]
        self.spe_config = get_checs("d190312_spectra_fitting/mc/spe_config.yml")