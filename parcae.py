#!/usr/bin/env python3

import sys

def up(args):
    import configparser

    config = configparser.ConfigParser()
    try:
        config.read(args.config)
    except:
        print('Could not parse configuration file "%s"' % args.config)
        raise
    if config.sections() == []:
        print('Did not find any section in configuration file "%s"'
                % args.config)
        sys.exit(1)




if __name__ == '__main__':
    import argparse

    # Top level parser
    parser = argparse.ArgumentParser(prog='parcae')
    subparsers = parser.add_subparsers(title='subcommands',
            help='additional help')

    # Parser for the "up" command
    parser_up = subparsers.add_parser('up',
            help='provision and start the cluster')
    parser_up.add_argument('-c', '--config',
            help='specify a config file to use',
            default='parcae.ini',
            dest='config')
    parser_up.set_defaults(func=up)

    # Parse argument and execute command
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        print('No action specified')
        print(parser.format_usage(), end='')

