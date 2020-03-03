import sys
import spm_snapshot as ss

def snap_xnat(config_fp, experiment_id, fp, axes=('A', 'C', 'S'),
    orig=True, opacity=10):

    resource_name = 'SPM12_SEGMENT_T2T1_COREG2'
    ss.snap_xnat(config_fp, experiment_id, resource_name, axes, orig, opacity, fp)


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
    parser.add_argument('-o', '--output', required=False, type=argparse.FileType('w'))

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


if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args()
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    check_logic(args)
    print(args)

    axes = tuple([e for e in args.axes])

    if args.config:
        snap_xnat(args.config.name, args.experiment, args.output.name, axes,
            not args.nobg, args.opacity)
    else:
        snap_files([e.name for e in args.files], args.output.name,
            getattr(args.bg, 'name', None), axes, args.opacity)
