import unittest
from nisnap.utils import parse
from nisnap import xnat
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
                '/tmp/.xnat.cfg /tmp/.xnat.cfg -o /tmp/toto.jpg'
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

        try:
            args = '--config /tmp/.xnat.cfg -e BBRC_E000 --nobg --opacity 10 -o /tmp/toto.jpg'
            args = parser.parse_args(args.split(' '))
            parse.check_logic(args)
        except Exception as e:
            print(e)
            pass

        try:
            args = '/tmp/.xnat.cfg /tmp/.xnat.cfg /tmp/.xnat.cfg '\
                '--opacity 10 -o /tmp/toto.jpg'
            args = parser.parse_args(args.split(' '))
            parse.check_logic(args)
        except Exception as e:
            print(e)
            pass


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
           '/tmp/BBRCDEV_E02859_SPM12_SEGMENT_T2T1_COREG3_c1.nii.gz /tmp/BBRCDEV_E02859_SPM12_SEGMENT_T2T1_COREG3_c2.nii.gz '\
           '/tmp/BBRCDEV_E02859_SPM12_SEGMENT_T2T1_COREG3_c3.nii.gz -o /tmp/test.png --axes x --opacity 30'
        args = parser.parse_args(args.split(' '))
        parse.run(args)

    def test_003_snap_xnat(self):
        parser = parse.create_parser()
        args = '--config .xnat.cfg '\
           '-e BBRCDEV_E02859 -o /tmp/test.png --axes x --opacity 30'
        args = parser.parse_args(args.split(' '))
        parse.run(args)

    def test_004(self):
        xnat.plot_segment(config='.xnat.cfg',
            experiment_id='BBRCDEV_E02859', axes='x', raw=False,
            animated=False, savefig=None)

    def test_005(self):
        filepaths = xnat.download_resources(config='.xnat.cfg',
            experiment_id='BBRCDEV_E02859',
            resource_name='SPM12_SEGMENT_T2T1_COREG3', destination='/tmp',
            raw=True)
        nisnap.plot_segment(filepaths[1:], bg=None, axes='x',
            slices=range(100, 110, 2),
            animated=False, savefig='/tmp/toto')
        nisnap.plot_segment(filepaths[1:], bg=None, axes='x',
            slices={'x':range(100, 110, 2)},
            animated=False, savefig='/tmp/toto')
        for bg in [None, filepaths[0]]:
            for animated in [True, False]:
                for savefig in [None, '/tmp/toto']:
                    print('bg:', bg, 'animated:', animated, 'savefig:', savefig)
                    nisnap.plot_segment(filepaths[1:], bg=bg, axes='x',
                        slices=range(100,110,2),
                        animated=animated, savefig=savefig)

    def test_xnat_spm12_006(self):
        from nisnap import xnat
        xnat.plot_segment(config='.xnat.cfg',
            experiment_id='BBRCDEV_E02859',
            resource_name='SPM12_SEGMENT_T2T1_COREG3',
            axes='x', opacity=100, slices=range(160,180,3), rowsize={'x':9},
            animated=False, contours=True, cache=True)

    def test_007_ashs(self):
        figsize = {'x':(10,3)}
        from nisnap import xnat
        xnat.plot_segment(config='.xnat.cfg',
            experiment_id='BBRCDEV_E02443',
            resource_name='ASHS', figsize=figsize,
            axes='x', opacity=50, slices=range(8,27,1), rowsize=5,
            animated=True, raw=False, contours=False, cache=False)

    def test_xnat_cat12_008(self):
        from nisnap import xnat
        xnat.plot_segment(config='.xnat.cfg',
            experiment_id='BBRCDEV_E00375',
            resource_name='CAT12_SEGMENT', figsize=(10,3),
            axes='x', opacity=50, slices=range(160,180,3), rowsize=9,
            animated=False, contours=False, cache=False,
            samebox=True)

    def test_xnat_freesurfer_009(self):
        from nisnap import xnat
        from nisnap.utils import aseg
        filepaths = xnat.download_resources(config='.xnat.cfg',
                experiment_id='BBRCDEV_E00559',
                resource_name='FREESURFER6', destination='/tmp/')        

        aseg_fp = filepaths[-1]
        aseg.__picklabel_fs__(aseg_fp, labels=[9,10,11,12,13,17,48,49,50,51,52,53])
        aseg.__swap_fs__(aseg_fp)
        try:
            aseg.__preproc_aseg__(aseg_fp, filepaths[1])
        except Exception as exc:
            pass
