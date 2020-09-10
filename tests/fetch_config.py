#!/usr/bin/env python

import json
import logging as log
import os.path as op


def create_parser():
    import argparse

    arg_parser = argparse.ArgumentParser(description='Retrieve login info and '
                                                     'store it in a temp file')
    arg_parser.add_argument('xnat_host')
    arg_parser.add_argument('--xnat_user')
    arg_parser.add_argument('--xnat_password')
    arg_parser.add_argument('--xnat_jsessionid')
    arg_parser.add_argument('--unverified_ssl_context',
                            action='store_true', default=False)

    return arg_parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    log.basicConfig(level=log.INFO)

    config_file = '.xnat.cfg'
    j = {'server': args.xnat_host.rstrip('/'),
         'verify': bool(not args.unverified_ssl_context)}
    if args.xnat_password is not None and args.xnat_user is not None:
        j.update({'user': args.xnat_user,
                  'password': args.xnat_password})
        log.info('Mode USER/PASSWORD')
    elif args.xnat_jsessionid is not None:
        j['jsession_id'] = args.xnat_jsessionid
        log.info('Mode JSESSIONID')
    else:
        raise Exception('Missing arguments (JSESSIONID or USER/PASSWORD)')

    json.dump(j, open(op.abspath(config_file), 'w'), indent=2)
    log.info('Saved in {}'.format(op.abspath(config_file)))
