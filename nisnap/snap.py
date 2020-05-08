
import logging as log
import tempfile, os

format = '.png'

def pick_labels(data, labels):
    import numpy as np
    data2 = np.where(np.isin(data, labels), data, 0)
    return data2

def aget_cmap(labels=[]):
    import json
    import numpy as np
    import nisnap
    import os.path as op
    n_labels = len(labels)
    fp = op.join(op.dirname(nisnap.__file__), 'utils', 'colormap.json')
    LUT = json.load(open(fp))
    LUT = {int(k): v for k,v in list(LUT.items())}

    if n_labels is None:
        n_labels = len(list(LUT.keys()))
    max_label = int(np.max(labels))
    LUT = [LUT.get(i, [0,0,0]) for i in range(0, max_label + 1)]
    LUT = np.array(LUT)
    LUT = LUT / 255.0
    return LUT

def plot_contours_in_slice(slice_seg, target_axis, labels=None):
    """Plots contour around the data in slice (after binarization)"""
    import numpy as np

    if labels is None: # if n_labels is not provided then take max from slice
        labels = list(np.unique(slice_seg))

    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(aget_cmap(labels))


    num_labels = len(cmap.colors)
    unique_labels = np.arange(num_labels, dtype='int16')

    from matplotlib import cm, colors
    normalize_labels = colors.Normalize(vmin=0, vmax=num_labels, clip=True)
    seg_mapper = cm.ScalarMappable(norm=normalize_labels, cmap=cmap)
    unique_labels_display = np.array(unique_labels) #np.setdiff1d(unique_labels, 0)

    color_for_label = seg_mapper.to_rgba(unique_labels_display)

    from matplotlib import pyplot as plt
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

def _snap_contours_(data, slices, axis, bg, figsize=None, bb=None, pbar=None):
    from matplotlib import pyplot as plt
    import numpy as np


    plt.style.use('dark_background')

    paths = []
    _, path = tempfile.mkstemp(suffix='_%s%s'%(axis, format))
    paths.append(path)


    same_box = not bb is None
    if not same_box:
        bb = {}

    lambdas = {'x': lambda y,x: y[:,:,x],
               'y': lambda y,x: y[:,x,:],
               'z': lambda y,x: y[x,:,:]}

    labels = list(np.unique(data))

    if figsize is None:
        ratio = len(slices) / float(len(slices[0]))
        figsize = (figsize, figsize * ratio)

    fig = plt.figure(dpi=300, figsize=figsize)

    abs_index = 0
    for a, chunk in enumerate(slices):
        if not same_box:
            bb[a] = []

        for i, slice_index in enumerate(chunk):
            abs_index += 1

            ax = fig.add_subplot(len(slices), len(slices[0]), abs_index,
                    label='%s_%s'%(axis, slice_index))
            test = np.flip(np.swapaxes(np.abs(lambdas[axis](data, int(slice_index))), 0, 1), 0)
            if not same_box:
                xs, ys = np.where(test!=0)
                bb[a].append((xs, ys))
            else:
                xs, ys = bb[a][i]

            if len(xs) == 0: continue

            test3 = np.flip(np.swapaxes(np.abs(lambdas[axis](bg, int(slice_index))), 0, 1), 0)
            test3 = test3[min(xs):max(xs) + 1, min(ys):max(ys) + 1]

            ax.imshow(test3, interpolation='none', cmap='gray')

            test = test[min(xs):max(xs) + 1, min(ys):max(ys) + 1]

            plot_contours_in_slice(test, ax, labels=labels)
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



def _snap_slices_(data, slices, axis, bb=None, figsize=None, pbar=None):
    from matplotlib import pyplot as plt
    import numpy as np


    labels = list(np.unique(data))
    has_bb = not bb is None
    has_orig = len(labels) > 100 #not bb is None

    paths = []
    if not has_bb:
        bb = {}

    fig = plt.figure(dpi=300, figsize=figsize)

    from nisnap.utils.slices import __get_lambdas__
    lambdas = __get_lambdas__(data)

    _, path = tempfile.mkstemp(suffix='_%s%s'%(axis, format))
    paths.append(path)

    abs_index = 0
    for a, chunk in enumerate(slices):

        if not has_bb:
            bb[a] = []

        for i, slice_index in enumerate(chunk):
            abs_index += 1
            ax = fig.add_subplot(len(slices), len(slices[0]), abs_index,
                    label='%s_%s'%(axis, slice_index))

            test = np.flip(np.swapaxes(np.abs(lambdas[axis](int(slice_index))), 0, 1), 0)
            if not has_bb:
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
                    vmax, cmap = (None, 'gray')
                else:
                    vmax = np.max(labels)
                    from matplotlib.colors import ListedColormap
                    cmap = ListedColormap(aget_cmap(labels))

                test = test[min(xs):max(xs) + 1, min(ys):max(ys) + 1]

                ax.imshow(test, interpolation='none', cmap=cmap,
                    vmin=0, vmax=vmax)


            ax.axis('off')
            ax.text(0, 0, '%i' %slice_index,
                {'color': 'w', 'fontsize': 10}, va="bottom", ha="left")

            if not pbar is None:
                pbar.update(1)

    fig.savefig(path, facecolor=fig.get_facecolor(),
            bbox_inches='tight', transparent=True, pad_inches=0)
    return paths, bb




