import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import logging as log
import tempfile, os
import numpy as np
from tqdm import tqdm
from matplotlib.colors import ListedColormap
from matplotlib import cm, colors

format = '.png'

def aget_cmap(n_labels=None):
    LUT = {0:  [0,   0,   0],
           1:  [70,  130, 180],
           2:  [205, 62,  78],
           3:  [245, 245, 245],
           4:  [120, 18,  134],
           5:  [196, 58,  250],
           6:  [0,   148, 0],
           7:  [220, 248, 164],
           8:  [230, 148, 34],
           9:  [0,   118, 14],
           10: [0,   118, 14],
           11: [122, 186, 220],
           12: [236, 13,  176],
           13: [12,  48,  255],
           14: [204, 182, 142],
           15: [42,  204, 164],
           16: [119, 159, 176]}

    if n_labels is None:
        n_labels = len(list(LUT.keys()))
    LUT = [LUT[i] for i in range(0, n_labels+1)]
    LUT = np.array(LUT)
    LUT = LUT / 255.0
    return LUT

def plot_contours_in_slice(slice_seg, target_axis, n_labels=None):
    """Plots contour around the data in slice (after binarization)"""

    if n_labels is None: # if n_labels is not provided then take max from slice
        n_labels = int(np.max(slice_seg))

    cmap = ListedColormap(aget_cmap(n_labels))

    num_labels = len(cmap.colors)
    unique_labels = np.arange(num_labels, dtype='int16')

    normalize_labels = colors.Normalize(vmin=0, vmax=num_labels, clip=True)
    seg_mapper = cm.ScalarMappable(norm=normalize_labels, cmap=cmap)
    unique_labels_display = np.setdiff1d(unique_labels, 0)
    color_for_label = seg_mapper.to_rgba(unique_labels_display)

    plt.sca(target_axis)

    for index, label in enumerate(unique_labels_display):
        binary_slice_seg = slice_seg == index
        if not binary_slice_seg.any():
            continue
        plt.contour(binary_slice_seg,
            levels=[0.5,],
            colors=(color_for_label[index],),
            linewidths=1,
            alpha=1,
            zorder=1)

    return

def _snap_contours_(data, slices, axis, bg, figsize=None, pbar=None):
    plt.style.use('dark_background')

    paths = []
    _, path = tempfile.mkstemp(suffix='_%s%s'%(axis, format))
    paths.append(path)

    bb = {}

    lambdas = {'A': lambda y,x: y[:,:,x],
               'C': lambda y,x: y[:,x,:],
               'S': lambda y,x: y[x,:,:]}

    n_labels = int(np.max(data))

    if figsize is None:
        ratio = len(slices) / float(len(slices[0]))
        figsize = (figsize, figsize * ratio)

    fig = plt.figure(dpi=300, figsize=figsize)

    abs_index = 0
    for a, chunk in enumerate(slices):
        bb[a] = []

        for i, slice_index in enumerate(chunk):
            abs_index += 1

            ax = fig.add_subplot(len(slices), len(slices[0]), abs_index,
                    label='%s_%s'%(axis, slice_index))
            test = np.flip(np.swapaxes(np.abs(lambdas[axis](data, int(slice_index))), 0, 1), 0)
            xs, ys = np.where(test!=0)

            bb[a].append((xs, ys))
            if len(xs) == 0: continue

            test3 = np.flip(np.swapaxes(np.abs(lambdas[axis](bg, int(slice_index))), 0, 1), 0)
            test3 = test3[min(xs):max(xs) + 1, min(ys):max(ys) + 1]
            ax.imshow(test3, interpolation='none', cmap='gray')

            test = test[min(xs):max(xs) + 1, min(ys):max(ys) + 1]

            plot_contours_in_slice(test, ax, n_labels=n_labels)
            ax.axis('off')

            ax.text(0, 0, '%i' %slice_index,
                {'color': 'w', 'fontsize': 10}, va="bottom", ha="left")

            if not pbar is None:
                pbar.update(1)

    fig.savefig(path, facecolor=fig.get_facecolor(),
            bbox_inches='tight',
            transparent=True,
            pad_inches=0)
    return paths, bb


