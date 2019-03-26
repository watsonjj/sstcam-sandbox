import numpy as np
from ctapipe.instrument.camera import _get_min_pixel_seperation


def _rectangular_pixel_row_column(pix_x, pix_y):
    """
    Get the row and column of rectangular pixels of a camera that are
    arranged in a grid
     The cameras in CTA with rectangular pixels have a curved focal plane
    surface. Pixels on a curved focal surface do not have consistent x and y
    coordinates along a single row or column. Therefore, a somewhat
    reliable technique to obtain the row and column is to define bin edges
    which the pixels are presumed to be within.
     This function first finds a row and column of the camera which contains a
    full set of pixels. The coordinates of these pixels are then used to
    define the bin edges for the entire camera.
     Parameters
    ----------
    pix_x : ndarray
        X coordinates of camera pixels
    pix_y : ndarray
        Y coordinates of camera pixels
     Returns
    -------
    row : ndarray
        Row for each camera pixel
    column : ndarray
        Column for each camera pixel
     """
    # Estimate the maximum number of rows and columns of pixels
    dist = _get_min_pixel_seperation(pix_x, pix_y)
    max_nrow = int(np.ceil((pix_y.max() - pix_y.min()) / dist)) + 1
    max_ncol = int(np.ceil((pix_x.max() - pix_x.min()) / dist)) + 1

    # Bin the pixel positions on a 2D grid
    hist_x = np.histogram2d(pix_x, pix_y, weights=pix_x, bins=[max_ncol, max_nrow])[0]
    hist_y = np.histogram2d(pix_x, pix_y, weights=pix_y, bins=[max_ncol, max_nrow])[0]
    hist_xc = np.histogram2d(pix_x, pix_y, bins=[max_ncol, max_nrow])[0]
    hist_yc = np.histogram2d(pix_x, pix_y, bins=[max_ncol, max_nrow])[0]
    # Find row and col with a complete number of pixels along them
    full_col = np.bincount(hist_x.nonzero()[0]).argmax()
    full_row = np.bincount(hist_y.nonzero()[0]).argmax()
    # Obtain coordinates of the pixels along this row and column
    full_x = hist_x[:, full_col][hist_xc[:, full_col].nonzero()]
    full_y = hist_y[full_row, :][hist_yc[full_row, :].nonzero()]

    # Define pixel bin edges based on full row and column of pixels
    mid_dist = _get_min_pixel_seperation(full_x, full_y) / 2
    edges_x = np.array([*(full_x - mid_dist), full_x[-1] + mid_dist])
    edges_y = np.array([*(full_y - mid_dist), full_y[-1] + mid_dist])

    # Obtain the corresponding row and column bin for each pixel
    column = np.digitize(pix_x, edges_x) - 1
    row = np.digitize(pix_y, edges_y) - 1

    return row, column
