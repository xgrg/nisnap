import sys

import matplotlib
matplotlib.use('Agg')
from nisnap import spm_snapshot as ss
import tempfile
import logging as log


def snap_xnat(config_fp, experiment_id, fp, resource_name='SPM12_SEGMENT_T2T1_COREG',
    axes=('A', 'C', 'S'), orig=True, opacity=10):

    wd = tempfile.gettempdir()
    # Downloading resources
    filepaths = ss.download_resources(config_fp, experiment_id, resource_name, wd)

    ss.snap_files(filepaths, axes, orig, opacity, fp)



def snap_files(filepaths, fp, bg=None, axes=('A', 'C', 'S'), opacity=10):
    filepaths.insert(0, bg)
    ss.snap_files(filepaths, axes, not bg is None, opacity, fp)


def create_parser():
    import argparse

    parser = argparse.ArgumentParser(description='Snap')
    parser.add_argument('--config', required=False, type=argparse.FileType('r'))
    parser.add_argument('--nobg', required=False, action='store_true')

    parser.add_argument('--bg', required=False, type=argparse.FileType('r'))
    parser.add_argument('--axes', required=False, default='ACS')
    parser.add_argument('--opacity', required=False, type=int)
    parser.add_argument('-e', '--experiment', required=False, type=str)
    parser.add_argument('--rn', required=False, type=str,
        default='SPM12_SEGMENT_T2T1_COREG2')

    parser.add_argument('-o', '--output', required=False, type=argparse.FileType('w'))
    parser.add_argument('--disable_warnings', required=False, action='store_true',
        default=False)
    parser.add_argument('--verbose', required=False, action='store_true',
        default=False)
    parser.add_argument('files', nargs='*', type=argparse.FileType('r'))

    return parser

def check_logic(args):
    if (args.bg or len(args.files) > 0) and (args.config or args.experiment):
        msg = 'Offline mode and XNAT options cannot be used simultaneously'
        raise Exception(msg)

    if args.config:
        if not args.experiment:
            msg = 'Missing option --experiment'
            raise Exception(msg)

    if args.experiment:
        if not args.config:
            msg = 'Missing option --config'
            raise Exception(msg)

    if args.nobg and args.opacity:
        msg = 'Warning. --nobg and --opacity used simultaneously.'
        raise Exception(msg)

    if args.opacity and not args.config:
        if not args.bg:
            msg = 'Missing option --bg'
            raise Exception(msg)

    if not args.config:
        if len(args.files) == 0 or len(args.files) > 3:
            msg = 'List of files must be of length 1, 2 or 3.'
            raise Exception(msg)

    if not args.opacity:
        args.opacity = 10

    if args.output.name.endswith('.gif') and ((args.config and args.nobg) or (not args.config and not args.bg)):
        msg = 'GIF animation can be created only providing a background image.'
        raise Exception(msg)

    if args.disable_warnings:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    logger = log.getLogger()
    if args.verbose:
        logger.setLevel(level=log.DEBUG)
    else:
        logger.setLevel(level=log.INFO)


def from_files(filepaths, axes=('A', 'C', 'S'), orig=True, opacity=30):
    import os, tempfile
    f, fp = tempfile.mkstemp(suffix='.jpg')
    os.close(f)
    ss.snap_files(filepaths, axes, orig=True, opacity=30, orig_fp=fp)
    from IPython.display import Image
    return Image(filename=fp.replace('.jpg', '_fusion.jpg'))



def from_xnat(config, experiment_id, resource_name='SPM12_SEGMENT_T2T1_COREG',
            axes=('A','C','S'), bg=True, opacity=30, animated=False):
    import os, tempfile
    ext = '.gif' if animated else '.jpg'
    f, fp = tempfile.mkstemp(suffix=ext)
    os.close(f)
    wd = tempfile.gettempdir()

    # Downloading resources
    filepaths = ss.download_resources(config, experiment_id, resource_name, wd)
    ss.snap_files(filepaths, axes=axes, orig=bg, opacity=opacity, orig_fp=fp)

    from IPython.display import Image
    fp1 = fp
    if bg:
        fp1 = fp.replace('.jpg', '_fusion.jpg')
    if animated:
        fp1 = fp.replace('.jpg', '.gif')

    return Image(filename=fp1)


if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args()
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    check_logic(args)

    axes = tuple([e for e in args.axes])

    if args.config:
        snap_xnat(args.config.name, args.experiment, args.output.name,
            args.rn, axes, not args.nobg, args.opacity)
    else:
        snap_files([e.name for e in args.files], args.output.name,
            getattr(args.bg, 'name', None), axes, args.opacity)
