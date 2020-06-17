"""
Executable to compare the pixel positions and gap sizes for the CHEC and
ASTRI cameras by using the sim_telarray config files
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class Image:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.nrows = row.max() + 1
        self.ncols = col.max() + 1
        self.npix = row.size

        self.fig = None
        self.ax = None

    def plot(self, values, title):
        image = np.ma.zeros((self.nrows, self.ncols))
        image[self.row, self.col] = values
        # image[0:8, 40:48] = np.ma.masked
        # image[0:8, 0:8] = np.ma.masked
        # image[40:48, 0:8] = np.ma.masked
        # image[40:48, 40:48] = np.ma.masked

        self.fig = plt.figure(figsize=(10, 10))
        self.ax = self.fig.add_subplot(111)
        im = self.ax.imshow(image, origin='lower')
        self.fig.colorbar(im)
        self.fig.suptitle(title)

    def add_text(self, values, fmt=None, size=3):
        for pix in range(self.npix):
            pos_x = self.col[pix]
            pos_y = self.row[pix]
            val = values[pix]
            if fmt:
                val = fmt.format(val)
            self.ax.text(pos_x, pos_y, val, fontsize=size,
                         color='w', ha='center')

    def add_direction(self, axl, ayl, adx, ady):
        self.ax.arrow(axl, ayl, adx, ady, head_width=1, head_length=1,
                      fc='r', ec='r')
        text = "ON-Telescope UP"
        self.ax.text(axl, ayl, text, fontsize=8, color='r', ha='center',
                     va='bottom')

    def save(self, fn):
        self.fig.savefig("{}.pdf".format(fn), bbox_inches='tight')
        print("Figure created: {}".format(fn))


def get_pixsize(path):
    pixsize = 0
    with open(path) as file:
        for line in file:
            if line.startswith('#'):
                continue
            if "PixType" in line:
                pixsize = line.split()[4]
    pixsize = float(pixsize) * 1E2 * 1E-3
    return pixsize


def get_df(path):
    columns = ["type", "pixel_number", "pixel_type", "x_pos", "y_pos",
               "module", "board", "channel", "boardID", "pixel_on"]
    df = pd.read_table(path, delim_whitespace=True, header=None,
                       names=columns, skiprows=36, comment='#')
    df = df.loc[df['type'] == "Pixel"]
    df = df.apply(pd.to_numeric, errors='ignore')
    df['x_pos'] /= 100
    df['y_pos'] /= 100
    return df


def set_row_col(df):
    x = df['x_pos'].values
    y = df['y_pos'].values
    x_unique = np.unique(x)
    y_unique = np.unique(y)
    x_sep = np.diff(x_unique)
    y_sep = np.diff(y_unique)
    x_sep_max = np.max(x_sep)
    y_sep_max = np.max(y_sep)
    x_col_val = x_unique[x_unique.size//2]
    y_row_val = y_unique[y_unique.size//2]
    x_row_pixels = np.where((x > x_col_val-x_sep_max/4) &
                            (x < x_col_val + x_sep_max/4))[0]
    y_col_pixels = np.where((y > y_row_val-y_sep_max/4) &
                            (y < y_row_val + y_sep_max/4))[0]
    col_x_values = x[y_col_pixels]
    row_y_values = y[x_row_pixels]
    col_edges = np.append(col_x_values - x_sep_max/4,
                          col_x_values[-1] + x_sep_max/4)
    row_edges = np.append(row_y_values - y_sep_max/4,
                          row_y_values[-1] + y_sep_max/4)
    column = np.digitize(x, col_edges) - 1
    row = np.digitize(y, row_edges) - 1
    df['column'] = column
    df['row'] = row


def get_neighbours(df):
    row = df['row'].values
    column = df['column'].values

    diagonal = True
    row_sep = np.abs(row - row[:, None])
    col_sep = np.abs(column - column[:, None])
    neighbours = np.where(
        (row_sep <= 1) & (col_sep <= 1) & # Include all neighbouring pixels
        (~((row_sep == 0) & (col_sep == 0))) & # Remove self
        (~((row_sep == 1) & (col_sep == 1)) | diagonal)  # Remove diagonals
    )

    neighbours = np.array(neighbours)

    # Remove duplicate pairs
    neighbours = np.sort(neighbours.T, 1)
    b = np.ascontiguousarray(neighbours).view(
        np.dtype((np.void, neighbours.dtype.itemsize * neighbours.shape[1])))
    _, ind = np.unique(b, return_index=True)
    neighbours = neighbours[ind]

    return neighbours


def get_separation(df, neighbours):
    x = df['x_pos'].values
    y = df['y_pos'].values
    sep = np.sqrt((x[neighbours[:, 0]] - x[neighbours[:, 1]]) ** 2 +
                  (y[neighbours[:, 0]] - y[neighbours[:, 1]]) ** 2)
    return sep


def main():
    path_astri = "camera-astri-smart5-prod3.dat"
    path_chec = "camera_CHEC-S_GATE.dat"

    # Get pixel size
    # pixsize_astri = get_pixsize(path_astri)
    # pixsize_chec = get_pixsize(path_chec)
    pixsize_astri = 6.975E-3
    pixsize_chec = 6.2E-3

    # Load pixel positions
    df_astri = get_df(path_astri)
    df_chec = get_df(path_chec)

    # Set the row and columns based on pixel positions
    set_row_col(df_astri)
    set_row_col(df_chec)

    # Get the neighbouring pixels
    nei_astri = get_neighbours(df_astri)
    nei_chec = get_neighbours(df_chec)

    n_nei_astri = np.bincount(nei_astri.ravel())
    n_nei_chec = np.bincount(nei_chec.ravel())

    # Get the pixel seperation between neighbours
    sep_astri = get_separation(df_astri, nei_astri) - pixsize_astri
    sep_chec = get_separation(df_chec, nei_chec) - pixsize_chec

    i = Image(df_astri['row'].values, df_astri['column'].values)
    i.plot(n_nei_astri, "")
    i.add_text(n_nei_astri)
    i.save("n_nei_astri")

    i = Image(df_chec['row'].values, df_chec['column'].values)
    i.plot(n_nei_chec, "")
    i.add_text(n_nei_chec)
    i.save("n_nei_chec")

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.hist(sep_astri, bins=50, alpha=0.8, label="ASTRI")
    ax.hist(sep_chec, bins=50, alpha=0.8, label="CHEC")
    ax.legend(loc="upper right")
    fn = "seperation.pdf"
    fig.savefig(fn, bbox_inches='tight')
    print("Figure created: {}".format(fn))


if __name__ == '__main__':
    main()
