import os as __os__

__ev__ = 'FREESURFER_REG_TO_NATIVE'
__freesurfer_reg_to_native__ = __os__.environ.get(__ev__, None) is not None
__all__ = []


def __is_valid_scan__(xnat_instance, scan):
    """ Checks if a scan is valid according to a set of rules """
    import fnmatch
    valid = False
    prefix = [i.split('/')[0] for i in scan.keys()
              if fnmatch.fnmatch(i, '*scandata/id')][0]
    if not prefix:
        raise Exception
    exp = xnat_instance.select.experiment(scan['ID'])
    dt = exp.scan(scan[f'{prefix}/id']).datatype()
    datatypes = ['xnat:mrScanData', 'xnat:petScanData', 'xnat:ctScanData']
    if scan[f'{prefix}/id'].isdigit() \
            and not scan[f'{prefix}/id'].startswith('0') \
            and scan[f'{prefix}/quality'] == 'usable' \
            and dt in datatypes:
        valid = True
    return valid


def __get_T1__(x, experiment_id, sequence='T1_ALFA1'):
    t1_lut_names = [sequence]
    t1_scans = []
    scans = x.array.mrscans(experiment_id=experiment_id,
                            columns=['xnat:mrScanData/quality',
                                     'xnat:mrScanData/type',
                                     'xsiType']).data
    e = x.select.experiment(experiment_id)
    for s in scans:
        scan = e.scan(s['xnat:mrscandata/id'])
        if scan.attrs.get('type').rstrip(' ') in t1_lut_names and\
                __is_valid_scan__(x, s):
            t1_scans.append(scan.id())
    assert len(t1_scans) == 1
    files = list(e.scan(t1_scans[0]).resource('NIFTI').files('*.nii.gz'))
    return files[0]


def __get_T2__(x, experiment_id, sequence='T2_ALFA1'):
    t2_lut_names = [sequence]
    t2_scans = []
    scans = x.array.mrscans(experiment_id=experiment_id,
                            columns=['xnat:mrScanData/quality',
                                     'xnat:mrScanData/type',
                                     'xsiType']).data
    e = x.select.experiment(experiment_id)
    for s in scans:
        scan = e.scan(s['xnat:mrscandata/id'])

        if scan.attrs.get('type').rstrip(' ') in t2_lut_names and\
                __is_valid_scan__(x, s):
            t2_scans.append(scan.id())
    assert len(t2_scans) == 1
    t2_t1space = list(e.resource('ANTS').files(f'*{t2_scans[0]}*T1space.nii.gz'))[0]
    return t2_t1space


def __download_freesurfer__(x, experiment_id, destination,
                            resource_name='FREESURFER7',
                            raw=True, cache=False, fn='aparc+aseg.mgz'):
    import os.path as op
    filepaths = []
    e = x.select.experiment(experiment_id)
    r = e.resource(resource_name)
    if not r.exists():
        raise Exception(f'Experiment {experiment_id} has no resource {resource_name}.')

    if raw:
        fp1 = op.join(destination, f'{experiment_id}_T1.nii.gz')
        filepaths.append(fp1)
        if not cache:
            t1_file = __get_T1__(x, experiment_id)
            t1_file.get(fp1)
    else:
        filepaths.append(None)

    files = ['rawavg.mgz', fn] if __freesurfer_reg_to_native__\
        else ['nu.mgz', fn]
    for each in files:
        c = list(r.files(f'*{each}'))
        if each in ['nu.mgz', 'rawavg.mgz']:  # should come from FREESURFER7
            r1 = e.resource(resource_name.split('_EXTRAS')[0])
            c = list(r1.files(f'*{each}'))

        fp = op.join(destination, f'{experiment_id}_{each}')
        if not cache:
            c[0].get(fp)
        filepaths.append(fp)

    if fn == 'hypothalamic_subunits_seg.v1.mgz':
        # Register hypothalamus
        import nibabel as nib
        from nilearn.image import resample_img
        target_affine = nib.load(filepaths[1]).affine  # thalamus
        img = nib.load(filepaths[2])  # hypothalamus
        resampled_nii = resample_img(img, target_affine, interpolation='nearest')
        fp = filepaths[2].replace('.mgz', 'FSvoxelSpace.mgz')
        resampled_nii.to_filename(fp)
        filepaths.pop(-1)
        filepaths.append(fp)

    from nisnap.utils import aseg
    aseg_fp = filepaths[2]
    bg = filepaths[1]

    # Note that the filepaths for these new steps are not stored/returned
    if __freesurfer_reg_to_native__:
        aseg.__preproc_aseg__(aseg_fp, bg, cache=cache)
    aseg.__swap_fs__(aseg_fp, cache=cache)
    aseg.__swap_fs__(bg, cache=cache)

    import logging as log
    log.basicConfig(level=log.INFO)
    log.info('__freesurfer_reg_to_native__: %s' % __freesurfer_reg_to_native__)

    bg = filepaths[0]

    aseg_fp = filepaths[2]

    # Files were created just before
    # So we only need to fetch their names (with cache=True)
    if __freesurfer_reg_to_native__:
        aseg_fp = aseg.__preproc_aseg__(aseg_fp, bg, cache=True)
    else:
        aseg_fp = aseg.__swap_fs__(aseg_fp, cache=True)
        bg = aseg.__swap_fs__(filepaths[1], cache=True)

    if raw:
        res = [bg, aseg_fp]
    else:
        res = [None, aseg_fp]
    return res


