from collections.abc import Iterable
import numpy as np

def _chunks_(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def __maxsize__(data):
    d = []
    if len(data.shape) == 4: # RGB mode (4D volume)
        lambdas = {'A': lambda x: data[:,:,x,:],
                   'C': lambda x: data[:,x,:,:],
                   'S': lambda x: data[x,:,:,:]}
    else: # standard 3D label volume
        lambdas = {'A': lambda x: data[:,:,x],
                   'C': lambda x: data[:,x,:],
                   'S': lambda x: data[x,:,:]}
    maxsize = 0
    slice_index = 0
    for slice_index in range(0,data.shape[2]):
        test = np.flip(np.swapaxes(np.abs(lambdas['A'](int(slice_index))), 0, 1), 0)
        black_pixels_mask = np.all(test == 0, axis=-1)

        size = len(test) - len(black_pixels_mask[black_pixels_mask==True])
        maxsize = max(size, maxsize)
        d.append((slice_index, size))
    return maxsize


def remove_empty_slices(data, slices, threshold=0):
    if len(data.shape) == 4: # RGB mode (4D volume)
        lambdas = {'A': lambda x: data[:,:,x,:],
                   'C': lambda x: data[:,x,:,:],
                   'S': lambda x: data[x,:,:,:]}
    else: # standard 3D label volume
        lambdas = {'A': lambda x: data[:,:,x],
                   'C': lambda x: data[:,x,:],
                   'S': lambda x: data[x,:,:]}

    new_slices = {}
    for axis, slices in slices.items():
        new_slices[axis] = []
        for slice_index in slices:
            test = np.flip(np.swapaxes(np.abs(lambdas[axis](int(slice_index))), 0, 1), 0)
            if len(data.shape) == 4:
                black_pixels_mask = np.all(test == [0, 0, 0], axis=-1)
            else:
                black_pixels_mask = np.all(test == 0, axis=-1)
            if len(test) - len(black_pixels_mask[black_pixels_mask==True]) > threshold:
                new_slices[axis].append(slice_index)
            else:
                import logging as log
                log.info('Removing empty slice %s-%s'%(axis, slice_index))
    return new_slices


def _fix_rowsize_(axes, rowsize=None):

    default_rowsize = {'A': 9, 'C': 9, 'S':6}

    if rowsize is None:
        rs = {e :default_rowsize[e] for e in axes}
    elif isinstance(rowsize, int):
        rs = {e :{'A': rowsize, 'C': rowsize, 'S':rowsize}[e] for e in axes}
    elif isinstance(rowsize, dict):
        from nisnap._parse import __check_axes__
        rs = {__check_axes__(e)[0]:rowsize[e] for e in axes}
    else:
        raise TypeError('rowsize should be an int or a dict')
    return rs


def _fix_figsize_(axes, figsize=None):

    default_figsize = {'A': (10, 5), 'C': (10, 5), 'S': (10, 5)}

    if figsize is None:
        fs = {e :default_figsize[e] for e in axes}
    elif isinstance(figsize, (list, tuple)) and len(figsize) == 2:
        fs = {each: figsize for each in axes}
    elif isinstance(figsize, dict):
        from nisnap._parse import __check_axes__
        fs = {__check_axes__(e)[0]:figsize[e] for e in axes}
    else:
        raise TypeError('figsize should be a tuple/list of size 2 or a dict')

    return fs


def cut_slices(data, axes, rowsize, slices=None, step=3, threshold=75):

    default_slices = {'A': list(range(0, data.shape[2], step)),
        'C': list(range(0, data.shape[1], step)),
        'S': list(range(0, data.shape[0], step))}

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
