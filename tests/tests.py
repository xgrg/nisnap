import unittest

class RunThemAll(unittest.TestCase):

    def test_001(self):
        import sys
        sys.path.append('/home/grg/git/nisnap')
        from nisnap import nisnap
        parser = nisnap.create_parser()
        args = ['/home/grg/.xnat.cfg', '/home/grg/.xnat.cfg',
            '/home/grg/.xnat.cfg', '-o', '/tmp/toto.jpg']
        args = parser.parse_args(args)
        nisnap.check_logic(args)

        try:
            args = ['/home/grg/.xnat.cfg', '/home/grg/.xnat.cfg', '/home/grg/.xnat.cfg',
                '/home/grg/.xnat.cfg', '-o', '/tmp/toto.jpg']
            args = parser.parse_args(args)
            nisnap.check_logic(args)
        except Exception as e:
            print(e)
            pass

        try:
            args = ['/home/grg/.xnat.cfg', '/home/grg/.xnat.cfg', '/home/grg/.xnat.cfg',
                '/home/grg/.xnat.cfg', '-o', '/tmp/toto.jpg']
            args = parser.parse_args(args)
            nisnap.check_logic(args)
        except Exception as e:
            print(e)
            pass

        args = ['/home/grg/.xnat.cfg', '-o', '/tmp/toto.jpg']
        args = parser.parse_args(args)
        nisnap.check_logic(args)

        args = ['/home/grg/.xnat.cfg', '--bg', '/home/grg/.xnat.cfg', '-o', '/tmp/toto.jpg']
        args = parser.parse_args(args)
        nisnap.check_logic(args)

        args = ['--config', '/home/grg/.xnat.cfg', '-e', 'BBRC_E000',
            '-o', '/tmp/toto.jpg']
        args = parser.parse_args(args)
        nisnap.check_logic(args)

        args = ['--config', '/home/grg/.xnat.cfg', '-e', 'BBRC_E000', '--nobg',
            '-o', '/tmp/toto.jpg']
        args = parser.parse_args(args)
        nisnap.check_logic(args)

        try:
            args = ['--config', '/home/grg/.xnat.cfg', '-e', 'BBRC_E000', '--nobg',
                '-o', '/tmp/toto.gif']
            args = parser.parse_args(args)
            nisnap.check_logic(args)
        except Exception as e:
            print(e)
            pass

        args = ['--config', '/home/grg/.xnat.cfg', '-e', 'BBRC_E000',
            '-o', '/tmp/toto.gif']
        args = parser.parse_args(args)
        nisnap.check_logic(args)