def __snap__(data, axes='xyz', bg=None, slices=None, rowsize=None,
        contours=False, figsize=None, samebox=False):
    from matplotlib import pyplot as plt

    plt.rcParams['figure.facecolor'] = 'black'
    plt.rcParams.update({'figure.max_open_warning': 0})

    from nisnap.utils.slices import cut_slices, _fix_rowsize_, _fix_figsize_, __maxsize__
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

    from tqdm import tqdm
    pbar = tqdm(total=n_slices, leave=False)

    paths, paths_orig = {}, {}

    for axis in axes:
        if samebox:
            from nisnap.utils.slices import __get_abs_minmax
            same_bb = __get_abs_minmax(data, axis, slices[axis], margin = 5)
            log.warning('Using bounding box: %s (axis %s)'%(same_bb[0][0], axis))

        opt = {'slices': slices[axis],
               'axis': axis,
               'figsize': figsize[axis],
               'pbar': pbar}

        if contours:
            # Rendering contours
            if samebox:
                opt['bb'] = same_bb

            path, bb = _snap_contours_(data, bg=bg, **opt)
            paths[axis] = path

        else:
            opt['bb'] = None if not samebox else same_bb
            # Rendering masks
            path, bb = _snap_slices_(data, **opt)
            paths[axis] = path


        if has_orig:
            opt['bb'] = bb if not samebox else same_bb
            path, _ = _snap_slices_(bg, **opt)
            paths_orig[axis] = path

    pbar.update(n_slices)
    pbar.close()
    return paths, paths_orig


def __stack_img__(filepaths):
    import nibabel as nib
    import numpy as np

    stack = [np.asarray(nib.load(e).dataobj) for e in filepaths[:]]

    data = np.stack(stack, axis=-1)

    data2 = np.argmax(data, axis=-1) + 1
    black_pixels_mask = np.all(data == [0, 0, 0], axis=-1)
    data2[black_pixels_mask] = 0
    return data2


def plot_segment(filepaths, axes='xyz', bg=None, opacity=90, slices=None,
        animated=False, savefig=None, contours=False, rowsize=None,
        figsize=None, samebox=False, labels=None):
    """Plots a set of segmentation maps/masks.

    Parameters
    ----------
    filepaths: a list of str
        Paths to segmentation maps (between 1 and 3). Must be of same dimensions
        and in same reference space.

    axes: string, or a tuple of str
        Choose the direction of the cuts (among 'x', 'y', 'z')

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
        Default: {'x': 9, 'y': 9, 'z': 6}

    figsize: None, or float
        Figure size (in inches) (matplotlib definition). Default: auto

    samebox: boolean, optional
        If True, bounding box will be fixed. If False, adjusted for each slice.

    labels: None or a tuple of int
        If a list of labels is provided, the label volume will be filtered to
        keep these labels only and remove the others.
        (Works with a label volume only, not with RGB mode)

    See Also
    --------
    xnat.plot_segment : To plot segmentation maps directly providing their
        experiment_id on an XNAT instance
    """
    import matplotlib
    import numpy as np
    matplotlib.use('Agg')

    fp = savefig
    if savefig is None:
        if animated:
            f, fp = tempfile.mkstemp(suffix='.gif')
        else:
            f, fp = tempfile.mkstemp(suffix=format)
        os.close(f)

    from nisnap.utils.parse import __check_axes__
    axes = __check_axes__(axes)

    # Creating snapshots (along given axes and original if needed)
    log.info('* Creating snapshots...')

    # Loading images
    import nibabel as nib
    if isinstance(filepaths, list): # RGB mode
        data = __stack_img__(filepaths)
    elif isinstance(filepaths, str): # 3D label volume
        if not labels is None:
            from nisnap.utils import aseg
            filepaths = aseg.__picklabel_fs__(filepaths, labels=labels)
        data = np.asarray(nib.load(filepaths).dataobj)

    if bg is not None:
        bg = np.asarray(nib.load(bg).dataobj)

    paths, paths_orig = __snap__(data, axes=axes, bg=bg,
        slices=slices, contours=contours, rowsize=rowsize, figsize=figsize,
        samebox=samebox)

    from nisnap.utils.montage import __montage__
    has_orig = not bg is None
    __montage__(paths, paths_orig, axes, opacity, has_orig, animated, savefig=fp)


    if savefig is None:
        # Return image
        from IPython.display import Image
        return Image(filename=fp)
