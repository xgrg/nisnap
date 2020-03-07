def create_parser():
    import argparse

    parser = argparse.ArgumentParser(description='Snap')
    parser.add_argument('--config', required=False, type=argparse.FileType('r'))
    parser.add_argument('--nobg', required=False, action='store_true')

    parser.add_argument('--bg', required=False, type=argparse.FileType('r'))
    parser.add_argument('--axes', required=False, default='ACS')
    parser.add_argument('--opacity', required=False, type=int)
    parser.add_argument('-e', '--experiment', required=False, type=str)
    parser.add_argument('--resource', required=False, type=str,
        default='SPM12_SEGMENT_T2T1_COREG2')

    parser.add_argument('-o', '--output', required=False) #, type=argparse.FileType('w'))
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

    if args.output.endswith('.gif') and ((args.config and args.nobg) or (not args.config and not args.bg)):
        msg = 'GIF animation can be created only providing a background image.'
        raise Exception(msg)

    if args.disable_warnings:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    import logging as log
    logger = log.getLogger()
    if args.verbose:
        logger.setLevel(level=log.DEBUG)
    else:
        logger.setLevel(level=log.INFO)


def run(args):
    check_logic(args)

    axes = tuple([e for e in args.axes])
    if args.config:
        from . import xnat
        xnat.plot_segment(args.config.name, args.experiment, savefig=args.output,
            resource_name=args.resource, axes=axes, raw=not args.nobg,
            opacity=args.opacity, animated=args.output.endswith('.gif'))
    else:
        from . import spm
        spm.plot_segment([e.name for e in args.files], axes=axes,
            bg=args.bg.name, opacity=args.opacity,
            animated=args.output.endswith('.gif'), savefig=args.output)
