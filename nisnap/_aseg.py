import os

def __picklabel_fs__(fp1, fp3, swap=True,
        labels=[9,10,11,12,13,17,48,49,50,51,52,53]):
    '''fp1: aseg.mgz
    fp3: output
    swap: if orig is in FS space, then swap must be True. False if coregistered
        to native T1.
    labels: labels to include in snapshots'''
    import nibabel as nib
    import numpy as np
    from nisnap.snap import pick_labels
    n1 = np.array(nib.load(fp1).dataobj)
    if swap:
        n1 = np.flip(np.swapaxes(n1, 1, 2), -1)
    if not labels is None:
        n1 = pick_labels(n1, labels)

    ref_niimg = nib.load(fp1)
    affine = ref_niimg.affine
    klass = ref_niimg.__class__
    print(fp1, fp3)
    klass(n1, affine, header=None).to_filename(fp3)

def __preproc_aseg__(aseg_fp, rawavg_fp, labels=None):
    fp = aseg_fp.replace('.mgz', '_native.mgz')
    cmd = 'mri_label2vol --seg {aseg} --temp {raw} --o {aseg_T1space} '\
        ' --regheader {aseg}'
    os.system(cmd.format(aseg=aseg_fp,
                        raw=rawavg_fp,
                        aseg_T1space=fp))

    #deepnuclei = [9,10,11,12,13,17,48,49,50,51,52,53]
    if labels is None:
        labels=[9,10,11,12,13,17,48,49,50,51,52,53]
    __picklabel_fs__(fp, fp, swap=False, labels=labels)
    return fp
