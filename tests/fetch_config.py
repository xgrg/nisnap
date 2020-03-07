#!/usr/bin/env python2
import argparse
import json
import logging as log
import os.path as op

if __name__ == '__main__':
    config_file = '.xnat.cfg'
    parser = argparse.ArgumentParser(description='Retrieve login info and '\
                                                 'store it in a temp file')
    parser.add_argument("xnat_host")
    parser.add_argument("--xnat_user")
    parser.add_argument("--xnat_password")
    parser.add_argument("--xnat_jsessionid")
    parser.add_argument('--unverified_ssl_context',
                        action='store_true',
                        default=False)

    args = parser.parse_args()
    log.basicConfig(level=log.INFO)
    j = {"server": args.xnat_host.rstrip('/'),
         "verify": bool(not args.unverified_ssl_context)}
    if args.xnat_password is not None and args.xnat_user is not None:
        j.update( { 'user'    : args.xnat_user,
                    'password': args.xnat_password })
        log.info('Mode USER/PASSWORD')
    elif args.xnat_jsessionid is not None:
        j['jsession_id'] = args.xnat_jsessionid
        log.info('Mode JSESSIONID')
    else:
        raise Exception('Missing arguments (JSESSIONID or USER/PASSWORD)')
    json.dump(j, open(op.abspath(config_file), 'w'), indent=2)
    log.info('Saved in %s'%op.abspath(config_file))