def __download_spm12__(x, experiment_id, destination,
                       resource_name='SPM12_SEGMENT',
                       raw=True, cache=False):
    import os.path as op

    filepaths = []
    e = x.select.experiment(experiment_id)
    r = e.resource(resource_name)

    if raw:
        fp1 = op.join(destination, f'{experiment_id}_T1.nii.gz')
        filepaths.append(fp1)
        if not cache:
            t1_file = __get_T1__(x, experiment_id)
            t1_file.get(fp1)

    else:
        filepaths.append(None)

    files = ['c1', 'c2', 'c3']
    if resource_name == 'SPM12_SEGMENT_T1T2':
        files = ['fixed_c1', 'fixed_c2', 'fixed_c3']
    for each in files:
        c = list(r.files(f'{each}*.nii.gz'))[0]
        fp = op.join(destination, f'{experiment_id}_{resource_name}_{each}.nii.gz')
        if not cache:
            c.get(fp)
        filepaths.append(fp)

    return filepaths


def __download_ashs__(x, experiment_id, destination, resource_name='ASHS',
                      raw=True, cache=False):
    import os.path as op

    filepaths = []
    e = x.select.experiment(experiment_id)
    r = e.resource(resource_name)

    for each in ['tse.nii.gz', 'left_lfseg_corr_nogray.nii.gz']:
        c = list(r.files(f'*{each}'))[0]
        fp = op.join(destination, f'{experiment_id}_{resource_name}_{each}.nii.gz')
        if not cache:
            c.get(fp)
        filepaths.append(fp)
    return filepaths


def __download_lcmodel__(x, experiment_id, destination, resource_name='LCMODEL',
                         raw=True, cache=False, fn='rAmask_Hipo*'):
    import os.path as op

    filepaths = []
    e = x.select.experiment(experiment_id)
    r = e.resource(resource_name)

    for each in ['T1*.nii.gz', fn]:
        c = list(r.files(f'*{each}'))[0]
        fp = op.join(destination, f'{experiment_id}_{resource_name}_{each}.nii.gz')
        if not cache:
            c.get(fp)
        filepaths.append(fp)
    return filepaths