def __get_lambdas__(data):
    if len(data.shape) == 4: # RGB mode (4D volume)
        lambdas = {'A': lambda x: data[:,:,x,:],
                   'C': lambda x: data[:,x,:,:],
                   'S': lambda x: data[x,:,:,:]}
    else: # standard 3D label volume
        lambdas = {'A': lambda x: data[:,:,x],
                   'C': lambda x: data[:,x,:],
                   'S': lambda x: data[x,:,:]}
    return lambdas


def _snap_slices_(data, slices, axis, bb=None, figsize=None, pbar=None):
    has_orig = not bb is None

    paths = []
    n_labels = int(np.max(data))
    if not has_orig:
        bb = {}

    lambdas = __get_lambdas__(data)

    fig = plt.figure(dpi=300, figsize=figsize)

    _, path = tempfile.mkstemp(suffix='_%s%s'%(axis, format))
    paths.append(path)

    abs_index = 0
    for a, chunk in enumerate(slices):

        if not has_orig:
            bb[a] = []

        for i, slice_index in enumerate(chunk):
            abs_index += 1
            ax = fig.add_subplot(len(slices), len(slices[0]), abs_index,
                    label='%s_%s'%(axis, slice_index))

            test = np.flip(np.swapaxes(np.abs(lambdas[axis](int(slice_index))), 0, 1), 0)
            if not has_orig:
                xs, ys = np.where(test!=0)
                bb[a].append((xs, ys))
            else:
                xs, ys = bb[a][i]

            if len(xs) == 0: continue

            if len(data.shape) == 4: # RGB mode (4D volume)
                test = test[min(xs):max(xs) + 1, min(ys):max(ys) + 1, :]
                ax.imshow((test * 255).astype(np.uint8), interpolation='none', )

            else: # standard 3D label volume
                if has_orig:
                    cmap = 'gray'
                else:
                    cmap = ListedColormap(aget_cmap(n_labels))

                test = test[min(xs):max(xs) + 1, min(ys):max(ys) + 1]
                ax.imshow(test, interpolation='none', cmap=cmap)

            ax.axis('off')
            ax.text(0, 0, '%i' %slice_index,
                {'color': 'w', 'fontsize': 10}, va="bottom", ha="left")

            if not pbar is None:
                pbar.update(1)

    fig.savefig(path, facecolor=fig.get_facecolor(),
            bbox_inches='tight', transparent=True, pad_inches=0)
    return paths, bb




def __snap__(data, axes=('A', 'S', 'C'), bg=None, slices=None, rowsize=None,
        contours=False, figsize=None):

    plt.rcParams['figure.facecolor'] = 'black'
    plt.rcParams.update({'figure.max_open_warning': 0})

    from nisnap._slices import cut_slices, _fix_rowsize_, _fix_figsize_, __maxsize__
    rowsize = _fix_rowsize_(axes, rowsize)
    figsize = _fix_figsize_(axes, figsize)

    t = int(__maxsize__(data)/3.0)
    slices = cut_slices(data, axes, slices=slices, rowsize=rowsize,
        threshold=t)
    n_slices = sum([sum([len(each) for each in slices[e]]) for e in axes])
    if n_slices == 0:
        msg = 'Should provide at least one slice. %s'%slices
        raise Exception(msg)
    has_orig = not bg is None



    if has_orig:
        n_slices = 2 * n_slices
    pbar = tqdm(total=n_slices, leave=False)

    paths, paths_orig = {}, {}

    for axis in axes:

        if contours:
            # Rendering contours
            path, bb = _snap_contours_(data,
                slices[axis], axis=axis, bg=bg, figsize=figsize[axis], pbar=pbar)
            paths[axis] = path

        else:
            # Rendering masks
            path, bb = _snap_slices_(data,
                slices[axis], axis=axis, bb=None, figsize=figsize[axis], pbar=pbar)
            paths[axis] = path

        if has_orig:
            path, _ = _snap_slices_(bg,
                slices[axis], axis=axis, bb=bb, figsize=figsize[axis], pbar=pbar)
            paths_orig[axis] = path

    pbar.update(n_slices)
    pbar.close()
    return paths, paths_orig


