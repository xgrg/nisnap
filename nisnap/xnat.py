import tempfile
import os

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

def download_resources(config, experiment_id, resource_name,  destination, raw=True):
    import os.path as op
    import pyxnat
    x = pyxnat.Interface(config=config)
    filepaths = []
    e = x.select.experiment(experiment_id)

    if 'SPM12' in resource_name:

        if raw:
            t2_lut_names = ['T2_ALFA1']
            t2_scans = []
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

            t2_t1space = list(e.resource('ANTS').files('*%s*T1space.nii.gz'%t2_scans[0]))[0]
            fp1 = op.join(destination, '%s_T2_T1space.nii.gz'%experiment_id)
            filepaths.append(fp1)
            t2_t1space.get(fp1)
        else:
            filepaths.append(None)

        r = e.resource(resource_name)
        for each in ['c1', 'c2', 'c3']:
            c = list(r.files('%s*.nii.gz'%each))[0]
            fp = op.join(destination, '%s_%s.nii.gz'%(experiment_id, each))
            c.get(fp)
            filepaths.append(fp)

    elif 'FREESURFER6' in resource_name:
        r = e.resource(resource_name)

        for each in ['orig.mgz', 'aparc+aseg.mgz']:
            c = list(r.files('*%s'%each))[0]
            fp = op.join(destination, '%s_%s'%(experiment_id, each))
            c.get(fp)
            filepaths.append(fp)
    return filepaths


def plot_segment(config, experiment_id, savefig=None, cut_coords=None, resource_name='SPM12_SEGMENT_T2T1_COREG',
    axes=('A', 'C', 'S'), raw=True, opacity=10, animated=False, figsize=None):

    fp = savefig
    if savefig is None:
        if animated:
            f, fp = tempfile.mkstemp(suffix='.gif')
        else:
            f, fp = tempfile.mkstemp(suffix='.png')
        os.close(f)

    dest = tempfile.gettempdir()
    # Downloading resources
    filepaths = download_resources(config, experiment_id, resource_name, dest,
        raw=raw)
    bg = filepaths[0]

    from . import spm
    spm.plot_segment(filepaths[1:], axes=axes, bg=bg, opacity=opacity,
        animated=animated, savefig=fp, figsize=figsize, cut_coords=cut_coords)

    if savefig is None:
        # Return image
        from IPython.display import Image
        return Image(filename=fp)
