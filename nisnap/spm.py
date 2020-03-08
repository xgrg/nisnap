import matplotlib
matplotlib.use('Agg')

import nibabel as nib
import tempfile, os
import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm
import logging as log
import shutil


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def snap_slices(slices, axis, row_size, figsize, func, pbar=None):

    paths = []
    bb = {}

    for a, chunk in enumerate(chunks(slices, row_size)):
        _, path = tempfile.mkstemp(prefix='%s%s_'%(axis, a), suffix='.png')
        paths.append(path)
        bb[a] = []

        fig = plt.figure(dpi=300, figsize=figsize)

        for i, slice_index in enumerate(chunk):
            ax = fig.add_subplot(1, len(chunk), i+1, label='slice_%s'%slice_index)
            test = np.flip(np.swapaxes(np.abs(func(int(slice_index))), 0, 1), 0)
            xs, ys, zs = np.where(test!=0)
            bb[a].append((xs, ys, zs))

            if len(xs) == 0: continue
            test = test[min(xs):max(xs) + 1, min(ys):max(ys) + 1, :]

            ax.imshow((test * 255).astype(np.uint8), interpolation='none', )
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


def snap_slices_orig(slices, axis, row_size, figsize, func, bb, pbar=None):

    paths = []

    for a, chunk in enumerate(chunks(slices, row_size)):
        _, path = tempfile.mkstemp(prefix='%s%s_'%(axis, a), suffix='.png')
        paths.append(path)

        fig = plt.figure(dpi=300, figsize=figsize)
        for i, slice_index in enumerate(chunk):
            ax = fig.add_subplot(1, len(chunk), i+1, label='slice_%s'%slice_index)
            test = np.flip(np.swapaxes(np.abs(func(int(slice_index))), 0, 1), 0)
            xs, ys, zs = bb[a][i]

            if len(xs) == 0: continue
            test = test[min(xs):max(xs) + 1, min(ys):max(ys) + 1]

            ax.imshow(test, interpolation='none', cmap='gray')
            ax.axis('off')

            ax.text(0, 0, '%i' %slice_index,
                {'color': 'w', 'fontsize': 10}, va="bottom", ha="left")

            if not pbar is None:
                pbar.update(1)

        fig.savefig(path, facecolor=fig.get_facecolor(),
                bbox_inches='tight',
                transparent=True,
                pad_inches=0)
    return paths



def __snap__(filepaths, axes=('A', 'S', 'C'), bg=None, cut_coords=None,
        figsize=None):
    from collections.abc import Iterable
    orig = not bg is None
    c = nib.load(filepaths[0]).dataobj.shape

    stack = [np.asarray(nib.load(e).dataobj) for e in filepaths[:]]
    while len(stack) < 3:
        stack.append(np.zeros(c))

    data = np.stack(stack, axis=-1)
    if orig:
        orig_data = np.asarray(nib.load(bg).dataobj)

    plt.rcParams['figure.facecolor'] = 'black'
    plt.rcParams.update({'figure.max_open_warning': 0})

    paths = {}
    paths_orig = {}
    slices = {'A': list(range(100, data.shape[2] - 60, 3)),
        'C': list(range(50, data.shape[1] - 70, 3)),
        'S': list(range(90, data.shape[0] - 90, 1))}

    row_sizes = {'A': 9, 'C': 9, 'S':6}

    if figsize is None:
        figsizes = {'A': (37, 3), 'C': (40, 3), 'S': (18, 3)}
    elif isinstance(figsize, (list,tuple)) and len(figsize) == 2:
        figsizes = {each: figsize for each in axes}
    else:
        raise TypeError('figsize should be a tuple/list of size 2')

    if not cut_coords is None:
        print(cut_coords, axes)
        if isinstance(cut_coords, dict):
            slices = {e: list(cut_coords[e]) for e in axes}
            row_sizes = {e: len(cut_coords[e]) for e in axes}
            figsizes = {e: (3*len(cut_coords[e]), 3) for e in axes}
        elif isinstance(cut_coords, Iterable):
            slices = {'A': cut_coords, 'S': cut_coords, 'C': cut_coords}
            lc = len(cut_coords)
            row_sizes = {'A': lc, 'S': lc, 'C': lc}
            figsizes = {e: (3*lc, 3) for e in axes}



    lambdas = {'A': lambda x: data[:,:,x,:],
               'C': lambda x: data[:,x,:,:],
               'S': lambda x: data[x,:,:,:]}

    lambdas_orig = {'A': lambda x: orig_data[:,:,x],
               'C': lambda x: orig_data[:,x,:],
               'S': lambda x: orig_data[x,:,:]}

    n_slices = sum([len(slices[e]) for e in axes])
    if orig:
        n_slices = 2 * n_slices

    pbar = tqdm(total=n_slices, leave=False)
    for each in axes:
        print([each, 'slices:', slices, slices[each]])
        path, bb = snap_slices(slices[each], axis=each, row_size=row_sizes[each],
            figsize=figsizes.get(each, None), func=lambdas[each], pbar=pbar)
        paths[each] = path

        if orig:
            path = snap_slices_orig(slices[each], axis=each, row_size=row_sizes[each],
                figsize=figsizes.get(each, None), func=lambdas_orig[each], bb=bb,
                pbar=pbar)
            paths_orig[each] = path

    pbar.update(n_slices)
    pbar.close()
    return paths, paths_orig




