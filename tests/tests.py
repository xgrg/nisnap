import unittest
from nisnap import parse, xnat
import nisnap


class RunThemAll(unittest.TestCase):

    def test_001_check_logic(self):
        parser = parse.create_parser()
        args = ['/home/grg/.xnat.cfg', '/home/grg/.xnat.cfg',
            '/home/grg/.xnat.cfg', '-o', '/tmp/toto.jpg']
        args = parser.parse_args(args)
        parse.check_logic(args)

        try:
            args = '/home/grg/.xnat.cfg /home/grg/.xnat.cfg /home/grg/.xnat.cfg '\
                '/home/grg/.xnat.cfg -o /tmp/toto.jpg'
            args = parser.parse_args(args.split(' '))
            parse.check_logic(args)
        except Exception as e:
            print(e)
            pass

        try:
            args = '/home/grg/.xnat.cfg /home/grg/.xnat.cfg /home/grg/.xnat.cfg '\
                '/home/grg/.xnat.cfg /home/grg/.xnat.cfg'
            args = parser.parse_args(args.split(' '))
            parse.check_logic(args)
        except Exception as e:
            print(e)
            pass

        args = '/home/grg/.xnat.cfg -o /tmp/toto.jpg'
        args = parser.parse_args(args.split(' '))
        parse.check_logic(args)

        args = '/home/grg/.xnat.cfg --bg /home/grg/.xnat.cfg -o /tmp/toto.jpg'
        args = parser.parse_args(args.split(' '))
        parse.check_logic(args)

        args = '--config /home/grg/.xnat.cfg -e BBRC_E000 -o /tmp/toto.jpg'
        args = parser.parse_args(args.split(' '))
        parse.check_logic(args)

        args = '--config /home/grg/.xnat.cfg -e BBRC_E000 --nobg -o /tmp/toto.jpg'
        args = parser.parse_args(args.split(' '))
        parse.check_logic(args)

        try:
            args = '--config /home/grg/.xnat.cfg -e BBRC_E000 --nobg -o /tmp/toto.gif'
            args = parser.parse_args(args.split(' '))
            parse.check_logic(args)
        except Exception as e:
            print(e)
            pass

        args = '--config /home/grg/.xnat.cfg -e BBRC_E000 -o /tmp/toto.gif'
        args = parser.parse_args(args.split(' '))
        parse.check_logic(args)

    def test_002_snap_files(self):
        parser = parse.create_parser()
        args = '--bg /home/grg/BBRCDEV_E02859_T2_T1space.nii.gz '\
           '/home/grg/BBRCDEV_E02859_c1.nii.gz /home/grg/BBRCDEV_E02859_c2.nii.gz '\
           '/home/grg/BBRCDEV_E02859_c3.nii.gz -o /tmp/test.gif --axes A --opacity 30'
        args = parser.parse_args(args.split(' '))
        parse.run(args)

    def test_003_snap_xnat(self):
        parser = parse.create_parser()
        args = '--config /home/grg/.xnat_goperto_ci.cfg '\
           '-e BBRCDEV_E02849 -o /tmp/test.gif --axes A --opacity 30'
        args = parser.parse_args(args.split(' '))
        parse.run(args)

    def test_004(self):
        for raw in [True, False]:
            for animated in [True, False]:
                for savefig in [None, '/tmp/toto']:
                    print('raw:', raw, 'animated:', animated, 'savefig:', savefig)
                    xnat.plot_segment(config='/home/grg/.xnat_goperto_ci.cfg',
                        experiment_id='BBRCDEV_E02859', axes=('A'), raw=raw,
                        animated=animated, savefig=savefig)

    def test_005(self):
        filepaths = ['/home/grg/BBRCDEV_E02859_T2_T1space.nii.gz',
            '/home/grg/BBRCDEV_E02859_c1.nii.gz',
            '/home/grg/BBRCDEV_E02859_c2.nii.gz',
            '/home/grg/BBRCDEV_E02859_c3.nii.gz']

        for bg in [None, filepaths[0]]:
            for animated in [True, False]:
                for savefig in [None, '/tmp/toto']:
                    print('bg:', bg, 'animated:', animated, 'savefig:', savefig)
                    nisnap.plot_segment(filepaths[1:], bg=bg, axes=('A'),
                        animated=animated, savefig=savefig)