def __stack_img__(filepaths):
    import nibabel as nib
    stack = [np.asarray(nib.load(e).dataobj) for e in filepaths[:]]

    data = np.stack(stack, axis=-1)

    data2 = np.argmax(data, axis=-1) + 1
    black_pixels_mask = np.all(data == [0, 0, 0], axis=-1)
    data2[black_pixels_mask] = 0
    return data2


def plot_segment(filepaths, axes=('A','C','S'), bg=None, opacity=30, slices=None,
        animated=False, savefig=None, contours=False, rowsize=None,
        figsize=None):
    """Plots a set of segmentation maps/masks.

    Parameters
    ----------
    filepaths: a list of str
        Paths to segmentation maps (between 1 and 3). Must be of same dimensions
        and in same reference space.

    axes: string, or a tuple of strings
        Choose the direction of the cuts (among 'A', 'S', 'C', 'AXIAL',
        'SAGITTAL' or 'CORONAL', or lowercase)

    bg: None or str
        Path to the background image that the masks will be plotted on top of.
        If nothing is specified, the segmentation maps/masks will be plotted only.
        The opacity (in %) of the segmentation maps when plotted over a background
        image. Only used if a background image is provided. Default: 10

    slices: None, or a tuple of floats
        The indexes of the slices that will be rendered. If None is given, the
        slices are selected automatically.

    animated: boolean, optional
        If True, the snapshot will be rendered as an animated GIF.
        If False, the snapshot will be rendered as a static PNG image. Default:
        False

    savefig: string, optional
        Filepath where the resulting snapshot will be created. If None is given,
        a temporary file will be created and/or the result will be displayed
        inline in a Jupyter Notebook.

    contours: boolean, optional
        If True, segmentations will be rendered as contoured regions. If False,
        will be rendered as superimposed masks. Default: False

    rowsize: None, or int, or dict
        Set the number of slices per row in the final compiled figure.
        Default: {'A': 9, 'C': 9, 'S': 6}

    figsize: None, or float
        Figure size (in inches) (matplotlib definition). Default: auto


    See Also
    --------
    xnat.plot_segment : To plot segmentation maps directly providing their
        experiment_id on an XNAT instance
    """
    fp = savefig
    if savefig is None:
        if animated:
            f, fp = tempfile.mkstemp(suffix='.gif')
        else:
            f, fp = tempfile.mkstemp(suffix=format)
        os.close(f)

    from nisnap._parse import __check_axes__
    axes = __check_axes__(axes)

    # Creating snapshots (along given axes and original if needed)
    log.info('* Creating snapshots...')

    # Loading images
    import nibabel as nib
    if isinstance(filepaths, list): # RGB mode
        data = __stack_img__(filepaths)
    elif isinstance(filepaths, str): # 3D label volume
        data = np.asarray(nib.load(filepaths).dataobj)

    if bg is not None:
        bg = np.asarray(nib.load(bg).dataobj)

    paths, paths_orig = __snap__(data, axes=axes, bg=bg,
        slices=slices, contours=contours, rowsize=rowsize, figsize=figsize)

    from nisnap._montage import __montage__
    has_orig = not bg is None
    __montage__(paths, paths_orig, axes, opacity, has_orig, animated, savefig=fp)


    if savefig is None:
        # Return image
        from IPython.display import Image
        return Image(filename=fp)