def __plot_segment__(filepaths, axes=('A','C','S'), bg=None, opacity=30,
        animated=False, cut_coords=None, savefig=None, figsize=None):
    orig = not bg is None
    # FIXME: be careful if a file contains .gif or .png elsewhere

    width = 2000
    f, fp = tempfile.mkstemp(suffix='.png')
    os.close(f)

    # Creating snapshots (along given axes and original if needed)
    log.info('* Creating snapshots...')
    paths, paths_orig = __snap__(filepaths, axes=axes, bg=bg,
        cut_coords=cut_coords, figsize=figsize)

    montage_cmd = 'montage -resize %sx -tile 1 -background black -geometry +0+0 %s %s'%(width, '%s', '%s')
    # Compiling images into a single one (one per axis)
    for each in axes:
        cmd = montage_cmd%(' '.join(paths[each]), fp.replace('.png', '_%s.png'%each))
        log.debug(cmd)
        os.system(cmd)
        for e in paths[each]:
            os.unlink(e) # Delete individual snapshots

    # Create one image with the selected axes

    cmd = montage_cmd%(' '.join([fp.replace('.png', '_%s.png'%each) for each in axes]), fp)
    log.debug(cmd)
    os.system(cmd)
    import os.path as op
    log.debug([fp.replace('.png', '_%s.png'%each) for each in axes])
    log.debug([op.isfile(fp.replace('.png', '_%s.png'%each)) for each in axes])
    #log.info('Saved in %s'%fp)
    for each in axes:
        fp1 = fp.replace('.png', '_%s.png'%each)
        if op.isfile(fp1):
            os.unlink(fp1)
        else:
            from glob import glob
            log.warning('%s not found. %s'%(fp1, glob('/tmp/tmp*.png')))

    if orig:
        # Repeat the process (montage) with the "raw" snapshots
        for each in axes:
            cmd = montage_cmd%(' '.join(paths_orig[each]), fp.replace('.png', '_orig_%s.png'%each))
            log.debug(cmd)
            os.system(cmd)
            for e in paths_orig[each]:
                os.unlink(e)

        # Create one image with the selected axes
        cmd = montage_cmd%(' '.join([fp.replace('.png', '_orig_%s.png'%each) for each in axes]),
                fp.replace('.png', '_orig.png'))
        log.debug(cmd)
        os.system(cmd)
        #log.info('Saved in %s'%fp.replace('.png', '_orig.png'))
        for each in axes:
            os.unlink(fp.replace('.png', '_orig_%s.png'%each))


    # At this point there should be two images max. (segmentation and raw image)
    composite_cmd = 'composite -dissolve %s -gravity Center %s %s -alpha Set %s'

    if orig:
        if animated: # will generate a .gif

            # Fading from raw data to segmentation
            l = list(range(0, opacity, int(opacity/10.0)))
            pbar = tqdm(total=2*len(l), leave=False)
            for i, opac in enumerate(l):
                cmd = composite_cmd %(opac, fp, fp.replace('.png', '_orig.png'),
                        fp.replace('.png', '_fusion_%03d.png'%i))
                log.debug(cmd)
                os.system(cmd)
                pbar.update(1)

            # From segmentation to raw data
            for i, opac in enumerate(l):
                cmd = composite_cmd %(opacity - opac, fp, fp.replace('.png', '_orig.png'),
                        fp.replace('.png', '_fusion_%03d.png'%(len(l)+i)))
                log.debug(cmd)
                os.system(cmd)
                pbar.update(1)

            pbar.update(2*len(l))
            pbar.close()

            # Collect frames and create gif
            filepaths = []
            for i, opac in enumerate(range(0, 2 * opacity, int(opacity/10.0))):
                filepaths.append(fp.replace('.png', '_fusion_%03d.png'%i))

            cmd = 'convert -delay 0 -loop 0 %s %s'\
                %(' '.join(filepaths), fp.replace('.png', '.gif'))
            log.debug(cmd)
            os.system(cmd)
            #log.info('Saved in %s'%fp.replace('.png', '.gif'))

            #Removing fusions (jpeg files)
            for each in filepaths:
                os.unlink(each)
            os.unlink(fp)
            os.unlink(fp.replace('.png', '_orig.png'))

        else:
            # Blends the two images (segmentation and original) into a composite one
            cmd = composite_cmd %(opacity, fp, fp.replace('.png', '_orig.png'),
                    fp.replace('.png', '_fusion.png'))
            log.debug(cmd)
            os.system(cmd)

            os.unlink(fp)
            os.unlink(fp.replace('.png', '_orig.png'))

    # Cleaning and saving files in right location

    if orig:
        if animated:
            if not savefig is None:
                shutil.move(fp.replace('.png', '.gif'), savefig)
                log.info('Saved in %s'%savefig)

        else:
            if not savefig is None:
                shutil.move(fp.replace('.png', '_fusion.png'), savefig)
                log.info('Saved in %s'%fp)
            else:
                shutil.move(fp.replace('.png', '_fusion.png'), fp)
                log.info('Saved in %s'%fp)

    else:
        if not savefig is None:
            shutil.move(fp, savefig)
            log.info('Saved in %s'%savefig)




def plot_segment(filepaths, axes=('A','C','S'), bg=None, opacity=30, cut_coords=None,
        animated=False, savefig=None, figsize=None):
    fp = savefig
    if savefig is None:
        if animated:
            f, fp = tempfile.mkstemp(suffix='.gif')
        else:
            f, fp = tempfile.mkstemp(suffix='.png')
        os.close(f)
    __plot_segment__(filepaths, axes=axes, bg=bg, opacity=opacity, cut_coords=cut_coords,
        animated=animated, savefig=fp, figsize=figsize)


    if savefig is None:
        # Return image
        from IPython.display import Image
        return Image(filename=fp)
