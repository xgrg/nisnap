import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

import tempfile, os
import numpy as np
import logging as log
import shutil
from collections.abc import Iterable
from tqdm import tqdm
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib import cm, colors


def _chunks_(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

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
        ctr_h = plt.contour(binary_slice_seg,
                            levels=[0.5,],
                            colors=(color_for_label[index],),
                            linewidths=1,
                            alpha=1,
                            zorder=1)

    return

def _snap_contours_(slices, axis, row_size, figsize, data, bg, pbar=None):
    plt.style.use('dark_background')

    paths = []
    bb = {}

    lambdas = {'A': lambda y,x: y[:,:,x],
               'C': lambda y,x: y[:,x,:],
               'S': lambda y,x: y[x,:,:]}

    n_labels = int(np.max(data))

    for a, chunk in enumerate(_chunks_(slices, row_size)):
        _, path = tempfile.mkstemp(prefix='%s%s_'%(axis, a), suffix='.png')
        paths.append(path)
        bb[a] = []

        fig = plt.figure(dpi=300, figsize=figsize)

        for i, slice_index in enumerate(chunk):
            ax = fig.add_subplot(1, len(chunk), i+1, label='slice_%s'%slice_index)
            test = np.flip(np.swapaxes(np.abs(lambdas[axis](data, int(slice_index))), 0, 1), 0)
            xs, ys = np.where(test!=0)

            bb[a].append((xs, ys))
            if len(xs) == 0: continue

            test3 = np.flip(np.swapaxes(np.abs(lambdas[axis](bg, int(slice_index))), 0, 1), 0)
            test3 = test3[min(xs):max(xs) + 1, min(ys):max(ys) + 1]
            ax.imshow(test3, interpolation='none', cmap='gray')

            test = test[min(xs):max(xs) + 1, min(ys):max(ys) + 1]

            plot_contours_in_slice(test, ax, n_labels = n_labels)
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


def _snap_slices_(data, slices, axis, row_size, figsize, bb=None, pbar=None):
    has_orig = not bb is None

    paths = []
    n_labels = int(np.max(data))
    if not has_orig:
        bb = {}

    if len(data.shape) == 4: # RGB mode
        lambdas = {'A': lambda x: data[:,:,x,:],
                   'C': lambda x: data[:,x,:,:],
                   'S': lambda x: data[x,:,:,:]}
    else: # standard label volume
        lambdas = {'A': lambda x: data[:,:,x],
                   'C': lambda x: data[:,x,:],
                   'S': lambda x: data[x,:,:]}

    for a, chunk in enumerate(_chunks_(slices, row_size)):
        _, path = tempfile.mkstemp(prefix='%s%s_'%(axis, a), suffix='.png')
        paths.append(path)

        if not has_orig:
            bb[a] = []

        fig = plt.figure(dpi=300, figsize=figsize)

        for i, slice_index in enumerate(chunk):

            ax = fig.add_subplot(1, len(chunk), i+1, label='slice_%s'%slice_index)
            test = np.flip(np.swapaxes(np.abs(lambdas[axis](int(slice_index))), 0, 1), 0)
            if not has_orig:
                xs, ys = np.where(test!=0)
                bb[a].append((xs, ys))
            else:
                xs, ys = bb[a][i]

            if len(xs) == 0: continue
            if len(data.shape) == 4:
                test = test[min(xs):max(xs) + 1, min(ys):max(ys) + 1, :]
                ax.imshow((test * 255).astype(np.uint8), interpolation='none', )
            else:
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




def __snap__(data, axes=('A', 'S', 'C'), bg=None, cut_coords=None,
        contours=False, figsize=None):

    has_orig = not bg is None

    plt.rcParams['figure.facecolor'] = 'black'
    plt.rcParams.update({'figure.max_open_warning': 0})

    paths, paths_orig = {}, {}

    slices = {'A': list(range(100, data.shape[2] - 60, 3)),
        'C': list(range(50, data.shape[1] - 70, 3)),
        'S': list(range(90, data.shape[0] - 90, 1))}

    row_sizes = {'A': 9, 'C': 9, 'S':6}

    if figsize is None:
        figsizes = {'A': (37, 3), 'C': (40, 3), 'S': (18, 3)}
    elif isinstance(figsize, (list, tuple)) and len(figsize) == 2:
        figsizes = {each: figsize for each in axes}
    else:
        raise TypeError('figsize should be a tuple/list of size 2')

    if not cut_coords is None:
        if isinstance(cut_coords, dict):
            slices = {e: list(cut_coords[e]) for e in axes}
            row_sizes = {e: len(cut_coords[e]) for e in axes}
            figsizes = {e: (3*len(cut_coords[e]), 3) for e in axes}
        elif isinstance(cut_coords, Iterable):
            slices = {'A': cut_coords, 'S': cut_coords, 'C': cut_coords}
            lc = len(cut_coords)
            row_sizes = {'A': lc, 'S': lc, 'C': lc}
            figsizes = {e: (3*lc, 3) for e in axes}

    n_slices = sum([len(slices[e]) for e in axes])
    if has_orig:
        n_slices = 2 * n_slices

    pbar = tqdm(total=n_slices, leave=False)
    for each in axes:
        if contours:
            # Rendering contours
            path, bb = _snap_contours_(slices[each], axis=each, row_size=row_sizes[each],
                figsize=figsizes.get(each, None), data=data,
                bg=bg, pbar=pbar)
            paths[each] = path

        else:
            # Rendering RGB maps
            path, bb = _snap_slices_(data, slices[each], axis=each, row_size=row_sizes[each],
                figsize=figsizes.get(each, None), bb=None, pbar=pbar)
            paths[each] = path

        if has_orig:
            path, _ = _snap_slices_(bg, slices[each], axis=each, row_size=row_sizes[each],
                figsize=figsizes.get(each, None), bb=bb,
                pbar=pbar)
            paths_orig[each] = path

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

def __plot_segment__(filepaths, axes=('A','C','S'), bg=None, opacity=30,
        animated=False, cut_coords=None, savefig=None, contours=False,
        figsize=None):
    has_orig = not bg is None

    width = 2000
    f, fp = tempfile.mkstemp(suffix='.png')
    os.close(f)

    # Creating snapshots (along given axes and original if needed)
    log.info('* Creating snapshots...')

    # Loading images

    import nibabel as nib
    if isinstance(filepaths, list):
        data = __stack_img__(filepaths)
    elif isinstance(filepaths, str):
        data = np.asarray(nib.load(filepaths).dataobj)
    if bg is not None:
        bg = np.asarray(nib.load(bg).dataobj)

    paths, paths_orig = __snap__(data, axes=axes, bg=bg,
        cut_coords=cut_coords, contours=contours, figsize=figsize)

    montage_cmd = 'montage -resize %sx -tile 1 -background black -geometry +0+0 %s %s'%(width, '%s', '%s')
    # Compiling images into a single one (one per axis)
    for each in axes:
        cmd = montage_cmd%(' '.join(paths[each]), fp.replace('.png', '_%s.png'%each))
        log.debug(cmd)
        os.system(cmd)
        for e in paths[each]:
            os.unlink(e) # Delete individual snapshots

    # Create one image with the selected axes

    import os.path as op
    cmd = montage_cmd%(' '.join([fp[:-4] + '_%s.png'%each for each in axes]), fp)
    log.debug(cmd)
    os.system(cmd)
    log.debug([fp[:-4] + '_%s.png'%each for each in axes])
    log.debug([op.isfile(fp[:-4] + '_%s.png'%each) for each in axes])
    #log.info('Saved in %s'%fp)
    for each in axes:
        fp1 = fp[:-4] + '_%s.png'%each
        if op.isfile(fp1):
            os.unlink(fp1)
        else:
            from glob import glob
            log.warning('%s not found. %s'%(fp1, glob('/tmp/tmp*.png')))

    if has_orig:
        # Repeat the process (montage) with the "raw" snapshots
        for each in axes:
            cmd = montage_cmd%(' '.join(paths_orig[each]), fp[:-4] + '_orig_%s.png'%each)
            log.debug(cmd)
            os.system(cmd)
            for e in paths_orig[each]:
                os.unlink(e)

        # Create one image with the selected axes
        cmd = montage_cmd%(' '.join([fp[:-4] + '_orig_%s.png'%each for each in axes]),
                fp[:-4] + '_orig.png')
        log.debug(cmd)
        os.system(cmd)
        #log.info('Saved in %s'%fp.replace('.png', '_orig.png'))
        for each in axes:
            os.unlink(fp[:-4] + '_orig_%s.png'%each)


    # At this point there should be two images max. (segmentation and raw image)
    composite_cmd = 'composite -dissolve %s -gravity Center %s %s -alpha Set %s'

    if has_orig:
        if animated: # will generate a .gif

            # Fading from raw data to segmentation
            l = list(range(0, opacity, int(opacity/10.0)))
            pbar = tqdm(total=2*len(l), leave=False)
            for i, opac in enumerate(l):
                cmd = composite_cmd %(opac, fp, fp[:-4] + '_orig.png',
                        fp[:-4] + '_fusion_%03d.png'%i)
                log.debug(cmd)
                os.system(cmd)
                pbar.update(1)

            # From segmentation to raw data
            for i, opac in enumerate(l):
                cmd = composite_cmd %(opacity - opac, fp, fp[:-4] + '_orig.png',
                        fp[:-4] + '_fusion_%03d.png'%(len(l)+i))
                log.debug(cmd)
                os.system(cmd)
                pbar.update(1)

            pbar.update(2*len(l))
            pbar.close()

            # Collect frames and create gif
            filepaths = []
            for i, opac in enumerate(range(0, 2 * opacity, int(opacity/10.0))):
                filepaths.append(fp[:-4] + '_fusion_%03d.png'%i)

            cmd = 'convert -delay 0 -loop 0 %s %s'\
                %(' '.join(filepaths), fp[:-4] + '.gif')
            log.debug(cmd)
            os.system(cmd)
            #log.info('Saved in %s'%fp.replace('.png', '.gif'))

            #Removing fusions (jpeg files)
            for each in filepaths:
                os.unlink(each)
            os.unlink(fp)
            os.unlink(fp[:-4] + '_orig.png')

        else:
            # Blends the two images (segmentation and original) into a composite one
            cmd = composite_cmd %(opacity, fp, fp[:-4] + '_orig.png',
                    fp[:-4] + '_fusion.png')
            log.debug(cmd)
            os.system(cmd)

            os.unlink(fp)
            os.unlink(fp[:-4] + '_orig.png')

    # Cleaning and saving files in right location

    if has_orig:
        if animated:
            if not savefig is None:
                shutil.move(fp[:-4] + '.gif', savefig)
                log.info('Saved in %s'%savefig)

        else:
            if not savefig is None:
                shutil.move(fp[:-4] + '_fusion.png', savefig)
                log.info('Saved in %s'%fp)
            else:
                shutil.move(fp[:-4] + '_fusion.png', fp)
                log.info('Saved in %s'%fp)

    else:
        if not savefig is None:
            shutil.move(fp, savefig)
            log.info('Saved in %s'%savefig)



def __check_axes__(axes):
    is_correct = True
    curated_axes = []
    ax_names = ('A', 'S', 'C', 'AXIAL', 'SAGITTAL', 'CORONAL')
    if ((isinstance(axes, str) or isinstance(axes, Iterable)) \
            and len(axes) > 0 and len(axes) < 4):
        for e in axes:
            if not e.upper() in ax_names:
                is_correct = False
            else:
                curated_axes.append(e.upper())
    else:
        is_correct = False

    msg = 'axes should be a single character or an Iterable with the'\
        ' following: %s'%', '.join(ax_names)
    if not is_correct:
        log.warning('Axes: %s (%s)'%(axes, type(axes)))
        raise ValueError(msg)
    return tuple(curated_axes)


def plot_segment(filepaths, axes=('A','C','S'), bg=None, opacity=30, cut_coords=None,
        animated=False, savefig=None, contours=False, figsize=None):
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

    cut_coords: None, or a tuple of floats
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

    figsize: None, or a 2-uple of floats
        Sets the figure size. Default: {'A': (37, 3), 'C': (40, 3), 'S': (18, 3)}


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
            f, fp = tempfile.mkstemp(suffix='.png')
        os.close(f)

    axes = __check_axes__(axes)
    __plot_segment__(filepaths, axes=axes, bg=bg, opacity=opacity, cut_coords=cut_coords,
        animated=animated, savefig=fp, contours=contours, figsize=figsize)


    if savefig is None:
        # Return image
        from IPython.display import Image
        return Image(filename=fp)
