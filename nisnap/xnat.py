

def __is_valid_scan__(xnat_instance, scan) :
    ''' Checks if a scan is valid according to a set of rules '''
    valid = False
    import fnmatch
    prefix = [i.split('/')[0] for i in scan.keys() if fnmatch.fnmatch(i,'*scandata/id')][0]
    if not prefix :
            raise Exception
    if scan['%s/id' % prefix].isdigit() \
            and not scan['%s/id' % prefix].startswith('0') \
            and scan['%s/quality' % prefix] == 'usable' \
            and xnat_instance.select.experiment(scan['ID']).scan(scan['%s/id' % prefix]).datatype() in\
                                        ['xnat:mrScanData',
                                         'xnat:petScanData',
                                         'xnat:ctScanData'] :
        valid = True
    return valid

def download_resources(config_fp, experiment_id, resource_name, destination):
    import os.path as op
    import pyxnat
    import tempfile
    x = pyxnat.Interface(config=config_fp)
    t2_lut_names = ['T2_ALFA1']
    t2_scans = []
    e = x.select.experiment(experiment_id)
    scans = x.array.mrscans(experiment_id=experiment_id,\
            columns=['xnat:mrScanData/quality',
                     'xnat:mrScanData/type',
                     'xsiType']).data
    for s in scans:
        scan = e.scan(s['xnat:mrscandata/id'])

        if scan.attrs.get('type') in t2_lut_names and \
            __is_valid_scan__(x, s):
                t2_scans.append(scan.id())
    assert(len(t2_lut_names) == 1)

    filepaths = []
    t2_t1space = list(e.resource('ANTS').files('*%s*T1space.nii.gz'%t2_scans[0]))[0]
    fp1 = op.join(destination, '%s_T2_T1space.nii.gz'%experiment_id)
    filepaths.append(fp1)
    t2_t1space.get(fp1)

    r = e.resource(resource_name)
    for each in ['c1', 'c2', 'c3']:
        c = list(r.files('%s*.nii.gz'%each))[0]
        fp = op.join(destination, '%s_%s.nii.gz'%(experiment_id, each))
        c.get(fp)
        filepaths.append(fp)
    return filepaths


def plot_segment(config_fp, experiment_id, filename=None, resource_name='SPM12_SEGMENT_T2T1_COREG',
    axes=('A', 'C', 'S'), orig=True, opacity=10):

    fp = filename
    if filename is None:
        f, fp = tempfile.mkstemp(suffix='.jpg')
        os.close(f)

    import tempfile
    dest = tempfile.gettempdir()
    # Downloading resources
    filepaths = download_resources(config_fp, experiment_id, resource_name, dest)

    from . import spm
    spm.plot_segment(filepaths, axes, orig, opacity, fp)

    if filename is None:
        # Return image
        from IPython.display import Image
        fp1 = fp
        if bg:
            fp1 = fp.replace('.jpg', '_fusion.jpg')
        if animated:
            fp1 = fp.replace('.jpg', '.gif')

        return Image(filename=fp1)