def download_resources(config, experiment_id, resource_name,
                       destination, raw=True, cache=False):
    """Download a given experiment/resource from an XNAT instance in a local
    destination folder.

    Parameters
    ----------
    config: string
        Configuration file to the XNAT instance.
        See http://xgrg.github.io/first-steps-with-pyxnat/ for more details.

    experiment_id : string
        ID of the experiment from which to download the segmentation maps and
        raw anatomical image.

    resource_name: string
        Name of the resource where the segmentation maps are stored in the XNAT
        instance.

    destination: string
        Destination folder where to store the downloaded resources.

    raw: boolean, optional
        If True, a raw anatomical image will be downloaded along with the
        target resources. If False, only the resources referred to by
        `resource_name` will be downloaded. Default: True

    cache: boolean, optional
        If False, resources will be normally downloaded from XNAT. If True,
        download will be skipped and data will be looked up locally.
        Default: False

    Notes
    -----
    Requires an XNAT instance where SPM segmentation maps will be found
    following a certain data organization in experiment resources named
    `resource_name`.

    See Also
    --------
    xnat.plot_segment : To plot segmentation maps directly providing their
        experiment_id on an XNAT instance
    nisnap.plot_segment : To plot segmentation maps directly providing their
        filepaths

    """
    import pyxnat
    import os.path as op

    x = pyxnat.Interface(config=config)
    filepaths = []
    e = x.select.experiment(experiment_id)

    if 'SPM12' in resource_name:
        filepaths = __download_spm12__(x, experiment_id, destination,
                                       resource_name, raw, cache)

    elif resource_name == 'ASHS':
        filepaths = __download_ashs__(x, experiment_id, destination,
                                      resource_name, raw, cache)

    elif resource_name == 'LCMODEL':
        filepaths = __download_lcmodel__(x, experiment_id, destination,
                                         resource_name, raw, cache)

    elif 'FREESURFER' in resource_name and resource_name.endswith('_EXTRAS'):
        files = ['hypothalamic_subunits_seg.v1.mgz',
                 'ThalamicNuclei.v12.T1.FSvoxelSpace.mgz',
                 'brainstemSsLabels.v12.FSvoxelSpace.mgz']
        filepaths = []
        for fn in files:
            fp = __download_freesurfer__(x, experiment_id,
                                         destination, resource_name,
                                         raw, cache, fn=fn)
            if len(filepaths) != 0:
                fp = [fp[-1]]
            filepaths.extend(fp)

    elif 'FREESURFER' in resource_name:
        filepaths = __download_freesurfer__(x, experiment_id, destination,
                                            resource_name, raw, cache)
        if resource_name == 'FREESURFER7':
            fn = '%s.hippoAmygLabels-T1.v21.%s.FSvoxelSpace.mgz'
            for side in ['lh', 'rh']:
                for each in ['CA', 'HBT', 'FS60']:
                    fp = __download_freesurfer__(x, experiment_id, destination,
                                                 resource_name, raw, cache,
                                                 fn=fn % (side, each))
                    filepaths.append(fp[-1])

    elif 'CAT12' in resource_name:
        if raw:
            fp1 = op.join(destination, f'{experiment_id}_T1.nii.gz')
            filepaths.append(fp1)
            if not cache:
                t2_t1space = __get_T1__(x, experiment_id)
                t2_t1space.get(fp1)
        else:
            filepaths.append(None)

        r = e.resource(resource_name)
        for each in ['p1', 'p2', 'p3']:
            c = list(r.files(f'mri/{each}*.nii.gz'))[0]
            fp = op.join(destination, f'{experiment_id}_{resource_name}_{each}.nii.gz')
            if not cache:
                c.get(fp)
            filepaths.append(fp)

    # If files missing with cache set to True, raise Exception
    if cache:
        for f in filepaths:
            if f is None and not raw:
                continue
            if not op.isfile(f):
                msg = f'No such file: \'{f}\'. Retry with cache set to False.'
                raise FileNotFoundError(msg)

    return filepaths


