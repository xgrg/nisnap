import os

basal_ganglia_labels = [9,10,11,12,13,17,48,49,50,51,52,53]

def __process_img__(ifp, ofp, func, **kwargs):
    import nibabel as nib
    import numpy as np
    n1 = np.array(nib.load(ifp).dataobj)

    n1 = func(n1, **kwargs)

    ref_niimg = nib.load(ifp)
    affine = ref_niimg.affine
    klass = ref_niimg.__class__
    klass(n1, affine, header=None).to_filename(ofp)


def __picklabel_fs__(fp, labels=basal_ganglia_labels):
    ofp = fp.replace('.mgz', '_filtered.mgz')
    from nisnap.snap import pick_labels
    __process_img__(fp, ofp, pick_labels, labels=labels)
    return ofp


def __swap_fs__(fp, cache=False):
    import numpy as np
    ofp = fp.replace('.mgz', '_swapped.mgz')
    if cache:
        return ofp
    __process_img__(fp, ofp, lambda n1: np.flip(np.swapaxes(n1, 1, 2), -1))
    return ofp


def __preproc_aseg__(aseg_fp, rawavg_fp, cache=False):
    fp = aseg_fp.replace('.mgz', '_native.mgz')
    if cache:
        return fp

    cmd = 'mri_label2vol --seg {aseg} --temp {raw} --o {aseg_T1space} '\
        ' --regheader {aseg}'
    ans = os.system(cmd.format(aseg=aseg_fp,
                               raw=rawavg_fp,
                               aseg_T1space=fp))
    if ans != 0:
        msg = 'FreeSurfer command `mri_label2vol` failed. Please check that '\
            'FreeSurfer is correctly installed and configured. (Command '\
            'returned %s)'%ans
        import logging as log
        log.error(msg)
        return fp

    return fp
