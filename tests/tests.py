import unittest
from nisnap import parse, xnat
import nisnap


class RunThemAll(unittest.TestCase):

    def test_001_check_logic(self):
        parser = parse.create_parser()
        import os
        os.system('touch /tmp/.xnat.cfg')
        os.system('touch /tmp/toto.jpg')
        args = ['/tmp/.xnat.cfg', '/tmp/.xnat.cfg',
            '/tmp/.xnat.cfg', '-o', '/tmp/toto.jpg']
        args = parser.parse_args(args)
        parse.check_logic(args)


        try:
            args = '/tmp/.xnat.cfg /tmp/.xnat.cfg /tmp/.xnat.cfg '\
                '/tmp/.xnat.cfg -o /tmp/toto.jpg'
            args = parser.parse_args(args.split(' '))
            parse.check_logic(args)
        except Exception as e:
            print(e)
            pass

        try:
            args = '/tmp/.xnat.cfg /tmp/.xnat.cfg /tmp/.xnat.cfg '\
                '/tmp/.xnat.cfg /tmp/.xnat.cfg'
            args = parser.parse_args(args.split(' '))
            parse.check_logic(args)
        except Exception as e:
            print(e)
            pass

        args = '/tmp/.xnat.cfg -o /tmp/toto.jpg'
        args = parser.parse_args(args.split(' '))
        parse.check_logic(args)

        args = '/tmp/.xnat.cfg --bg /tmp/.xnat.cfg -o /tmp/toto.jpg'
        args = parser.parse_args(args.split(' '))
        parse.check_logic(args)

        args = '--config /tmp/.xnat.cfg -e BBRC_E000 -o /tmp/toto.jpg'
        args = parser.parse_args(args.split(' '))
        parse.check_logic(args)

        args = '--config /tmp/.xnat.cfg -e BBRC_E000 --nobg -o /tmp/toto.jpg'
        args = parser.parse_args(args.split(' '))
        parse.check_logic(args)

        try:
            args = '--config /tmp/.xnat.cfg -e BBRC_E000 --nobg -o /tmp/toto.gif'
            args = parser.parse_args(args.split(' '))
            parse.check_logic(args)
        except Exception as e:
            print(e)
            pass

        args = '--config /tmp/.xnat.cfg -e BBRC_E000 -o /tmp/toto.gif'
        args = parser.parse_args(args.split(' '))
        parse.check_logic(args)

    def test_002_snap_files(self):
        xnat.download_resources(config='.xnat.cfg', experiment_id='BBRCDEV_E02859',
            resource_name='SPM12_SEGMENT_T2T1_COREG3', destination='/tmp',
            raw=True)
        parser = parse.create_parser()
        args = '--bg /tmp/BBRCDEV_E02859_T2_T1space.nii.gz '\
           '/tmp/BBRCDEV_E02859_c1.nii.gz /tmp/BBRCDEV_E02859_c2.nii.gz '\
           '/tmp/BBRCDEV_E02859_c3.nii.gz -o /tmp/test.gif --axes A --opacity 30'
        args = parser.parse_args(args.split(' '))
        parse.run(args)

    def test_003_snap_xnat(self):
        parser = parse.create_parser()
        args = '--config .xnat.cfg '\
           '-e BBRCDEV_E02859 -o /tmp/test.gif --axes A --opacity 30'
        args = parser.parse_args(args.split(' '))
        parse.run(args)

    def test_004(self):
        raw = False
        animated = False
        savefig = None
        print('raw:', raw, 'animated:', animated, 'savefig:', savefig)
        xnat.plot_segment(config='.xnat.cfg',
            experiment_id='BBRCDEV_E02859', axes=('A'), raw=raw,
            animated=animated, savefig=savefig)

    def test_005(self):
        filepaths = xnat.download_resources(config='.xnat.cfg', experiment_id='BBRCDEV_E02859',
            resource_name='SPM12_SEGMENT_T2T1_COREG3', destination='/tmp',
            raw=True)
        for bg in [None, filepaths[0]]:
            for animated in [True, False]:
                for savefig in [None, '/tmp/toto']:
                    print('bg:', bg, 'animated:', animated, 'savefig:', savefig)
                    nisnap.plot_segment(filepaths[1:], bg=bg, axes=('A'),
                        animated=animated, savefig=savefig)