def plot_segment(config, experiment_id, savefig=None, slices=None,
                 resource_name='SPM12_SEGMENT', fn='aparc+aseg.mgz',
                 axes='xyz', raw=True, opacity=70, animated=False,
                 rowsize=None, figsize=None, contours=False, cache=False,
                 samebox=False):
    """Download a given experiment/resource from an XNAT instance and create
    snapshots of this resource along a selected set of slices.

    Parameters
    ----------
    config: string
        Configuration file to the XNAT instance.

    experiment_id : string
        ID of the experiment from which to download the segmentation maps and
        raw anatomical image.

    savefig: string, optional
        Filepath where the resulting snapshot will be created. If None is
        given, a temporary file will be created and/or the result will be
        displayed inline in a Jupyter Notebook.

    slices: None, or a tuple of floats
        The indexes of the slices that will be rendered. If None is given, the
        slices are selected automatically.

    resource_name: string, optional
        Name of the resource where the segmentation maps are stored in the XNAT
        instance. Default: SPM12_SEGMENT

    fn: string, optional
        Only for FREESURFER7_EXTRAS. Defines which segmentation should be
        rendered (among 'brainstem', 'thalamus', 'hypothalamus') Default: None

    axes: string, or a tuple of strings
        Choose the direction of the cuts (among 'x', 'y', or 'z')

    raw: boolean, optional
        If True, the segmentation maps will be plotted over a background image
        (e.g. anatomical T1 or T2, as in xnat.download_resources). If False,
        the segmentation maps will be rendered only. Default: True

    opacity: integer, optional
        The opacity (in %) of the segmentation maps when plotted over a
        background image. Only used if a background image is provided.
        Default: 10

    animated: boolean, optional
        If True, the snapshot will be rendered as an animated GIF.
        If False, the snapshot will be rendered as a static PNG image. Default:
        False

    rowsize: None, or int, or dict
        Set the number of slices per row in the final compiled figure.
        Default: {'x': 9, 'y': 9, 'z': 6}

    figsize: None, or float
        Figure size (matplotlib definition) along each axis. Default: auto.

    contours: boolean, optional
        If True, segmentations will be rendered as contoured regions. If False,
        will be rendered as superimposed masks. Default: False

    cache: boolean, optional
        If False, resources will be normally downloaded from XNAT. If True,
        download will be skipped and data will be looked up locally.
        Default: False

    samebox: boolean, optional
        If True, bounding box will be fixed. If False, adjusted for each slice.

    Notes
    -----
    Requires an XNAT instance where SPM segmentation maps will be found
    following a certain data organization in experiment resources named
    `resource_name`.

    See Also
    --------
    xnat.download_resources : To download resources (e.g. segmentation maps +
        raw images) from an XNAT instance (e.g. prior to snapshot creation)
    nisnap.plot_segment : To plot segmentation maps directly providing their
        filepaths

    """
    import tempfile

    if animated and not raw:
        msg = 'animated cannot be True with raw set to False. ' \
              'Switching raw to True.'
        import logging as log
        log.warning(msg)
        raw = True

    options = ['aparc+aseg.mgz']
    fn0 = '%s.hippoAmygLabels-T1.v21.%s.FSvoxelSpace.mgz'
    for side in ['lh', 'rh']:
        for each in ['CA', 'HBT', 'FS60']:
            options.append(fn0 % (side, each))
    if resource_name == 'FREESURFER7_EXTRAS':
        options = ['hypothalamic_subunits_seg.v1.mgz',
                   'ThalamicNuclei.v12.T1.FSvoxelSpace.mgz',
                   'brainstemSsLabels.v12.FSvoxelSpace.mgz']
        if fn not in options:
            raise Exception(f'`fn` should be among {options}')
    elif resource_name.startswith('FREESURFER'):
        if fn not in options:
            raise Exception(f'`fn` should be among {options}')

    fp = savefig
    if savefig is None:
        if animated:
            f, fp = tempfile.mkstemp(suffix='.gif')
        else:
            from nisnap.snap import __format__
            f, fp = tempfile.mkstemp(suffix=__format__)
        __os__.close(f)

    dest = tempfile.gettempdir()
    # Downloading resources
    try:
        filepaths = download_resources(config, experiment_id, resource_name,
                                       dest, raw=raw, cache=cache)
    except FileNotFoundError as exc:
        msg = f'{exc}. Retry with cache set to False.'
        raise FileNotFoundError(msg) from exc
    bg = filepaths[0]

    if resource_name == 'FREESURFER7_EXTRAS':
        filepaths = [bg, filepaths[options.index(fn) + 1]]
    elif resource_name.startswith('FREESURFER'):
        if fn[3:].startswith('hippoAmygLabels'):
            filepaths = [bg, filepaths[options.index(fn) + 1]]
        else:
            filepaths = filepaths[:2]

    filepaths = filepaths[1] if len(filepaths) == 2 else filepaths[1:]
    from . import snap
    snap.plot_segment(filepaths, axes=axes, bg=bg, opacity=opacity,
                      animated=animated, savefig=fp, figsize=figsize,
                      contours=contours, rowsize=rowsize, slices=slices,
                      samebox=samebox)

    if savefig is None:
        # Return image
        from IPython.display import Image
        return Image(filename=fp)
