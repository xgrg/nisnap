from collections.abc import Iterable
import numpy as np

def _chunks_(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def __get_lambdas__(data):
    if len(data.shape) == 4: # RGB mode (4D volume)
        lambdas = {'x': lambda x: data[:,:,x,:],
                   'y': lambda x: data[:,x,:,:],
                   'z': lambda x: data[x,:,:,:]}
    else: # standard 3D label volume
        lambdas = {'x': lambda x: data[:,:,x],
                   'y': lambda x: data[:,x,:],
                   'z': lambda x: data[x,:,:]}
    return lambdas

def __get_abs_minmax(data, axis, slices, margin = 5):
    bb = {}
    lambdas = __get_lambdas__(data)

    for a, chunk in enumerate(slices):

        bb[a] = []
        for i, slice_index in enumerate(chunk):
            test = np.flip(np.swapaxes(np.abs(lambdas[axis](int(slice_index))), 0, 1), 0)
            xs, ys = np.where(test!=0)
            bb[a].append((xs, ys))

    min_xs, max_xs = 9999, 0
    min_ys, max_ys = 9999, 0

    for a, bba in bb.items():
        for xs, ys in bba:
            min_xs = min(min_xs, min(xs))
            max_xs = max(max_xs, max(xs))
            min_ys = min(min_ys, min(ys))
            max_ys = max(max_ys, max(ys))

    # Create mock bounding-box
    res = {}
    for a, bba in bb.items():
        res[a] = []
        for each in bba:
            i = [int(min_xs - margin), int(max_xs + margin)],\
                [int(min_ys - margin), int(max_ys + margin)]
            res[a].append(i)
    return res

def __maxsize__(data):
    d = []
    lambdas = __get_lambdas__(data)

    maxsize = 0
    slice_index = 0
    for slice_index in range(0, data.shape[2]):
        test = np.flip(np.swapaxes(np.abs(lambdas['x'](int(slice_index))), 0, 1), 0)
        black_pixels_mask = np.all(test == 0, axis=-1)

        size = len(test) - len(black_pixels_mask[black_pixels_mask==True])
        maxsize = max(size, maxsize)
        d.append((slice_index, size))
    return maxsize


def remove_empty_slices(data, slices, threshold=0):
    lambdas = __get_lambdas__(data)

    new_slices = {}
    for axis, slices in slices.items():
        new_slices[axis] = []
        for slice_index in slices:
            test = np.flip(np.swapaxes(np.abs(lambdas[axis](int(slice_index))), 0, 1), 0)
            if len(data.shape) == 4:
                black_pixels_mask = np.all(test == [0, 0, 0], axis=-1)
            else:
                black_pixels_mask = np.all(test == 0, axis=-1)
            size = len(test) - len(black_pixels_mask[black_pixels_mask==True])
            if size > threshold:
                new_slices[axis].append(slice_index)
            else:
                import logging as log
                log.info('Removing empty slice %s-%s'%(axis, slice_index))
    return new_slices


def _fix_rowsize_(axes, rowsize=None):

    default_rowsize = {'x': 9, 'y': 9, 'z':6}

    if rowsize is None:
        rs = {e :default_rowsize[e] for e in axes}
    elif isinstance(rowsize, int):
        rs = {e :{'x': rowsize, 'y': rowsize, 'z':rowsize}[e] for e in axes}
    elif isinstance(rowsize, dict):
        from nisnap.utils.parse import __check_axes__
        rs = {__check_axes__(e)[0]:rowsize[e] for e in axes}
    else:
        raise TypeError('rowsize should be an int or a dict')
    return rs


def _fix_figsize_(axes, figsize=None):

    default_figsize = {'x': (10, 5), 'y': (10, 5), 'z': (10, 5)}

    if figsize is None:
        fs = {e :default_figsize[e] for e in axes}
    elif isinstance(figsize, (list, tuple)) and len(figsize) == 2:
        fs = {each: figsize for each in axes}
    elif isinstance(figsize, dict):
        from nisnap.utils.parse import __check_axes__
        fs = {__check_axes__(e)[0]:figsize[e] for e in axes}
    else:
        raise TypeError('figsize should be a tuple/list of size 2 or a dict')

    return fs


def cut_slices(data, axes, rowsize, slices=None, step=3, threshold=75):

    default_slices = {'x': list(range(0, data.shape[2], step)),
        'y': list(range(0, data.shape[1], step)),
        'z': list(range(0, data.shape[0], step))}

    if not slices is None:
        if isinstance(slices, dict):
            sl = {e: list(slices[e]) for e in axes}
        elif isinstance(slices, Iterable):
            sl = {e: slices for e in axes}
    else:
        sl = {e: default_slices[e] for e in axes}
        sl = remove_empty_slices(data, sl, threshold=threshold)

    sl = remove_empty_slices(data, sl)

    sl = {each: list(_chunks_(sl[each], rowsize[each])) for each in axes}

    return sl
