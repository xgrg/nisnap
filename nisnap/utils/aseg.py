import os

basal_ganglia_labels = [9, 10, 11, 12, 13, 17, 18, 48, 49, 50, 51, 52, 53, 54]
cortical_labels = [1000, 1001, 1002, 1003, 1005, 1006, 1007, 1008, 1009, 1010,
                   1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020,
                   1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030,
                   1031, 1032, 1033, 1034, 1035, 2000, 2001, 2002, 2003, 2005,
                   2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015,
                   2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025,
                   2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035,
                   4, 5, 7, 8, 14, 15, 16, 24, 26, 28, 30, 31, 43,
                   44, 46, 47, 58, 60, 62, 63, 77, 85, 251, 252, 253, 254, 255]


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
            'returned %s)' % ans
        import logging as log
        log.error(msg)
        return fp

    return fp
