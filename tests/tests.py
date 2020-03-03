import unittest
from nisnap import spm_snapshot as ss
from nisnap import plot


class RunThemAll(unittest.TestCase):

    def test_001_check_logic(self):
        parser = plot.create_parser()
        args = ['/home/grg/.xnat.cfg', '/home/grg/.xnat.cfg',
            '/home/grg/.xnat.cfg', '-o', '/tmp/toto.jpg']
        args = parser.parse_args(args)
        plot.check_logic(args)

        try:
            args = '/home/grg/.xnat.cfg /home/grg/.xnat.cfg /home/grg/.xnat.cfg '\
                '/home/grg/.xnat.cfg -o /tmp/toto.jpg'
            args = parser.parse_args(args.split(' '))
            plot.check_logic(args)
        except Exception as e:
            print(e)
            pass

        try:
            args = '/home/grg/.xnat.cfg /home/grg/.xnat.cfg /home/grg/.xnat.cfg '\
                '/home/grg/.xnat.cfg /tmp/toto.jpg'
            args = parser.parse_args(args.split(' '))
            plot.check_logic(args)
        except Exception as e:
            print(e)
            pass

        args = '/home/grg/.xnat.cfg -o /tmp/toto.jpg'
        args = parser.parse_args(args.split(' '))
        plot.check_logic(args)

        args = '/home/grg/.xnat.cfg --bg /home/grg/.xnat.cfg -o /tmp/toto.jpg'
        args = parser.parse_args(args.split(' '))
        plot.check_logic(args)

        args = '--config /home/grg/.xnat.cfg -e BBRC_E000 -o /tmp/toto.jpg'
        args = parser.parse_args(args.split(' '))
        plot.check_logic(args)

        args = '--config /home/grg/.xnat.cfg -e BBRC_E000 --nobg -o /tmp/toto.jpg'
        args = parser.parse_args(args.split(' '))
        plot.check_logic(args)

        try:
            args = '--config /home/grg/.xnat.cfg -e BBRC_E000 --nobg -o /tmp/toto.gif'
            args = parser.parse_args(args.split(' '))
            plot.check_logic(args)
        except Exception as e:
            print(e)
            pass

        args = '--config /home/grg/.xnat.cfg -e BBRC_E000 -o /tmp/toto.gif'
        args = parser.parse_args(args.split(' '))
        plot.check_logic(args)

    def test_002_snap_files(self):
        parser = plot.create_parser()
        args = '--bg /tmp/BBRCDEV_E02849_T2_T1space.nii.gz '\
           '/tmp/BBRCDEV_E02849_c1.nii.gz /tmp/BBRCDEV_E02849_c2.nii.gz '\
           '/tmp/BBRCDEV_E02849_c3.nii.gz -o /tmp/test.gif --axes ACS --opacity 30'
        args = parser.parse_args(args.split(' '))
        axes = tuple([e for e in args.axes])

        filepaths = [args.bg.name]
        filepaths.extend([e.name for e in args.files])
        bg = getattr(args.bg, 'name', None)
        ss.snap_files(filepaths, axes, not bg is None, args.opacity, args.output.name)

    def test_003_snap_xnat(self):
        parser = plot.create_parser()
        args = '--config /home/grg/.xnat_goperto_ci.cfg '\
           '-e BBRCDEV_E02849 -o /tmp/test.gif --axes ACS --opacity 30'
        args = parser.parse_args(args.split(' '))
        axes = tuple([e for e in args.axes])

        filepaths = [args.bg.name]
        filepaths.extend([e.name for e in args.files])
        bg = getattr(args.bg, 'name', None)
        ss.snap_files(filepaths, axes, not bg is None, args.opacity, args.output.name)
