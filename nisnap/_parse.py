
def create_parser():
    import argparse
    from argparse import RawTextHelpFormatter

    desc = 'Create snapshots from segmentation maps. \n\nData can be downloaded '\
        'from an XNAT instance or passed as arguments.\n'

    desc = desc + '\nnisnap is distributed in the hope that it will be useful, '\
     'but WITHOUT ANY WARRANTY. \nSubmit issues/comments/PR at '\
     'http://gitlab.com/xgrg/nisnap.\n\n'\
     'Author: Greg Operto - BarcelonaBeta Brain Research Center (2020)'
    parser = argparse.ArgumentParser(description=desc,
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('--bg', required=False, type=argparse.FileType('r'),
        help = 'background image on which segmentations will be plotted.')
    parser.add_argument('--axes', required=False, default='ACS',
        help = "choose the direction of the cuts (among 'A', 'S', 'C', 'AXIAL',"\
            "'SAGITTAL' or 'CORONAL', or lowercase)")
    parser.add_argument('--contours', required=False, action='store_true',
        default=False,
        help='If True, segmentations will be rendered as contoured regions. If False,'\
        ' will be rendered as superimposed masks')
    parser.add_argument('--opacity', required=False, type=int,
        help = 'opacity (in %%) of the segmentation maps when plotted over a background '\
        'image. Only used if a background image is provided.')
    parser.add_argument('-o', '--output', required=False,
        help='snapshot will be stored in this file. If extension is .gif, snapshot'\
            ' will be rendered as an animation.') #, type=argparse.FileType('w'))
    parser.add_argument('--config', required=False, type=argparse.FileType('r'),
        help = '[XNAT mode] XNAT configuration file')
    parser.add_argument('--nobg', required=False, action='store_true',
        help = '[XNAT mode] no background image. Plots segmentation maps only.')
    parser.add_argument('-e', '--experiment', required=False, type=str,
        help = '[XNAT mode] ID of the experiment to create snapshots from.')
    parser.add_argument('--resource', required=False, type=str,
        default='SPM12_SEGMENT_T2T1_COREG2',
        help = '[XNAT mode] name of the resource to download')
    parser.add_argument('--cache', required=False, action='store_true',
        default=False, help='[XNAT mode] skip downloads (e.g. if running for a second time')


    parser.add_argument('--disable_warnings', required=False, action='store_true',
        default=False)
    parser.add_argument('--verbose', required=False, action='store_true',
        default=False)
    parser.add_argument('files', nargs='*', type=argparse.FileType('r'),
        help='segmentation map(s) to create snapshots from (not XNAT mode)')

    return parser


def __check_axes__(axes):
    import logging as log
    from collections.abc import Iterable
    is_correct = True
    curated_axes = []
    ax_names = ('A', 'S', 'C', 'AXIAL', 'SAGITTAL', 'CORONAL')
    if ((isinstance(axes, str) or isinstance(axes, Iterable)) \
            and len(axes) > 0 and len(axes) < 4):
        for e in axes:
            if not e.upper() in ax_names:
                is_correct = False
            else:
                curated_axes.append(e.upper())
    else:
        is_correct = False

    msg = 'axes should be a single character or an Iterable with the'\
        ' following: %s'%', '.join(ax_names)
    if not is_correct:
        log.warning('Axes: %s (%s)'%(axes, type(axes)))
        raise ValueError(msg)
    return tuple(curated_axes)

def check_logic(args):
    '''Some arguments/options are not compatible, or required jointly. This
    function checks them and may raise Exceptions if logic rules are failed.'''

    if (args.bg or len(args.files) > 0) and (args.config or args.experiment):
        msg = 'Offline mode and XNAT options cannot be used simultaneously'
        raise Exception(msg)

    if (args.bg or len(args.files) > 0) and args.cache:
        msg = '--cache can be used in XNAT mode only.'
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

    if args.output.endswith('.gif') and ((args.config and args.nobg) or \
            (not args.config and not args.bg)):
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
            opacity=args.opacity, animated=args.output.endswith('.gif'),
            cache=args.cache, contours=args.contours)
    else:
        from . import snap

        fp = args.files[0].name if len(args.files) == 1 \
            else [e.name for e in args.files]

        snap.plot_segment(fp, axes=axes,
            bg=args.bg.name, opacity=args.opacity, contours=args.contours,
            animated=args.output.endswith('.gif'), savefig=args.output)
